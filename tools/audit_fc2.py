import urllib.request, urllib.parse, pathlib, json, re
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
BASE='http://heartwarmingphotographer.web.fc2.com/'
ROOT=pathlib.Path('migration/original')
ROOT.mkdir(parents=True, exist_ok=True)
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.refs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for k in ('href','src','background'):
            if a.get(k): self.refs.append(a[k])
        if tag=='param' and a.get('name')=='movie': self.refs.append(a.get('value',''))
queue=['index.html','flashgallery002/flashgallery.xml']; seen=set(); results=[]
def fetch(rel):
    path=ROOT/rel
    try:
        if path.exists(): return rel,path.read_bytes(),200,''
        with urllib.request.urlopen(urllib.parse.urljoin(BASE,rel),timeout=25) as f: data=f.read(); status=f.status; ctype=f.headers.get('Content-Type','')
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
        return rel,data,status,ctype
    except Exception as e: return rel,None,0,str(e)
with ThreadPoolExecutor(max_workers=6) as pool:
    while queue and len(seen)<12000:
        batch=list(dict.fromkeys(r for r in queue if r not in seen)); queue=[]; seen.update(batch)
        for rel,data,status,ctype in pool.map(fetch,batch):
            if data is None:
                results.append(dict(path=rel,error=ctype)); continue
            results.append(dict(path=rel,status=status,bytes=len(data),type=ctype))
            if rel.lower().endswith(('.html','.htm','.css','.xml')):
                try: s=data.decode('utf-8')
                except UnicodeDecodeError: s=data.decode('cp932',errors='replace')
                p=Links(); p.feed(s)
                refs=p.refs+re.findall(r"[\"']([^\"']+\.(?:jpg|jpeg|png|gif|xml))[\"']",s,re.I)+re.findall(r'url\([\"\']?([^\)\"\']+)',s)
                refs+=re.findall(r'>([^<>]+\.(?:jpg|jpeg|png))<',s,re.I)
                for ref in refs:
                    u=urllib.parse.urlsplit(urllib.parse.urljoin(urllib.parse.urljoin(BASE,rel),ref))
                    if u.netloc!=urllib.parse.urlsplit(BASE).netloc or u.query: continue
                    name=urllib.parse.unquote(u.path).lstrip('/')
                    if name and '..' not in pathlib.PurePosixPath(name).parts and name not in seen: queue.append(name)
            if len(results)%100==0: print('Saved',len(results),flush=True)
            pathlib.Path('migration/inventory.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('Complete',len(results),'errors',sum('error' in x for x in results))
