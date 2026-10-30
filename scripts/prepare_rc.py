"""Assemble immutable, same-SHA tested RC inputs. Read-only API; no publication."""
import argparse
import csv
import datetime
import email
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sedrava_version import VERSION, ANDROID_VERSION_CODE
from sedrava_android_identity import application_id
from sedrava_core import parse
from web_codegen import generate
from scripts.rc_api import GitHub
from scripts.rc_archive import sha256, read_zip, read_sdist, deterministic_zip, safe_name
from scripts.check_rc_availability import check as check_availability

GATES=('alpha.yml','ci.yml','android.yml','navigation-010.yml','records-language-010.yml','text-010.yml','reference-09-android.yml','sedrava07-pypi.yml')
LIMITS=['Experimental RC, not a stable release','No physical-device validation for these APKs','Debug APKs, not production signing; different machines may use different keys','No data/schema migrations or encrypted storage','No Gradle wrapper, transitive lockfiles or byte-identical APK guarantee','Same-title default Android identities intentionally coincide; explicit ID separates apps','TestPyPI not checked and not a publication target; recheck any target before authorized publication']


def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode('utf-8')


def validate_run(run,sha,repo):
    if run.get('head_sha')!=sha or run.get('head_repository',{}).get('full_name')!=repo or run.get('status')!='completed' or run.get('conclusion')!='success':
        raise ValueError('Run is not successful for the exact source SHA/repository')
    return run


def wait_gates(api,sha,timeout):
    deadline=time.monotonic()+timeout
    while True:
        runs=[r for r in api.pages('/actions/runs?head_sha='+sha,'workflow_runs')
              if r.get('event') in ('pull_request','push','workflow_dispatch') and r.get('path')!='.github/workflows/rc-prepare.yml']
        pending=[r for r in runs if r['status']!='completed']
        for run in runs:
            if run['status']=='completed':validate_run(run,sha,api.repo)
        chosen={}
        for gate in GATES:
            candidates=[r for r in runs if r.get('path')=='.github/workflows/'+gate]
            candidates.sort(key=lambda r:(r.get('event')=='pull_request',r['id']),reverse=True)
            if candidates and candidates[0]['status']=='completed':chosen[gate]=candidates[0]
        if len(chosen)==len(GATES) and not pending:
            selected={run['id'] for run in chosen.values()}
            for run in runs:
                if run['id'] not in selected:
                    chosen[run['path'].rsplit('/',1)[-1]+':'+run['event']+':'+str(run['id'])]=run
            return chosen
        if time.monotonic()>deadline:raise TimeoutError('Timed out waiting for same-SHA release gates')
        print('Waiting for all applicable same-SHA gates; completed required '+str(len(chosen))+'/'+str(len(GATES))+', running '+str(len(pending)),flush=True)
        time.sleep(20)


def artifact(api,run,name,sha):
    entries=api.pages('/actions/runs/'+str(run['id'])+'/artifacts','artifacts')
    found=[a for a in entries if a['name']==name]
    if len(found)!=1:raise ValueError('Expected exactly one immutable artifact: '+name)
    meta=found[0]
    if meta.get('expired') or meta.get('workflow_run',{}).get('head_sha')!=sha or not re.fullmatch(r'sha256:[0-9a-f]{64}',meta.get('digest','')):
        raise ValueError('Artifact provenance/digest missing or mismatched')
    raw=api.get('/actions/artifacts/'+str(meta['id'])+'/zip',binary=True)
    if sha256(raw)!=meta['digest'].split(':',1)[1]:raise ValueError('Artifact ZIP digest mismatch')
    info={'id':meta['id'],'name':name,'sha256':sha256(raw),'run_id':run['id'],
          'url':'https://github.com/'+api.repo+'/actions/runs/'+str(run['id'])+'/artifacts/'+str(meta['id'])}
    return read_zip(raw),info,raw


def check_distributions(files):
    wheels=[n for n in files if n.endswith('.whl')];sdists=[n for n in files if n.endswith('.tar.gz')]
    if wheels!=['sedrava-'+VERSION+'-py3-none-any.whl'] or sdists!=['sedrava-'+VERSION+'.tar.gz']:
        raise ValueError('Unexpected distribution names/count/version')
    wheel=read_zip(files[wheels[0]]);sdist=read_sdist(files[sdists[0]])
    metadata_names=[n for n in wheel if n.endswith('.dist-info/METADATA')]
    source_metadata=[n for n in sdist if n=='sedrava-'+VERSION+'/PKG-INFO']
    if len(metadata_names)!=1 or len(source_metadata)!=1:raise ValueError('Missing package metadata')
    for raw in [wheel[metadata_names[0]],sdist[source_metadata[0]]]:
        meta=email.message_from_bytes(raw)
        if meta.get('Name')!='sedrava' or meta.get('Version')!=VERSION or meta.get('License-Expression')!='Apache-2.0':raise ValueError('Distribution metadata disagrees')
    # Source files in the checked archives must be the files from this exact checkout.
    for name,data in wheel.items():
        if name.endswith('.py'):
            source=ROOT/name
            if '/' in name or not source.is_file() or source.read_bytes()!=data:raise ValueError('Wheel code differs from checked source')
        if name.endswith('.pth') or name.endswith(('.so','.dll','.exe')):raise ValueError('Unexpected executable wheel payload')
    for name,data in sdist.items():
        relative=name.partition('/')[2]
        if name.partition('/')[0]!='sedrava-'+VERSION:raise ValueError('Unexpected sdist root')
        source=ROOT/relative
        if source.is_file() and '.egg-info/' not in relative and source.read_bytes()!=data:raise ValueError('Source archive differs from checkout: '+relative)
        if relative.endswith('.py') and not source.is_file():raise ValueError('Unexpected source archive code')
    if wheel.get('sedrava_version.py')!=(ROOT/'sedrava_version.py').read_bytes():raise ValueError('Version module missing/mismatched')
    records=[n for n in wheel if n.endswith('.dist-info/RECORD')]
    if len(records)!=1:raise ValueError('Missing wheel RECORD')
    import base64
    rows=list(csv.reader(io.StringIO(wheel[records[0]].decode())))
    if {r[0] for r in rows}!=set(wheel) or len(rows)!=len(wheel):raise ValueError('Invalid wheel RECORD inventory')
    for name,digest,size in rows:
        if name==records[0]:
            if digest or size:raise ValueError('Invalid RECORD self entry')
        elif digest!='sha256='+base64.urlsafe_b64encode(bytes.fromhex(sha256(wheel[name]))).decode().rstrip('=') or size!=str(len(wheel[name])):
            raise ValueError('Wheel RECORD checksum mismatch')
    return {name:files[name] for name in wheels+sdists}


def test_evidence(api,runs,nav):
    summary={'python':{},'chromium':None,'jvm_navigation':[],'emulator':[],'physical_device':'unavailable; not tested'}
    ci=[]
    for gate,run in runs.items():
        jobs=api.pages('/actions/runs/'+str(run['id'])+'/jobs','jobs')
        if not jobs or any(j['status']!='completed' or j['conclusion']!='success' for j in jobs):raise ValueError('Prerequisite job not successful')
        ci.append({'workflow':run['path'],'event':run['event'],'run_id':run['id'],'source_sha':run['head_sha'],'url':run['html_url'],'conclusion':run['conclusion'],'attempt':run.get('run_attempt',1),
                   'jobs':[{'id':j['id'],'name':j['name'],'conclusion':j['conclusion']} for j in jobs]})
        if gate=='alpha.yml':
            for job in jobs:
                text=api.job_log(job['id'])
                counts=re.findall(r'Ran ([0-9]+) tests? in ',text)
                if len(counts)!=1:raise ValueError('Missing/ambiguous actual test count in '+job['name'])
                count=int(counts[0])
                if job['name']=='chromium':summary['chromium']=count
                elif m:=re.fullmatch(r'language-package \((3\.(?:10|12|13))\)',job['name']):summary['python'][m[1]]=count
                else:raise ValueError('Unrecognized alpha test job')
    if set(summary['python'])!={'3.10','3.12','3.13'} or min(summary['python'].values())<141 or (summary['chromium'] or 0)<23:raise ValueError('Regression coverage missing')
    unit={};device={}
    for name,data in nav.items():
        target=unit if '/test-results/testDebugUnitTest/' in name else device if '/outputs/androidTest-results/' in name else None
        if target is None or not name.endswith('.xml'):continue
        if b'<!DOCTYPE' in data or b'<!ENTITY' in data:raise ValueError('Unexpected XML DTD')
        root=ET.fromstring(data)
        for case in root.iter('testcase'):
            if any(case.find(tag) is not None for tag in ('failure','error','skipped')):raise ValueError('Native test did not pass')
            key=(case.get('classname'),case.get('name'))
            target[key]={'class':key[0],'name':key[1]}
    summary['jvm_navigation']=list(unit.values());summary['emulator']=list(device.values())
    if len(unit)<7 or len(device)<4:raise ValueError('Native JVM/emulator test evidence incomplete')
    upgrade=json.loads(nav['rc-upgrade.json'])
    if upgrade.get('result')!='PASS' or upgrade.get('rc_apk',{}).get('version_name')!=VERSION or upgrade.get('rc_apk',{}).get('version_code')!=ANDROID_VERSION_CODE or upgrade.get('baseline_apk',{}).get('version_code')!=1:
        raise ValueError('Real APK upgrade evidence missing')
    if upgrade['baseline_apk']['signer_certificate_sha256']!=upgrade['rc_apk']['signer_certificate_sha256']:raise ValueError('Update signing identity differs')
    summary['upgrade']=upgrade
    return summary,ci


def write_bundle(output,payload,manifest):
    if output.exists():raise ValueError('Use a fresh bundle output directory')
    output.mkdir(parents=True)
    manifest['files']=[{'path':name,'size':len(data),'sha256':sha256(data)} for name,data in sorted(payload.items())]
    manifest['checksum_scope']='files lists payload; SHA256SUMS also hashes manifest.json and manifest.md; external immutable Actions ZIP digest binds SHA256SUMS itself'
    payload=dict(payload);payload['manifest.json']=encode(manifest)
    lines=['# Sedrava '+VERSION+' experimental RC manifest','', 'Source SHA: `'+manifest['git_sha']+'`','',
           'Technical status: **GO_FOR_OWNER_REVIEW**. Publication authorized: **false**.','',
           'Build: '+manifest['build']['url'],'','## Verified files','', '| File | SHA-256 |','| --- | --- |']
    lines.extend('| '+n+' | `'+sha256(d)+'` |' for n,d in sorted(payload.items()) if n!='manifest.json')
    lines+=['','## CI','']+[x['url'] for x in manifest['ci']]+['','## Limits','']+['- '+x for x in LIMITS]
    lines+=['','Hashes are integrity checks, not a production signing key. Verify immutable Actions artifact digest externally. See manifest.json and SHA256SUMS.']
    payload['manifest.md']=('\n'.join(lines)+'\n').encode()
    for name,data in payload.items():
        safe_name(name)
        if '/' in name:raise ValueError('Bundle payload must be flat')
        (output/name).write_bytes(data)
    (output/'SHA256SUMS').write_text(''.join(sha256(data)+'  '+name+'\n' for name,data in sorted(payload.items())))
    verify_bundle(output)
    return manifest


def verify_bundle(output):
    output=Path(output)
    sums={}
    for line in (output/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        if not re.fullmatch(r'[0-9a-f]{64}',digest) or '/' in safe_name(name) or name in sums:raise ValueError('Invalid checksum inventory')
        sums[name]=digest
    actual={p.name for p in output.iterdir()}
    if actual != set(sums)|{'SHA256SUMS'}:raise ValueError('Unexpected/missing bundle file')
    for name,digest in sums.items():
        file=output/name
        if file.is_symlink() or not file.is_file() or sha256(file.read_bytes())!=digest:raise ValueError('Bundle checksum mismatch: '+name)
    manifest=json.loads((output/'manifest.json').read_text())
    expected={f['path'] for f in manifest['files']}|{'manifest.json','manifest.md'}
    if set(sums)!=expected or len(manifest['files'])+2!=len(sums):raise ValueError('Manifest inventory mismatch')
    if manifest['version']!=VERSION or not re.fullmatch(r'[0-9a-f]{40}',manifest['git_sha']) or manifest['publication_authorized'] is not False or manifest['status']!='GO_FOR_OWNER_REVIEW':raise ValueError('Invalid RC manifest identity/status')
    for item in manifest['files']:
        if sums[item['path']]!=item['sha256'] or (output/item['path']).stat().st_size!=item['size']:raise ValueError('Manifest checksum mismatch')
    print('PASS: every candidate payload, both manifests and exact file inventory verified')
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sha',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--timeout',type=int,default=1800);args=p.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}',args.sha):raise ValueError('Full source SHA required')
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=args.sha or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Checkout must be clean and match exact source SHA')
    api=GitHub('VasiliiBabkin/sedrava');runs=wait_gates(api,args.sha,args.timeout)
    availability=check_availability(api)
    dist,dist_info,_=artifact(api,runs['alpha.yml'],'sedrava-alpha-distributions',args.sha)
    nav,nav_info,_=artifact(api,runs['navigation-010.yml'],'sedrava-navigation-apk-web-evidence',args.sha)
    web,web_info,_=artifact(api,runs['alpha.yml'],'sedrava-web-examples',args.sha)
    traces,trace_info,trace_raw=artifact(api,runs['alpha.yml'],'sedrava-browser-traces',args.sha)
    summary,ci=test_evidence(api,runs,nav)
    for source in sorted((ROOT/'examples').glob('*.sdr')):
        text=source.read_text(encoding='utf-8');program=parse(text)
        if program.widgets and web.get(source.stem+'.html')!=generate(text).encode():raise ValueError('Tested Web bytes differ from checked source')
    payload=check_distributions(dist)
    payload['web-examples.zip']=deterministic_zip(web)
    payload['chromium-traces.zip']=trace_raw
    native_files={name:data for name,data in nav.items() if name.endswith(('.xml','.png','.txt','.json','.html'))}
    payload['native-test-evidence.zip']=deterministic_zip(native_files)
    rollback=json.loads(dist['UPGRADE_ROLLBACK.json'])
    if rollback.get('result')!='PASS' or rollback.get('rc_version')!=VERSION:raise ValueError('Upgrade/rollback evidence missing')
    summary['python_upgrade_rollback']=rollback
    payload['checks.json']=encode(summary);payload['availability.json']=encode(availability)
    payload['toolchains.json']=encode({'python_build':json.loads(dist['BUILD_TOOLS.json']),'android_build':json.loads(nav['rc-android-tools.json']),
                                      'direct_python_requirements':(ROOT/'requirements-rc.txt').read_text(), 'action_pins':json.loads((ROOT/'.github/action-pins.json').read_text())})
    import tempfile
    apk_results=[]
    with tempfile.TemporaryDirectory(prefix='sedrava APK audit ') as folder:
        for stem,directory in [('task_manager_navigation','navigation-android'),('task_manager','tasks-android')]:
            name=stem+'-'+VERSION+'-debug.apk';data=nav[directory+'/app/build/outputs/apk/debug/app-debug.apk'];path=Path(folder)/name;path.write_bytes(data)
            expected=application_id(parse((ROOT/'examples'/ (stem+'.sdr')).read_text()).name)
            report=Path(folder)/(stem+'.json')
            subprocess.run([sys.executable,str(ROOT/'scripts/verify_apk.py'),str(path),'--application-id',expected,'--version',VERSION,'--json-output',str(report)],check=True)
            result=json.loads(report.read_text())
            if not result['debuggable'] or result['version_code']!=ANDROID_VERSION_CODE:raise ValueError('Expected versioned debug APK')
            apk_results.append(result);payload[name]=data
    run_id=os.environ['GITHUB_RUN_ID'];repo=api.repo
    if not run_id.isdigit():raise ValueError('Actual Actions build ID required')
    manifest={'schema':1,'version':VERSION,'package_name':'sedrava','git_sha':args.sha,'status':'GO_FOR_OWNER_REVIEW','publication_authorized':False,
              'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'build':{'run_id':int(run_id),'attempt':int(os.environ['GITHUB_RUN_ATTEMPT']),'url':'https://github.com/'+repo+'/actions/runs/'+run_id},
              'ci':ci,'source_artifacts':[dist_info,nav_info,web_info,trace_info],'tests':summary,'apk':apk_results,'availability':availability,
              'limits':LIMITS,'commands':['python -m build','python -m twine check dist/*','python scripts/audit_dist.py','python scripts/check_installed_dist.py','python scripts/check_upgrade_rollback.py','python scripts/test_web_browser.py','gradle -p build/navigation-android --no-daemon :app:assembleDebug :app:testDebugUnitTest :app:lintDebug :app:assembleDebugAndroidTest','python scripts/test_rc_upgrade.py','bash scripts/test_navigation_emulator.sh','bash scripts/test_records_emulator.sh','bash scripts/test_side_by_side.sh']}
    report=['# Sedrava '+VERSION+' — final CI report / Итоговый CI-отчёт','',
            'Final source SHA / Итоговый SHA: `'+args.sha+'`','',
            'Build: '+manifest['build']['url'],'',
            '**GO for controlled experimental RC owner review. Publication authorization: NOT GIVEN.**','',
            'Python tests: '+json.dumps(summary['python'],sort_keys=True),
            'Chromium scenarios: '+str(summary['chromium']),
            'Main-workflow JVM tests: '+str(len(summary['jvm_navigation'])),
            'Emulator scenarios including baseline UI seed/update: '+str(len(summary['emulator'])),
            'Real development code 1 -> RC code '+str(ANDROID_VERSION_CODE)+' same-key update: PASS',
            'Two installed apps, independent persistence, Back, rotation, Activity recreation and cold launch: PASS',
            'Published 0.9 wheel -> separate RC -> original environment: PASS',
            'Physical Android: UNAVAILABLE / НЕ ПРОВЕРЕНО','',
            '## Checked payload SHA-256','']
    report += [sha256(data)+'  '+name for name,data in sorted(payload.items())]
    report += ['','## Actual CI / Фактические CI','']+[item['url'] for item in ci]
    report += ['','## Limits and risks / Ограничения и риски','']+['- '+item for item in LIMITS]
    report += ['','No tag, release, package upload, merge or deployment was performed. Debug APKs are not production-signed releases. See the same-source docs/RC_010_REPORT.md and bilingual notes for implementation and installation details.']
    payload['RC_010_REPORT.md']=('\n'.join(report)+'\n').encode('utf-8')
    write_bundle(args.output,payload,manifest)
    print((args.output/'SHA256SUMS').read_text())
    print('SHA256SUMS SHA-256: '+sha256((args.output/'SHA256SUMS').read_bytes()))
    print('GO_FOR_OWNER_REVIEW; publication_authorized=false; nothing uploaded to any release or package index')

if __name__=='__main__':main()
