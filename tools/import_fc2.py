"""One-time migration; do not rerun after hand-editing docs/content or docs/data."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import json, re, html, hashlib, xml.etree.ElementTree as ET

SOURCE=Path('migration/original'); OUT=Path('docs')
for d in ['assets/photos','assets/thumbs','content','data/albums']: (OUT/d).mkdir(parents=True,exist_ok=True)
mapping={}; hashes={}; missing=[]
def photo(name):
    name=name.removeprefix('./')
    if name in mapping: return mapping[name]
    src=SOURCE/name
    if not src.is_file(): missing.append(name); return None
    try:
        im=ImageOps.exif_transpose(Image.open(src)); im.load()
    except Exception: missing.append(name); return None
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if digest in hashes: mapping[name]=hashes[digest]; return hashes[digest]
    filename=name.replace('/','-').rsplit('.',1)[0]+'.jpg'
    im=im.convert('RGB'); im.thumbnail((1920,1920))
    target=OUT/'assets/photos'/filename
    if not target.exists(): im.save(target,quality=88,optimize=True,progressive=True)
    # Keep an already-small original JPEG byte-for-byte when it is smaller.
    original=Image.open(src)
    if original.format=='JPEG' and max(original.size)<=1920 and original.getexif().get(274,1)==1 and src.stat().st_size<target.stat().st_size:
        target.write_bytes(src.read_bytes())
    w,h=im.size
    if not (OUT/'assets/thumbs'/filename).exists():
        thumb=im.copy(); thumb.thumbnail((640,640)); thumb.save(OUT/'assets/thumbs'/filename,quality=82,optimize=True,progressive=True)
    result=dict(src='assets/photos/'+filename,thumb='assets/thumbs/'+filename,width=w,height=h)
    mapping[name]=result; hashes[digest]=result
    return result

def soup(name): return BeautifulSoup((SOURCE/name).read_bytes().decode('cp932',errors='replace'),'html.parser')
def clean(fragment):
    s=BeautifulSoup(str(fragment),'html.parser')
    for e in s.select('script,object,embed,style,noscript'): e.decompose()
    for e in list(s.find_all('img')):
        src=e.get('src',''); alt=e.get('alt','')
        if src.startswith('logo'):
            if alt: h=s.new_tag('h2'); h.string=alt; e.replace_with(h)
            else: e.decompose()
        elif min(int(e.get('width','99')),int(e.get('height','99')))<=5: e.decompose()
        else:
            p=photo(src)
            if p: e.attrs=dict(src=p['src'],alt=alt,loading='lazy',width=p['width'],height=p['height'])
            else: e.replace_with(s.new_string('[元画像を取得できませんでした: '+src+']'))
    for e in list(s.find_all(True)):
        if e.name=='img': continue
        if e.name=='a':
            href=e.get('href','')
            if re.search(r'\.(jpg|jpeg|png|gif)$',href,re.I):
                asset=photo(href)
                if asset: href=asset['src']
            e.attrs={'href':href}
            if href.startswith('javascript:'): e.unwrap()
        elif e.name in ['br','h2','h3','strong','em','p','ul','li']: e.attrs={}
        else: e.unwrap()
    text=str(s).replace('\xa0',' ')
    text=re.sub(r'[ \t\u3000]+',' ',text)
    text=re.sub(r'(?:\s*<br/>\s*){3,}','<br/><br/>',text)
    return text.strip()

nav=[('index.html','TOP'),('CCP.html','PORTFOLIO'),('CCP003.html','GALLERIES'),('CCP015.html','PHOTO TIPS'),('CCP033.html','GUEST GALLERIES'),('CCP010.html','ABOUT')]
albums={}; pages=[]
for src in sorted(SOURCE.glob('*.html')):
    s=soup(src.name); main=s.select_one('#main')
    if not main: continue
    title=s.title.get_text() if s.title else src.stem
    anchors=main.select('a.HPZImageLightBox') if src.name not in [n[0] for n in nav] else []
    if anchors:
        items=[]
        for i,a in enumerate(anchors):
            p=photo(a['href'])
            if p: items.append(dict(**p,alt=a.get('title') or f'{title} — {i+1}',caption=a.get('title','')))
        albums[src.name]=dict(title=title,photos=items)
        (OUT/'data/albums'/f'{src.stem}.json').write_text(json.dumps(albums[src.name],ensure_ascii=False,indent=2))
    pages.append(dict(file=src.name,title=title,kind='album' if anchors else 'content',originalPhotoCount=len(anchors)))

for page in pages:
    name=page['file']; main=soup(name).select_one('#main'); chunks=[]
    if page['kind']=='album' or name=='index.html': continue
    if name=='CCP.html':
        chunks=['<div class="portfolio-grid">']
        for a in main.select('a[href]'):
            dest=a['href']; im=a.find('img')
            if dest not in albums: continue
            title=albums[dest]['title']; p=albums[dest]['photos'][0] if albums[dest]['photos'] else None
            if p: chunks.append(f'<a class="portfolio-item" href="{dest}"><img src="{p["thumb"]}" alt="{html.escape(title)}" loading="lazy"><h2>{html.escape(title)}</h2></a>')
        chunks.append('</div>')
    elif name in ['CCP003.html','CCP033.html','CCP015.html']:
        for row in main.find_all('tr'):
            cells=row.find_all('td',recursive=False)
            if len(cells)<2 or not cells[0].find('img'): continue
            textcell=cells[-1]
            if not textcell.get_text(strip=True): continue
            link=cells[0].find('a'); dest=link.get('href') if link else None
            if dest in albums:
                image=albums[dest]['photos'][0] if albums[dest]['photos'] else None
                imagehtml=f'<a href="{dest}"><img src="{image["thumb"]}" alt="{html.escape(albums[dest]["title"])}" loading="lazy"></a>' if image else clean(cells[0])
            else: imagehtml=clean(cells[0])
            chunks.append('<section class="story"><div class="story-image">'+imagehtml+'</div><div class="story-copy">'+clean(textcell)+'</div></section>')
    else: chunks=['<div class="prose">'+clean(main)+'</div>']
    (OUT/'content'/name).write_text('\n'.join(chunks),encoding='utf-8')

slides=[]
for im in ET.parse(SOURCE/'flashgallery002/flashgallery.xml').findall('./images/image'):
    p=photo('flashgallery002/'+im.find('large').get('filename'))
    if p: slides.append(dict(**p,alt=im.findtext('title') or "Y's HM Photography",caption=im.findtext('title') or ''))
settings=dict(title="Y's HM Photography",tagline='heartwarming photo　心あたたまる写真',slideshowSeconds=6,slides=slides)
(OUT/'data/site.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2))
(OUT/'data/pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2))
for p in pages:
    links=''.join(f'<a href="{href}"'+(' aria-current="page"' if href==p['file'] else '')+f'>{label}</a>' for href,label in nav)
    (OUT/p['file']).write_text(f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(p['title'])} | Y's HM Photography</title><meta name="description" content="Y's HM Photography。心あたたまる写真と、撮影の思い出。">
<link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script></head>
<body data-page="{p['file']}" data-kind="{p['kind']}"><a class="skip" href="#main">本文へ</a>
<header><a class="brand" href="index.html">Y's HM Photography</a><nav aria-label="メインメニュー">{links}</nav></header>
<main id="main"><p role="status">読み込み中…</p></main>
<noscript><p>写真一覧の表示にはJavaScriptを有効にしてください。</p></noscript>
<footer>© Y's HM Photography <a href="#top" id="to-top">ページの先頭へ ↑</a></footer>
<dialog id="viewer" aria-label="写真の拡大表示"><div class="viewer-toolbar"><span id="counter"></span><button id="close-viewer" aria-label="拡大表示を閉じる">閉じる ×</button></div>
<img id="viewer-photo" alt=""><p id="viewer-caption"></p><div class="viewer-controls"><button id="previous" aria-label="前の写真">← 前へ</button><button id="play-viewer">再生</button><button id="next" aria-label="次の写真">次へ →</button></div></dialog>
</body></html>''',encoding='utf-8')
(OUT/'.nojekyll').touch()
Path('migration/photo-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
Path('migration/import-result.json').write_text(json.dumps(dict(pages=len(pages),albums=len(albums),placements=sum(len(a['photos']) for a in albums.values()),uniqueImages=len(hashes),missing=sorted(set(missing))),ensure_ascii=False,indent=2))
print(Path('migration/import-result.json').read_text())
