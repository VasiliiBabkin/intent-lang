"""Real same-key APK update, including rejected-data protection on API35."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_apk import verify
from sedrava_version import VERSION, ANDROID_VERSION_CODE
from sedrava_android_identity import project_identity

BASELINE='2ff3994dd503d453c2fc81c133cc1c95a9c3d3b1'

def run(*args):
    return subprocess.check_output(list(map(str,args)),text=True)

def raw_snapshot(raw):
    return next(n.text for n in ET.fromstring(raw) if n.get('name')=='snapshot')

def snapshot(raw):
    return json.loads(raw_snapshot(raw))

def validate_update(old,new):
    if (old['application_id']!=new['application_id'] or
            old['signer_certificate_sha256']!=new['signer_certificate_sha256'] or
            new['version_code']<=old['version_code']):
        raise ValueError('Update requires the same ID/key and strictly increasing versionCode')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--baseline-project',default='build/navigation-baseline')
    parser.add_argument('--baseline-source',default='build/rc-baseline-src')
    parser.add_argument('--baseline-sha',default=BASELINE)
    parser.add_argument('--baseline-version',default='0.10.0.dev0')
    parser.add_argument('--baseline-code',type=int,default=1)
    parser.add_argument('--evidence-prefix',default='build/rc-upgrade')
    parser.add_argument('--verify-rejected-updates',action='store_true')
    args=parser.parse_args()
    sdk=Path(os.environ['ANDROID_HOME'])
    properties={key:run('adb','shell','getprop',key).strip() for key in ('ro.build.version.sdk','ro.build.version.release','ro.product.model','ro.product.cpu.abi','ro.kernel.qemu')}
    if properties['ro.build.version.sdk']!='35' or properties['ro.kernel.qemu']!='1':
        raise SystemExit('Requires disposable API 35 emulator; no app was changed')
    before_apk=ROOT/args.baseline_project/'app/build/outputs/apk/debug/app-debug.apk'
    after_apk=ROOT/'build/navigation-android/app/build/outputs/apk/debug/app-debug.apk'
    package=project_identity(ROOT/'build/navigation-android')
    assert project_identity(ROOT/args.baseline_project)==package
    assert run('git','-C',ROOT/args.baseline_source,'rev-parse','HEAD').strip()==args.baseline_sha
    old=verify(before_apk,sdk,package,args.baseline_version)
    new=verify(after_apk,sdk,package,VERSION)
    assert old['version_code']==args.baseline_code and new['version_code']==ANDROID_VERSION_CODE
    validate_update(old,new)
    relative='shared_prefs/sedrava_state.xml'
    prefix=ROOT/args.evidence_prefix

    def provision_baseline():
        # Between independent fixture scenarios only. NEVER uninstall/clear
        # between the UI seed/corruption and the real install -r transition.
        if 'package:'+package in run('adb','shell','pm','list','packages',package).splitlines():
            assert 'Success' in run('adb','uninstall',package)
        subprocess.run(['gradle','-p',str(ROOT/args.baseline_project),'--no-daemon','-Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true',':app:connectedDebugAndroidTest'],check=True)

    def read_preferences():
        return run('adb','shell','run-as',package,'cat',relative)

    def install_update():
        run('adb','shell','am','force-stop',package)
        assert 'Success' in run('adb','install','-r',after_apk)
        dump=run('adb','shell','dumpsys','package',package)
        assert 'versionName='+VERSION in dump and 'versionCode='+str(ANDROID_VERSION_CODE) in dump
        run('adb','shell','am','start','-W','-n',package+'/.MainActivity')

    def find_ui(needle):
        for _ in range(8):
            run('adb','shell','uiautomator','dump','/sdcard/rc-upgrade.xml')
            ui=run('adb','shell','cat','/sdcard/rc-upgrade.xml')
            if needle in ui:return ui
            run('adb','shell','input','swipe','500','750','500','250','200')
        raise AssertionError('Updated app UI did not contain '+needle)

    provision_baseline()
    before=read_preferences()
    expected={'next_id':2,'items':[{'id':1,'title':'Upgrade kept','done':False}]}
    assert snapshot(before)['state']['tasks']==expected
    install_update()
    ui=find_ui('Upgrade kept')
    after=read_preferences()
    assert snapshot(after)==snapshot(before)
    run('adb','shell','am','force-stop',package)
    run('adb','shell','am','start','-W','-n',package+'/.MainActivity')
    find_ui('Upgrade kept')
    assert snapshot(read_preferences())==snapshot(before)
    Path(str(prefix)+'-before.xml').write_text(before)
    Path(str(prefix)+'-after.xml').write_text(after)
    Path(str(prefix)+'-ui.xml').write_text(ui)
    with Path(str(prefix)+'.png').open('wb') as handle:
        subprocess.run(['adb','exec-out','screencap','-p'],stdout=handle,check=True)
    rejected=[]
    if args.verify_rejected_updates:
        for kind in ('malformed','incompatible'):
            provision_baseline()
            original=read_preferences();tree=ET.fromstring(original)
            bad='{broken' if kind=='malformed' else json.dumps({**snapshot(original),'schema':2},ensure_ascii=False)
            next(n for n in tree if n.get('name')=='snapshot').text=bad
            run('adb','shell','am','force-stop',package)
            subprocess.run(['adb','shell','-T','run-as',package,'tee',relative],input=ET.tostring(tree,encoding='utf-8'),stdout=subprocess.DEVNULL,check=True)
            install_update()
            bad_ui=find_ui('original retained')
            assert raw_snapshot(read_preferences())==bad
            run('adb','shell','am','force-stop',package)
            run('adb','shell','am','start','-W','-n',package+'/.MainActivity')
            find_ui('original retained')
            assert raw_snapshot(read_preferences())==bad
            Path(str(prefix)+'-'+kind+'-ui.xml').write_text(bad_ui)
            rejected.append({'kind':kind,'install_method':'adb install -r','rejection_visible':True,'cold_restart_retained':True,'original_sha256':hashlib.sha256(bad.encode()).hexdigest()})
    Path(str(prefix)+'.json').write_text(json.dumps({'baseline_sha':args.baseline_sha,'baseline_apk':old,'rc_apk':new,'preserved_tasks':expected,'emulator':properties,'install_method':'adb install -r','cold_restart_preserved':True,'rejected_updates':rejected,'result':'PASS'},sort_keys=True,indent=2)+'\n')
    # Only after all update assertions, isolate the following lifecycle scenario.
    assert 'Success' in run('adb','shell','pm','clear',package)
    print('PASS: real '+args.baseline_version+' code '+str(args.baseline_code)+' -> '+VERSION+' code '+str(ANDROID_VERSION_CODE)+' update; valid and rejected data retained')
