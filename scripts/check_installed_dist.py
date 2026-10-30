"""Install both archives in isolated venvs; exercise bundled apps outside checkout."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

ROOT=Path(__file__).resolve().parents[1]

def check(archive, folder):
    venv.EnvBuilder(with_pip=True).create(folder)
    bindir=folder/('Scripts' if os.name=='nt' else 'bin')
    python=bindir/('python.exe' if os.name=='nt' else 'python')
    cli=bindir/('sedrava.exe' if os.name=='nt' else 'sedrava')
    env=os.environ.copy();env.pop('PYTHONPATH',None)
    def run(*args):
        subprocess.run(list(map(str,args)),cwd=folder,env=env,check=True)
    run(python,'-m','pip','install','--no-cache-dir',archive)
    run(python,'-c',"import pathlib,sys,sedrava_core,sedrava_android_identity;assert pathlib.Path(sedrava_core.__file__).is_relative_to(sys.prefix);assert (pathlib.Path(sys.prefix)/'share/sedrava/docs/BUILD.md').is_file();assert (pathlib.Path(sys.prefix)/'share/sedrava/LICENSE').is_file()")
    run(cli,'--version')
    for name in ('task_manager','task_manager_navigation'):
        source=folder/'share/sedrava/examples'/f'{name}.sdr'
        run(cli,'check',source);run(cli,'test',source);run(cli,'run',source)
        web=folder/'generated with spaces'/name/'index.html'
        run(cli,'build','web',source,'--output',web)
        before=web.read_bytes()
        run(cli,'build','web',source,'--output',web)
        assert before==web.read_bytes()
        run(cli,'build','android',source,'--output',folder/'generated with spaces'/name/'android')
    run(cli,'build','android',source,'--application-id','com.example.installed','--output',folder/'explicit android')
    print(f'PASS: clean {archive.name}, bundled docs/examples/license, check/test/run/Web/Android and deterministic Web',flush=True)

if __name__=='__main__':
    archives=[*sorted((ROOT/'dist').glob('*.whl')),*sorted((ROOT/'dist').glob('*.tar.gz'))]
    assert len(archives)==2,'Build exactly one wheel and sdist first'
    with tempfile.TemporaryDirectory(prefix='sedrava installed ') as tmp:
        for index,archive in enumerate(archives):check(archive,Path(tmp)/str(index))
