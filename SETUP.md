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

`1`か`2`のどちらかに一度`cd`してから実行します（`requirements.txt`の内容は同じなので片方でOK）。

```bash
pip install -r requirements.txt
```

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
`(.venv)` が表示された状態のまま、1本実行して終了してから次を実行してください（3行まとめて貼り付けない）。
`1`フォルダに`cd`してから実行してください。

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

手順は同じです（`winget`の代わりにRaspberry Pi OSに標準搭載のPython/Gitを使用）。
Raspberry Pi OSの「ターミナル」アプリ（画面上部のアイコン、黒い四角のアイコン）を開いて、1行ずつ実行します。

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

USB Webカメラを接続していれば、`03_inference.py` はPCと同じコードのまま動作します。
