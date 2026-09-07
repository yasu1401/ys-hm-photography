"""Run with Python 3: python3 tools/check_site.py"""
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parent.parent/'docs'
errors=[]; checked=0

def check(value,base=ROOT):
    global checked
    u=urlsplit(value)
    if u.scheme or u.netloc or not u.path:return
    target=base/unquote(u.path)
    checked+=1
    if not target.exists():errors.append(f'Missing: {target.relative_to(ROOT)}')
class Links(HTMLParser):
    def __init__(self,base):super().__init__();self.base=base
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v:check(v,self.base)
for p in ROOT.rglob('*.html'):
    # Content fragments are inserted into root-level pages.
    base=ROOT if p.parent.name=='content' else p.parent
    Links(base).feed(p.read_text())
for p in (ROOT/'data').rglob('*.json'):
    try:data=json.loads(p.read_text())
    except Exception as e:errors.append(f'{p}: {e}');continue
    def walk(obj):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in ('src','thumb','file') and isinstance(v,str):check(v)
                else:walk(v)
        elif isinstance(obj,list):
            for x in obj:walk(x)
    walk(data)
size=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
print(f'Checked {checked} local references. Site size {size/1e6:.1f} MB.')
if size>1e9:errors.append('Site exceeds 1 GB')
for p in ROOT.rglob('*'):
    if p.is_file() and p.stat().st_size>10e6:errors.append(f'Large file: {p}')
if errors:
    print('\n'.join(sorted(set(errors))))
    raise SystemExit(1)
print('PASS: all local links and JSON references resolve.')
