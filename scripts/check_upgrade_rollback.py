"""Exercise actual published 0.9 wheel and local RC wheel in separate environments."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request
import venv
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sedrava_version import VERSION
from scripts.rc_api import SafeRedirect

OLD_WHEEL='sedrava-0.9.0a1-py3-none-any.whl'
OLD_SHA='b6e3a54df2355803fa1e47b5e7e849ba242bfd6437f226534db13aabc4210339'
OLD_SUMS_SHA='1c1dec588511c551c252b79ca3af08601d81ade57e2ad785cf50c44b8079cae2'
BASE='https://github.com/VasiliiBabkin/sedrava/releases/download/v0.9.0a1/'

def download(name,digest):
    opener=urllib.request.build_opener(SafeRedirect())
    with opener.open(BASE+name,timeout=60) as response:data=response.read(1_000_001)
    if len(data)>1_000_000 or hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Published baseline checksum mismatch')
    return data

def check():
    env=os.environ.copy();env.pop('PYTHONPATH',None)
    with tempfile.TemporaryDirectory(prefix='sedrava rollback ') as temp:
        root=Path(temp);wheel=root/OLD_WHEEL;wheel.write_bytes(download(OLD_WHEEL,OLD_SHA))
        sums=download('SHA256SUMS',OLD_SUMS_SHA).decode()
        if OLD_SHA+'  '+OLD_WHEEL not in sums:raise ValueError('Baseline release inventory mismatch')
        project=root/'user project.sdr';project.write_bytes((ROOT/'examples/reference_09.sdr').read_bytes());original=project.read_bytes()
        cli={};versions={}
        for label,archive in [('old',wheel),('rc',ROOT/'dist'/('sedrava-'+VERSION+'-py3-none-any.whl'))]:
            folder=root/label;venv.EnvBuilder(with_pip=True).create(folder);bindir=folder/('Scripts' if os.name=='nt' else 'bin')
            python=bindir/('python.exe' if os.name=='nt' else 'python');command=bindir/('sedrava.exe' if os.name=='nt' else 'sedrava')
            subprocess.run([str(python),'-m','pip','install','--no-index',str(archive)],cwd=root,env=env,check=True)
            cli[label]=command
            versions[label]=subprocess.check_output([str(command),'--version'],cwd=root,env=env,text=True).strip()
            subprocess.run([str(python),'-c',"import importlib.metadata,pathlib,sys,sedrava_core;assert importlib.metadata.metadata('sedrava')['Name']=='sedrava';assert pathlib.Path(sedrava_core.__file__).is_relative_to(sys.prefix)"],cwd=root,env=env,check=True)
            for action in ('check','test'):
                subprocess.run([str(command),action,str(project)],cwd=root,env=env,check=True)
            subprocess.run([str(command),'build','web',str(project),'--output',str(root/(label+' web')/'index.html')],cwd=root,env=env,check=True)
            subprocess.run([str(command),'build','android',str(project),'--output',str(root/(label+' android'))],cwd=root,env=env,check=True)
        if versions!={'old':'sedrava 0.9.0a1','rc':'sedrava '+VERSION}:raise ValueError('Installed version mismatch')
        old=json.loads(subprocess.check_output([str(cli['old']),'run',str(project),'add'],cwd=root,env=env,text=True))
        new=json.loads(subprocess.check_output([str(cli['rc']),'run',str(project),'add'],cwd=root,env=env,text=True))
        if old!=new:raise ValueError('0.9 reference action compatibility changed')
        # Return to the untouched old environment after using RC; no in-place downgrade.
        subprocess.run([str(cli['old']),'test',str(project)],cwd=root,env=env,check=True)
        if project.read_bytes()!=original:raise ValueError('User project modified')
        return {'result':'PASS','baseline_package':'sedrava','baseline_version':'0.9.0a1','baseline_url':BASE+OLD_WHEEL,'baseline_sha256':OLD_SHA,
                'baseline_release_sha256sums_sha256':OLD_SUMS_SHA,'rc_version':VERSION,'installed_versions':versions,
                'verified_commands':['check','test','run add','build web','build android'],'reference_action_result':new,
                'user_source_unchanged':True,'rollback':'reactivate original separate environment; no automatic data migration'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=check();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS: published sedrava 0.9.0a1 wheel -> separate RC environment -> unchanged 0.9 environment; project bytes preserved')
