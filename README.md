# Y's HM Photography — FC2からの移行版

黒い背景、金色のサイト名、6つのメニュー、既存の写真と文章を引き継ぐGitHub Pages用サイトです。FC2側は変更していません。公開するのは **docsフォルダだけ**です。普段の更新にビルドやプログラミング用ライブラリは必要ありません。

## どのファイルを変える？

|変えたいもの|編集するファイル|
|---|---|
|トップ写真・表示順・切り替え秒数|`docs/data/site.json`|
|各ギャラリーの写真・順番・タイトル|`docs/data/albums/CCP番号.json`|
|プロフィール・機材・メール|`docs/content/CCP010.html`|
|撮影の思い出・ギャラリーの紹介文|`docs/content/CCP003.html`|
|PHOTO TIPS|`docs/content/CCP015.html`|
|ゲストギャラリー紹介文|`docs/content/CCP033.html`|
|PORTFOLIOの入口|`docs/content/CCP.html`|
|色・余白・文字サイズ|`docs/assets/site.css`|
|画像ファイル|`docs/assets/photos/`（拡大用）、`docs/assets/thumbs/`（一覧用）|

`docs/data/pages.json`でページのタイトルとファイル名を探せます。たとえば「名古屋みなと祭」は`CCP071.html`、写真リストは`docs/data/albums/CCP071.json`です。既存URLのファイル名を残しています。

`migration/original/`は元データのローカル保管場所です。Gitの対象から除外しています。ここは公開用ではなく、別のディスクなどにも保管してください。`tools/import_fc2.py`は初回移行専用です。実行すると手作業の編集を上書きするため、日常の更新には使いません。

## 文章を変更する

1. 上の表から該当するファイルを開きます。
2. 変更したい日本語の文章だけを書き換えて保存します。`<section>`、`<div>`などの括弧で囲まれた部分はそのまま残します。
3. 改行したい位置には`<br>`を入れます。段落は`<p>文章</p>`でも作れます。
4. ブラウザで確認します。

古い機材・撮影メモ・日付は当時の記録です。現在の事実に変更する場合は、ご自身で内容を確認してから書き換えてください。

## 写真を交換する

最も簡単なのは、同じファイル名の画像を上書きする方法です。`photos`と`thumbs`の両方を交換します。縦横比が変わる場合は一覧ファイルの`width`（横ピクセル数）と`height`（縦ピクセル数）も直します。写真を使い回している場合、同じ画像を参照するすべてのページで変わります。1ページだけ交換したい場合は新しいファイル名を使い、そのページのリストの`src`と`thumb`だけ変更してください。

## 写真を追加・並べ替えする

1. Web用に書き出したJPEGを`docs/assets/photos/`へ入れます。ファイル名は`beach-2026-01.jpg`など、半角英数字とハイフンがおすすめです。
2. 長辺640px程度の小さい版を同じ名前で`docs/assets/thumbs/`へ入れます。
3. アルバムのJSONにある`photos`の中に、次の1件を追加します。

```json
{
  "src": "assets/photos/beach-2026-01.jpg",
  "thumb": "assets/thumbs/beach-2026-01.jpg",
  "width": 1920,
  "height": 1280,
  "alt": "夕暮れの海を歩く人",
  "caption": "海辺にて、2026年9月"
}
```

複数の写真は`},`のようにカンマで区切ります。最後の写真の後にはカンマを付けません。ダブルクォート`"`を使い、JSONの中にコメントは書かないでください。`alt`は写真の説明、`caption`は画面に表示する文章です。説明文を表示しない場合は`"caption": ""`にします。

**並べ替えは、写真1件の`{`から`}`までをまとめて移動するだけ**です。追加後、枚数は自動で変わります。小さい版が用意できない場合は`thumb`の行を削除すれば拡大用画像を一覧にも使用できますが、表示は重くなります。

## 写真を削除する

アルバムのJSONで、対象の写真1件の`{`から`}`までを削除します。前後のカンマも整えます。これでページから消えます。画像ファイル自体は、トップやほかのアルバムでも使われていないか検索してから削除してください。迷ったら画像ファイルを残しておいて構いません。

## トップのスライドショー

`docs/data/site.json`の`slides`がトップの写真リストです。追加・削除・順番変更はアルバムと同じです。`slideshowSeconds`を`6`から`8`にすれば8秒ごとに変わります。最低3秒です。停止・再生と前後のボタンがあり、動きを減らす端末設定では自動再生を停止します。

写真は**横3:2、1920×1280px、sRGBのJPEG**を推奨します。16:9なら1920×1080pxでも使えます。縦や正方形も切り取らずに全体表示するため、周囲に黒い余白が入ります。拡大用は1枚200～600KB程度を目安に、細部を確認しながら書き出してください。一覧用は長辺640px、50～120KB程度が目安です。

旧トップの写真は主に600×400pxで、高解像度画面では少し柔らかく見えます。無理に引き伸ばして保存せず、必要に応じてお手元の元写真から1920px版を書き出して交換してください。RAWや必要以上に大きいJPEGは別の場所に保管します。

## パソコンで確認する

Python 3が使える場合、ターミナルでこのフォルダを開き、次を実行します。

```sh
python3 -m http.server 8000 --directory docs --bind 127.0.0.1
```

ブラウザで`http://127.0.0.1:8000/`を開きます。終了はターミナルでControl+Cです。HTMLを直接ダブルクリックする方法では、写真リストを読み込めません。Pythonがない場合はVS CodeのLive Previewなどのローカルサーバーでも確認できます。

## GitHubへ反映する（GitHub Desktop）

1. GitHub Desktopで`File → Add Local Repository`からこのフォルダを指定します。Git管理がまだなければ表示された案内から作成します。
2. 変更一覧を見て、`migration/original`やRAW画像が含まれていないことを確認します。
3. Summaryに「写真を追加」などと記入し、`Commit to main`を押します。
4. 最初は`Publish repository`、2回目からは`Push origin`でGitHubに反映します。公開先のアカウント・リポジトリを確認してください。
5. 無料プランでPagesを使う場合は公開リポジトリを使います。ローカルの原本保管フォルダをWeb画面へドラッグして一括アップロードしないでください。Webアップロードでは`.gitignore`による除外が働きません。

Gitに慣れている方は、初回は`git init`、`git symbolic-ref HEAD refs/heads/main`、`git add docs README.md .gitignore tools migration/*.json migration/*.md`、`git commit -m "Restore photography website"`、作成したリポジトリを`origin`に設定して`git push -u origin main`でも反映できます。

## GitHub Pagesで公開する

1. GitHubで対象リポジトリを開きます。
2. `Settings → Pages`を開きます。
3. `Build and deployment`のSourceを`Deploy from a branch`にします。
4. Branchを`main`、フォルダを`/docs`にして`Save`を押します。
5. 公開処理が終わると、同じ画面の`Visit site`から開けます。通常は`https://ユーザー名.github.io/リポジトリ名/`になります。
6. トップの写真切り替え・各メニュー・写真拡大・スマートフォン表示を確認します。FC2からの切り替えは、この確認が済んでから判断してください。

この構成では更新のたびにビルドする必要はなく、Pushしたファイルが公開に使われます。`.nojekyll`は残してください。相対パスなので、リポジトリ名がURLに入るPagesにも対応します。

GitHub Pagesの公開サイト上限は1GBです。画像を何度も入れ替えるとGitの履歴も増えるので、Web用の軽い画像だけを追加してください。

公式手順：[Pagesサイトの作成](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)、[容量などの制限](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)（2026年9月確認）。
