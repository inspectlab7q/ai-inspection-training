# セットアップ手順（Windows PC）

このリポジトリはPublicなので、GitHubアカウントは不要です。
**Python** と **Git** の2つを導入すれば、講習当日でも、持ち帰った後の会社PCでも同じ手順で使えます。

以降の手順は、すべて「コマンドプロンプト」という黒い画面に文字を入力して進めます。
プログラミング未経験の方向けに、その開き方から説明します。

## 0. コマンドプロンプトを開く

1. キーボードの **Windowsキー** を押す（画面左下のスタートボタンでも可）
2. そのまま `cmd` と入力する
3. 検索結果に出てくる **「コマンドプロンプト」** をクリックして開く

黒い画面（下のような表示）が出れば成功です。

```
C:\Users\あなたの名前>
```

これ以降、コードブロックで示すコマンドは、この画面に**そのまま貼り付けて（またはタイプして）Enterキー**を押して実行します。
貼り付けは、コピーした状態でコマンドプロンプトの画面を右クリックすると貼り付けられます。

## 1. Pythonのインストール

```bash
winget install --id Python.Python.3.11 -e
```

1. 上記コマンドを貼り付けてEnter
2. 途中で「インストールされます」等の確認が出たら `Y` を入力してEnter（出ない場合もある）
3. `インストールが完了しました` と表示されたら成功
4. インストール後、一度コマンドプロンプトを閉じ、0の手順でもう一度開き直す
   （閉じずに使い続けると、`python`コマンドが認識されないことがある）
5. 正しく入るか確認：

```bash
python --version
```

`Python 3.11.x` のように表示されればOK。`'python' は、内部コマンドまたは外部コマンド...` と出た場合は、4の「開き直し」を忘れていないか確認してください。

（winget が使えない場合は [python.org](https://www.python.org/downloads/) から3.11系をダウンロードし、インストーラーの最初の画面で **「Add python.exe to PATH」に必ずチェック** を入れてください）

## 2. Gitのインストール

```bash
winget install --id Git.Git -e
```

Pythonと同じく、完了後は一度コマンドプロンプトを閉じて開き直してください。

```bash
git --version
```

`git version 2.x.x` のように表示されればOK。

## 3. プログラムの取得と仮想環境の準備

STEP1とSTEP2（[ai-inspection-multiscene](https://github.com/inspectlab7q/ai-inspection-multiscene)）を両方使う前提の手順。
親フォルダを1つ作り、その中にSTEP1・STEP2をそれぞれサブフォルダとして`clone`し、
仮想環境は親フォルダに1つだけ作ります（**STEP1・STEP2の`requirements.txt`は中身が同じ**なので共有できる）。

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

> コマンドプロンプトを一度閉じて後日また作業する場合は、`ai-inspection`フォルダ（`1`や`2`の中ではなく、
> その一つ上）に移動した上で、もう一度 `.venv\Scripts\activate` を実行してください
> （`python -m venv .venv` は最初の1回だけでよい）。
> STEP1・STEP2のプログラムを実行するときは、`(.venv)`を有効にしたまま
> `cd 1`（STEP1）または`cd 2`（STEP2）で該当フォルダに移動してから実行してください。

## 4. ライブラリの導入

```bash
cd 1
```

```bash
pip install -r requirements.txt
```

STEP1・STEP2の`requirements.txt`は中身が同じなので、`1`側で1回入れれば`2`でも使えます
（`2`フォルダに`cd`して入れ直す必要はありません）。

インストールには数分かかります。ネット回線が遅い場合は特に、事前（前日まで）に済ませておくことを強く推奨します。

## 5. 学習済み重みの事前ダウンロード（重要）

`02_train.py` はMobileNetV2の学習済み重み（約9MB）をインターネットから自動ダウンロードします。
講習当日、現場のモバイルWi-Fiなど不安定な回線でこれを初めて行うと、ダウンロードが途中で切れて
`OSError: Unable to synchronously open file` というエラーになることがあります。

安定した回線がある事前準備の段階で、一度だけ以下を実行してキャッシュしておいてください
（`(.venv)` を有効にした状態で実行）。

```bash
python -c "import tensorflow as tf; tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False)"
```

エラーなく終了すればキャッシュ完了です。以降は`02_train.py`を回線なしで実行してもこのステップは通ります。

> もし途中でこのエラーが出た場合は、キャッシュが壊れているので削除してやり直してください:
> ```bash
> rmdir /s /q "%USERPROFILE%\.keras\models"
> ```

## 6. 事前に確認しておくこと

- **カメラのプライバシー設定**：Windowsの「設定 → プライバシーとセキュリティ → カメラ」で
  「デスクトップアプリがカメラにアクセスすることを許可する」がONになっているか確認してください。
  OFFのままだと `cv2.VideoCapture(0)` が映像を取得できません。
- **`DLL load failed` エラーが出た場合**：
  [Visual C++ 再頒布可能パッケージ](https://aka.ms/vs/17/release/vc_redist.x64.exe) を導入してください。
- **Webカメラが複数ある場合**：各プログラムの `CONFIG` 内 `CAMERA_ID` を `0` → `1`, `2`… と変更してください。

## 7. 動作確認

セットアップが終わったら、1つずつ実行して動くことを確認してください（詳しい使い方は [README.md](README.md) 参照）。
`(.venv)` が表示され、`1`フォルダにいる状態のまま、1本実行して終了してから次を実行してください（3行まとめて貼り付けない）。

```bash
python 01_capture_augment.py
```

```bash
python 02_train.py
```

```bash
python 03_inference.py
```

---

## Raspberry Piの場合

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
現場のネット回線に依存しないよう、この手順は事前に済ませておくことを推奨します（PC側のSETUP.mdと同じ理由）。

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

（Pcからアクセスする際のパスワードを聞かれるので設定。`ユーザー名`はPiのログインユーザー名に置き換える）

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

### 3. PCからモデルをコピーする

Windowsのエクスプローラーのアドレス欄に、確認したIPアドレスを使って以下のように入力します。

```
\\<Piのipアドレス>\ai-inspection
```

Piのユーザー名・先ほど設定したSMBパスワードを聞かれたら入力してください。

共有フォルダ（`ai-inspection`直下）が開いたら、`model`フォルダを探します。
**`model`フォルダは`.gitignore`されているため、`git clone`した直後は存在しません。無ければ新規作成してください。**

1. この画面（`ai-inspection`直下）で右クリック → 新規作成 → フォルダー → 名前を`model`にする
2. PC側の`ai-inspection-training\model\model.tflite`（`02_train.py`が出力したもの）を、その`model`フォルダにドラッグ＆ドロップでコピーする

この設定は最初の1回だけでOKです。次回以降は、同じ手順でエクスプローラーからそのままアクセスできます
（2回目以降は`model`フォルダが既にあるので、作成は不要）。

### 4. Pi側で実行

Piのターミナル（モニター・キーボードで直接操作）に戻り、実行します。

```bash
python 03_inference.py
```

USB Webカメラを接続していれば、コードはPCと同じままで動作します。
検査範囲(ROI)はPCとカメラの設置位置が変わるため、初回はPi側で選び直すことになります
（`roi_config.json`が無ければ自動でライブ選択画面が出ます）。

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
