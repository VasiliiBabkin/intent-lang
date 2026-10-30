"""Read-only current-version reservation checks. Never create a tag or upload."""
import datetime
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sedrava_version import VERSION
from scripts.rc_api import GitHub


def check(api):
    checks=[]
    for path in ['/git/ref/tags/v'+VERSION,'/releases/tags/v'+VERSION]:
        try:api.get(path)
        except urllib.error.HTTPError as exc:
            if exc.code!=404:raise
            checks.append({'url':'https://api.github.com/repos/'+api.repo+path,'http_status':404,'result':'absent'})
        else:raise ValueError('Version already exists on GitHub: '+path)
    url='https://pypi.org/pypi/sedrava/'+VERSION+'/json'
    try:
        with urllib.request.urlopen(url,timeout=30) as response:response.read(1000)
    except urllib.error.HTTPError as exc:
        if exc.code!=404:raise
        checks.append({'url':url,'http_status':404,'result':'absent'})
    else:raise ValueError('Version already exists on PyPI')
    return {'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'version':VERSION,'checks':checks,
            'testpypi':'not checked; not a publication target; unavailable in managed local environment',
            'notice':'Recheck immediately before any separately authorized publication; this is not a reservation.'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    data=check(GitHub('VasiliiBabkin/sedrava'))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    print('PASS: RC version absent on PyPI and GitHub at recorded UTC time; no mutation performed')
