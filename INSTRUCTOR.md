# 講師用ノート

このファイルは、**講師が事前準備・当日運用のために使う**内容をまとめたものです。
受講者に配布する [SETUP.md](SETUP.md)（PCの最小限の準備手順）とは別に管理しています。

## STEP1とSTEP2を両方使う場合の構成

[ai-inspection-multiscene](https://github.com/inspectlab7q/ai-inspection-multiscene)（STEP2）も同じPCで扱う場合、
親フォルダを1つ作り、その中にSTEP1・STEP2をそれぞれサブフォルダとして`clone`し、
仮想環境は親フォルダに1つだけ作ると、`pip install`を2回やらずに済みます
（**STEP1・STEP2の`requirements.txt`は中身が同じ**）。

```
Desktop\
  ai-inspection\        ← 親フォルダ
    .venv\                ← 仮想環境はここに1つだけ
    1\                     ← STEP1 (ai-inspection-training)
    2\                     ← STEP2 (ai-inspection-multiscene)
```

**1行ずつ**Enterを押して実行してください（複数行まとめて貼り付けると、`git clone`の途中経過表示に
紛れて次の行が実行されないことがあるため）。

```bash
cd Desktop
```

```bash
mkdir ai-inspection
```

```bash
cd ai-inspection
```

```bash
git clone https://github.com/inspectlab7q/ai-inspection-training.git 1
```

```bash
git clone https://github.com/inspectlab7q/ai-inspection-multiscene.git 2
```

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

`activate`を実行した後にプロンプトの先頭へ `(.venv)` と表示されればOKです。
以降のコマンドは、必ずこの `(.venv)` が表示された状態で実行してください。

```bash
cd 1
```

```bash
pip install -r requirements.txt
```

STEP1・STEP2の`requirements.txt`は中身が同じなので、`1`側で1回入れれば`2`でも使えます
（`2`フォルダに`cd`して入れ直す必要はありません）。

> コマンドプロンプトを一度閉じて後日また作業する場合は、`ai-inspection`フォルダ（`1`や`2`の中ではなく、
> その一つ上）に移動した上で、もう一度 `.venv\Scripts\activate` を実行してください
> （`python -m venv .venv` は最初の1回だけでよい）。
> STEP1・STEP2のプログラムを実行するときは、`(.venv)`を有効にしたまま
> `cd 1`（STEP1）または`cd 2`（STEP2）で該当フォルダに移動してから実行してください。

### 起動用ショートカット（あると便利）

毎回`.venv\Scripts\activate`→`cd 1`と打つのが面倒な場合、以下の内容をメモ帳に貼り付けて、
`ai-inspection`フォルダ直下（`.venv`と同じ階層）に`start.bat`という名前で保存しておくと、
ダブルクリックだけでvenv起動→STEP1/STEP2選択まで一発で行えます
（メモ帳の保存時、ファイルの種類を「すべてのファイル」にし、拡張子が`.txt`にならないよう注意）。

```bat
@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo.
echo  [1] STEP1 (ai-inspection-training)
echo  [2] STEP2 (ai-inspection-multiscene)
echo.
choice /c 12 /n /m "Which one? (1 or 2): "
if errorlevel 2 (
    cd 2
) else (
    cd 1
)
cmd /k
```

この`start.bat`を右クリック→「ショートカットの作成」し、できたショートカットをデスクトップに置けば、
デスクトップからダブルクリックするだけで起動できる。

---

## Raspberry Piの準備

ラズパイにはモニター・キーボードを直接接続し、Pi本体のターミナルで作業します。
PCとラズパイは有線LANで同じネットワークに接続。**お客様のPCには追加のソフトを一切インストールしません**
（SFTP/VNCクライアントなどは使わず、Windows標準のファイル共有機能だけを使います）。

### 1. コードの取得とライブラリ導入（ラズパイ本体で）

Piに繋いだキーボード・モニターで、ターミナルアプリを開いて実行します。

```bash
git clone https://github.com/inspectlab7q/ai-inspection-training.git
```

```bash
cd ai-inspection-training
```

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

**このステップにはPi自体のインターネット接続が必要です**（ライブラリはPCとPiでCPUの種類が違うため、PC側でインストールしたものをコピーしても動きません）。
現場のネット回線に依存しないよう、この手順は事前に済ませておくことを推奨します。

### 2. ファイル共有(SMB)を設定する（最初の1回だけ）

学習済みモデル（`model/model.tflite`）はGitには含まれていません（お客様のワーク固有の情報のため）。
PCから直接コピーできるよう、Pi側にSMB（Windowsのファイル共有）を立てます。

```bash
sudo apt update
```

```bash
sudo apt install -y samba samba-common-bin
```

```bash
sudo smbpasswd -a ユーザー名
```

（PCからアクセスする際のパスワードを聞かれるので設定。`ユーザー名`はPiのログインユーザー名に置き換える）

設定ファイルを開いて、共有フォルダを追記します。

```bash
sudo nano /etc/samba/smb.conf
```

ファイルの一番下に、以下を追記して保存します（`Ctrl+O` → `Enter`で保存、`Ctrl+X`で終了）。

```
[ai-inspection]
   path = /home/ユーザー名/ai-inspection-training
   read only = no
   guest ok = no
```

保存後、Sambaを再起動します。

```bash
sudo systemctl restart smbd
```

PiのIPアドレスを確認しておきます（この後Windows側で使います）。

```bash
hostname -I
```

### 3. PCからモデルと設定をコピーする

Windowsのエクスプローラーのアドレス欄に、確認したIPアドレスを使って以下のように入力します。

```
\\<Piのipアドレス>\ai-inspection
```

Piのユーザー名・先ほど設定したSMBパスワードを聞かれたら入力してください。

共有フォルダ（`ai-inspection`直下）が開いたら、`model`フォルダを探します。
**`model`フォルダは`.gitignore`されているため、`git clone`した直後は存在しません。無ければ新規作成してください。**

1. この画面（`ai-inspection`直下）で右クリック → 新規作成 → フォルダー → 名前を`model`にする
2. PC側の`ai-inspection-training\model\model.tflite`（`02_train.py`が出力したもの）を、その`model`フォルダにドラッグ＆ドロップでコピーする
3. PC側の`ai-inspection-training\roi_config.json`も、共有フォルダのルート（`ai-inspection`直下、`model`と同じ階層）にコピーする

この設定は最初の1回だけでOKです。次回以降は、同じ手順でエクスプローラーからそのままアクセスできます
（2回目以降は`model`フォルダが既にあるので、作成は不要）。

> `roi_config.json`はPC上でのカメラ位置を基準にした値です。ラズパイ側でカメラの設置位置が変わっていると
> 検査範囲がずれることがありますが、`03_inference.py`実行中に`R`キーを押せばその場で選び直せます
> （ファイルを手動で消す必要はありません）。

### 4. Pi側で実行

Piのターミナル（モニター・キーボードで直接操作）に戻り、実行します。

```bash
python 03_inference.py
```

USB Webカメラを接続していれば、コードはPCと同じままで動作します。
検査範囲がPC側と合わない場合は、`R`キーでその場でPi用に選び直してください。

### デスクトップからダブルクリックで実行できるようにする（あると便利）

毎回ターミナルで`cd`・`source .venv/bin/activate`・`python 03_inference.py`と打つのが大変な場合、
デスクトップにアイコンを1つ作っておくと、ダブルクリックだけで起動できます。

```bash
nano ~/Desktop/ai-inspection.desktop
```

以下を貼り付けて保存します（`Ctrl+O` → `Enter`で保存、`Ctrl+X`で終了。`ユーザー名`は実際の値に置き換える）。

```
[Desktop Entry]
Type=Application
Name=AI Inspection
Comment=Run 03_inference.py
Exec=bash -c "cd /home/ユーザー名/ai-inspection-training && source .venv/bin/activate && python 03_inference.py; echo; echo Press Enter to close...; read"
Terminal=true
Icon=camera-photo
```

実行権限を付けます。

```bash
chmod +x ~/Desktop/ai-inspection.desktop
```

デスクトップのアイコンをダブルクリックすると起動します。初回だけ「信頼して実行しますか」といった
確認ダイアログが出ることがあるので、そのときは「実行」を選んでください。

### 時間短縮したい場合：SDカードを複製する

ラズパイのライブラリ導入（`pip install`）はPCより時間がかかる。複数台用意する場合は、
1台で上記1〜2（コード取得・ライブラリ導入・SMB設定）まで済ませた「元カード」を作り、
そのSDカードを複製して配ると、他のPiでは`git clone`や`pip install`が不要になる。

**準備するもの**：PC用のSDカードリーダー、[Win32DiskImager](https://sourceforge.net/projects/win32diskimager/)（無料）

1. 元になるラズパイで、上記の手順（1〜2）をすべて完了させる
2. 正常にシャットダウンし、SDカードを取り出す

   ```bash
   sudo shutdown -h now
   ```

3. PCにSDカードリーダーでカードを挿し、Win32DiskImagerの「Read」機能でカードの中身を`.img`ファイルとして保存する
4. 複製先の空SDカードを挿し、同じツールの「Write」機能で、保存した`.img`を書き込む

**複製後、他のPiと同じネットワークに繋ぐ前に、必ず以下を変更する**（そのままだと、
元のPiと同じ固定IP・ホスト名を持った2台が同時にネットワーク上に存在することになり、IPアドレスが衝突する）。

- 固定IPを、そのPi用の値に変更する（例：講師機`172.25.120.11` → 受講者機`172.25.120.30`）
- ホスト名を変更する（`sudo raspi-config` → `System Options` → `Hostname`）

以降、コードが更新された場合は、複製済みの各Piで`git pull`するだけでよい
（ライブラリのバージョンが変わらない限り、`pip install`のやり直しは不要）。
