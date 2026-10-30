"""Actual cold-launch rejection without overwriting a disposable emulator's data."""
import json
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sedrava_android_identity import project_identity
from scripts.emulator_ui import handle_launcher_dialog


def run(*args):
    return subprocess.check_output(list(map(str,args)),text=True)


def verify(project):
    # Refuse physical devices before stopping or modifying any application.
    if run('adb','shell','getprop','ro.kernel.qemu').strip()!='1' or run('adb','shell','getprop','ro.build.version.sdk').strip()!='35':
        raise RuntimeError('Requires disposable API 35 emulator; no app changed')
    package=project_identity(project)
    relative='shared_prefs/sedrava_state.xml'
    run('adb','shell','am','force-stop',package)
    original=run('adb','shell','run-as',package,'cat',relative)
    root=ET.fromstring(original)
    saved=next(n.text for n in root if n.get('name')=='snapshot')
    incompatible=json.loads(saved);incompatible['schema']=2
    cases=['{broken',json.dumps(incompatible,ensure_ascii=False)]
    output=ROOT/'build/storage-rejection';output.mkdir(parents=True,exist_ok=True)
    results=[]
    def write(raw):
        subprocess.run(['adb','shell','-T','run-as',package,'tee',relative],input=raw.encode('utf-8'),stdout=subprocess.DEVNULL,check=True)
    try:
        for index,bad in enumerate(cases):
            run('adb','shell','am','force-stop',package)
            tree=ET.fromstring(original)
            next(n for n in tree if n.get('name')=='snapshot').text=bad
            write(ET.tostring(tree,encoding='unicode'))
            run('adb','shell','am','start','-W','-n',package+'/.MainActivity')
            seen_error=seen_empty=False
            for _ in range(8):
                run('adb','shell','uiautomator','dump','/sdcard/storage-rejection.xml')
                ui=run('adb','shell','cat','/sdcard/storage-rejection.xml')
                (output/(str(index)+'-ui.xml')).write_text(ui)
                if handle_launcher_dialog(ui,package):continue
                seen_error |= 'original retained' in ui
                seen_empty |= 'No tasks yet' in ui
                if seen_error and seen_empty:break
                run('adb','shell','input','swipe','500','750','500','250','200')
            assert seen_error and seen_empty,'Cold launch must report rejection and show empty defaults'
            run('adb','shell','am','force-stop',package)
            actual=ET.fromstring(run('adb','shell','run-as',package,'cat',relative))
            assert next(n.text for n in actual if n.get('name')=='snapshot')==bad
            results.append({'case':index,'cold_defaults':True,'rejection_visible':True,'original_retained':True})
        (output/'result.json').write_text(json.dumps({'result':'PASS','package':package,'cases':results},indent=2)+'\n')
    finally:
        run('adb','shell','am','force-stop',package)
        write(original)
        run('adb','shell','am','start','-W','-n',package+'/.MainActivity')
    print('PASS: actual cold-launch malformed/incompatible storage retained; original test data restored')

if __name__=='__main__':verify(sys.argv[1])
