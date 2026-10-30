"""Read-only GitHub API client with bounded downloads and redirect credential stripping."""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from scripts.rc_archive import MAX_BYTES

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme != 'https':
            raise ValueError('Refusing non-HTTPS artifact redirect')
        target=super().redirect_request(req,fp,code,msg,headers,newurl)
        if urllib.parse.urlsplit(newurl).netloc != 'api.github.com':
            target.remove_header('Authorization')
        return target

class GitHub:
    def __init__(self,repo,token=None):
        if repo != 'VasiliiBabkin/sedrava':raise ValueError('Unexpected release repository')
        self.repo=repo;self.token=token if token is not None else os.environ.get('GH_TOKEN','')
        self.opener=urllib.request.build_opener(SafeRedirect())
    def get(self,path,binary=False):
        if not path.startswith('/') or '..' in path:raise ValueError('Unsafe API path')
        url='https://api.github.com/repos/'+self.repo+path
        headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'Sedrava-RC-preparation'}
        if self.token:headers['Authorization']='Bearer '+self.token
        for attempt in range(3):
            try:
                with self.opener.open(urllib.request.Request(url,headers=headers),timeout=60) as response:
                    data=response.read(MAX_BYTES+1)
                if len(data)>MAX_BYTES:raise ValueError('Download exceeds size limit')
                return data if binary else json.loads(data)
            except urllib.error.HTTPError as exc:
                if exc.code not in (429,500,502,503,504) or attempt==2:raise
                time.sleep(5*(attempt+1))
    def pages(self,path,key):
        output=[]
        for page in range(1,11):
            chunk=self.get(path+('&' if '?' in path else '?')+'per_page=100&page='+str(page))[key]
            output.extend(chunk)
            if len(chunk)<100:return output
        raise ValueError('API pagination exceeds bound')
    def job_log(self,job):
        return self.get('/actions/jobs/'+str(job)+'/logs',binary=True).decode('utf-8-sig')
