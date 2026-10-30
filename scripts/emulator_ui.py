"""Handle only the API35 emulator launcher's known system ANR, never app ANRs."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]

def launcher_close_point(raw):
    nodes=list(ET.fromstring(raw).iter('node'))
    alerts=[n for n in nodes if "isn't responding" in n.get('text','') or 'isn’t responding' in n.get('text','')]
    if not alerts:return None
    if not all(n.get('package')=='android' and n.get('text') in ("Quickstep isn't responding",'Quickstep isn’t responding') for n in alerts):
        raise ValueError('Application/unknown ANR must fail the test; not dismissed')
    close=[n for n in nodes if n.get('package')=='android' and n.get('text')=='Close app']
    if len(close)!=1:raise ValueError('Ambiguous launcher dialog; no tap performed')
    match=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',close[0].get('bounds',''))
    if not match:raise ValueError('Invalid launcher close bounds')
    x1,y1,x2,y2=map(int,match.groups())
    if not (x1<x2 and y1<y2):raise ValueError('Invalid launcher close bounds')
    return ((x1+x2)//2,(y1+y2)//2)


def handle_launcher_dialog(raw,package):
    # Read-only device guard before any UI intervention.
    def run(*args):return subprocess.check_output(list(args),text=True)
    point=launcher_close_point(raw)
    if point is None:return False
    if run('adb','shell','getprop','ro.kernel.qemu').strip()!='1' or run('adb','shell','getprop','ro.build.version.sdk').strip()!='35':
        raise ValueError('Launcher intervention requires disposable API35 emulator')
    if not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+',package):raise ValueError('Invalid package')
    output=ROOT/'build/emulator-system-dialogs';output.mkdir(parents=True,exist_ok=True)
    index=len(list(output.glob('*.json')))
    if index>=2:raise ValueError('Repeated launcher ANRs; emulator not healthy')
    prefix=output/str(index)
    prefix.with_suffix('.xml').write_text(raw,encoding='utf-8')
    with prefix.with_suffix('.png').open('wb') as f:subprocess.run(['adb','exec-out','screencap','-p'],stdout=f,check=True)
    run('adb','shell','input','tap',str(point[0]),str(point[1]))
    run('adb','shell','am','start','-W','-n',package+'/.MainActivity')
    prefix.with_suffix('.json').write_text(json.dumps({'system_dialog':"Quickstep isn't responding",'action':'close launcher only; foreground existing tested Activity','application_id':package,'no_app_data_reset':True},indent=2)+'\n')
    print('Observed/dismissed Quickstep system ANR; no app action replay or state mutation')
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('xml',type=Path);p.add_argument('package');a=p.parse_args()
    handle_launcher_dialog(a.xml.read_text(encoding='utf-8'),a.package)
