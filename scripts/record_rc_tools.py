"""Record actual tool versions without environment/credential values."""
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import shutil
import sys

def record(android=False):
    result={'python':platform.python_version(), 'platform':platform.platform(), 'python_distributions':{}}
    for item in importlib.metadata.distributions():
        name=item.metadata.get('Name')
        if name:result['python_distributions'][name]=item.version
    if shutil.which('node'):
        result['node']=subprocess.check_output(['node','--version'],text=True).strip()
    if android:
        for name,command in [('java',['java','-version']),('gradle',['gradle','--version'])]:
            run=subprocess.run(command,capture_output=True,text=True,check=True)
            result[name]=(run.stdout+run.stderr).strip()
        props=Path(os.environ['ANDROID_HOME'])/'build-tools/35.0.0/source.properties'
        result['android_build_tools']=props.read_text()
        result['direct_dependencies']={'AGP':'8.9.2','Kotlin':'2.0.21','Compose_BOM':'2024.12.01','activity_compose':'1.9.3','min_sdk':26,'target_sdk':35}
    return result

if __name__=='__main__':
    output=Path(sys.argv[1]);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(record('--android' in sys.argv),sort_keys=True,indent=2)+'\n')
