"""Real same-key Android update from checked main development APK to RC APK."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_apk import verify
from sedrava_version import VERSION, ANDROID_VERSION_CODE
from sedrava_android_identity import project_identity

BASELINE='2ff3994dd503d453c2fc81c133cc1c95a9c3d3b1'

def run(*args):
    return subprocess.check_output(list(map(str,args)),text=True)

def snapshot(raw):
    root=ET.fromstring(raw)
    return json.loads(next(n.text for n in root if n.get('name')=='snapshot'))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--baseline-project',default='build/navigation-baseline')
    parser.add_argument('--baseline-source',default='build/rc-baseline-src')
    parser.add_argument('--baseline-sha',default=BASELINE)
    parser.add_argument('--baseline-version',default='0.10.0.dev0')
    parser.add_argument('--baseline-code',type=int,default=1)
    parser.add_argument('--evidence-prefix',default='build/rc-upgrade')
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
    assert old['version_code']==args.baseline_code and new['version_code']==ANDROID_VERSION_CODE>=args.baseline_code
    assert old['signer_certificate_sha256']==new['signer_certificate_sha256']
    subprocess.run(['gradle','-p',str(ROOT/args.baseline_project),'--no-daemon','-Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true',':app:connectedDebugAndroidTest'],check=True)
    before=run('adb','shell','run-as',package,'cat','shared_prefs/sedrava_state.xml')
    expected={'next_id':2,'items':[{'id':1,'title':'Upgrade kept','done':False}]}
    assert snapshot(before)['state']['tasks']==expected
    run('adb','shell','am','force-stop',package)
    install=run('adb','install','-r',after_apk)
    assert 'Success' in install
    after=run('adb','shell','run-as',package,'cat','shared_prefs/sedrava_state.xml')
    assert snapshot(after)==snapshot(before)
    package_dump=run('adb','shell','dumpsys','package',package)
    assert 'versionName='+VERSION in package_dump and 'versionCode='+str(ANDROID_VERSION_CODE) in package_dump
    run('adb','shell','am','start','-W','-n',package+'/.MainActivity')
    found=False
    for attempt in range(8):
        run('adb','shell','uiautomator','dump','/sdcard/rc-upgrade.xml')
        ui=run('adb','shell','cat','/sdcard/rc-upgrade.xml')
        if 'Open Upgrade kept' in ui or 'text="Upgrade kept"' in ui:
            found=True;break
        run('adb','shell','input','swipe','500','750','500','250','200')
    assert found,'Updated app did not render accepted baseline task'
    prefix=ROOT/args.evidence_prefix
    Path(str(prefix)+'-before.xml').write_text(before)
    Path(str(prefix)+'-after.xml').write_text(after)
    Path(str(prefix)+'-ui.xml').write_text(ui)
    with Path(str(prefix)+'.png').open('wb') as handle:subprocess.run(['adb','exec-out','screencap','-p'],stdout=handle,check=True)
    assert properties['ro.build.version.sdk']=='35' and properties['ro.kernel.qemu']=='1'
    Path(str(prefix)+'.json').write_text(json.dumps({'baseline_sha':args.baseline_sha,'baseline_apk':old,'rc_apk':new,'preserved_tasks':expected,'emulator':properties,'result':'PASS'},sort_keys=True,indent=2)+'\n')
    # Reset only this disposable emulator app for the independent existing lifecycle scenario.
    assert 'Success' in run('adb','shell','pm','clear',package)
    print('PASS: real '+args.baseline_version+' code '+str(args.baseline_code)+' -> audit code '+str(ANDROID_VERSION_CODE)+' update; UI-created data and stable ID retained')
