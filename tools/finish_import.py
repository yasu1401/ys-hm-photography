"""One-time content corrections after initial import; not a routine build step."""
from pathlib import Path
import json,re
from bs4 import BeautifulSoup
ROOT=Path('docs'); corrections=[]
for name in ['CCP003.html','CCP033.html','CCP015.html']:
 p=ROOT/'content'/name;s=BeautifulSoup(p.read_text(),'html.parser')
 for story in s.select('.story'):
  cover=story.select_one('.story-image a');copy=story.select_one('.story-copy')
  if cover and cover.get('href','').endswith('.html'):
   dest=cover['href']
   for a in copy.select('a[href]'):
    if re.fullmatch(r'CCP\d*\.html',a['href']) and a['href']!=dest:
     corrections.append(dict(page=name,text=a.get_text(' ',strip=True),old=a['href'],new=dest));a['href']=dest
  # Promote the existing first text line to a real heading, keeping wording.
  raw=copy.decode_contents().strip()
  raw=re.sub(r'^(?:\s*<br/?>(?:\s|&nbsp;)*)+','',raw)
  head,sep,rest=raw.partition('<br/>')
  if sep and BeautifulSoup(head,'html.parser').get_text(strip=True):
   copy.clear();copy.append(BeautifulSoup('<h2>'+head+'</h2>'+rest,'html.parser'))
 for a in s.select('a[href]'):
  if a['href'].startswith('http'):
   label=s.new_tag('span',attrs={'class':'link-note'});label.string='（リンク先を確認できません・当時のURL）';a.insert_after(label)
 p.write_text(str(s))
p=ROOT/'content/CCP010.html';s=p.read_text();s=s.replace('・キーボードの"Ｆ１１"を押すとメニューバーとかが消えて全画面表示になります。この方が気持ちよく見れます。','・写真をクリックまたはタップすると拡大できます。閉じるボタンで一覧に戻ります。')
s=s.replace('・"PORTFOLIO"や"GALLERIES"で写真をクリックすると写真が拡大表示され、右下の再生ボタンを押すとスライドショーになります。','・拡大画面の「再生」でスライドショーになります。前後ボタンやキーボードの左右矢印でも写真を送れます。Escキーでも閉じられます。')
s='<p class="archive-note">機材・活動内容・更新頻度は、FC2公開当時の記録です。</p>\n'+s
s=s.replace('（友達のHPです。）','（友達のHPです。リンク先は現在確認できません）')
p.write_text(s)
for name,date in [('CCP.html','Update: Dec 8, 2011'),('CCP003.html','July 27, 2013更新'),('CCP033.html','Update: June 25, 2011')]:
 p=ROOT/'content'/name;p.write_text('<p class="archive-note">'+date+'（FC2掲載時）</p>\n'+p.read_text())
# Only remove superseded files created by this migration, never originals.
extra=ROOT/'data/albums/CCP015.json'
if extra.exists():extra.unlink()
refs=set()
for p in ROOT.rglob('*'):
 if p.is_file() and p.suffix in ['.json','.html']:
  refs.update(re.findall(r'assets/(?:photos|thumbs)/[^"<>\s]+',p.read_text()))
removed=[]
for p in (ROOT/'assets').rglob('*.jpg'):
 if str(p.relative_to(ROOT)) not in refs:removed.append(str(p.relative_to(ROOT)));p.unlink()
Path('migration/link-corrections.json').write_text(json.dumps(corrections,ensure_ascii=False,indent=2))
Path('migration/generated-cleanup.json').write_text(json.dumps(removed,ensure_ascii=False,indent=2))
print('Internal wrong destinations fixed:',len(corrections),'superseded generated images removed:',len(removed))
