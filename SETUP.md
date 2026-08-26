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

## 3. プログラムの取得

作業したいフォルダに移動してから（例：デスクトップに置く場合）、以下を実行します。

```bash
cd Desktop
git clone https://github.com/inspectlab7q/ai-inspection-training.git
cd ai-inspection-training
```

`ai-inspection-training` フォルダがデスクトップにできていれば成功です。
以降のコマンドは、すべてこの `ai-inspection-training` フォルダの中で実行します
（`cd ai-inspection-training` を実行した直後の状態）。

## 4. 仮想環境(venv)の作成

PCに他の用途でPythonを使っている場合、ライブラリのバージョンがぶつかることがあるため、
このプロジェクト専用の仮想環境を作って作業します。

```bash
python -m venv .venv
.venv\Scripts\activate
```

`activate`を実行した後、プロンプトの先頭に `(.venv)` と表示されればOKです（例: `(.venv) C:\...\ai-inspection-training>`）。
以降のコマンドは、必ずこの `(.venv)` が表示された状態で実行してください。

> コマンドプロンプトを一度閉じて後日また作業する場合は、`ai-inspection-training` フォルダに移動した上で、
> もう一度 `.venv\Scripts\activate` を実行してください（`python -m venv .venv` は最初の1回だけでよい）。

## 5. ライブラリの導入

```bash
pip install -r requirements.txt
```

インストールには数分かかります。ネット回線が遅い場合は特に、事前（前日まで）に済ませておくことを強く推奨します。

## 6. 学習済み重みの事前ダウンロード（重要）

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

## 7. 事前に確認しておくこと

- **カメラのプライバシー設定**：Windowsの「設定 → プライバシーとセキュリティ → カメラ」で
  「デスクトップアプリがカメラにアクセスすることを許可する」がONになっているか確認してください。
  OFFのままだと `cv2.VideoCapture(0)` が映像を取得できません。
- **`DLL load failed` エラーが出た場合**：
  [Visual C++ 再頒布可能パッケージ](https://aka.ms/vs/17/release/vc_redist.x64.exe) を導入してください。
- **Webカメラが複数ある場合**：各プログラムの `CONFIG` 内 `CAMERA_ID` を `0` → `1`, `2`… と変更してください。

## 8. 動作確認

セットアップが終わったら、順番に実行して動くことを確認してください（詳しい使い方は [README.md](README.md) 参照）。
`(.venv)` が表示された状態のまま実行してください。

```bash
python 01_capture_augment.py
python 02_train.py
python 03_inference.py
```

---

## Raspberry Piの場合

手順は同じです（`winget`の代わりにRaspberry Pi OSに標準搭載のPython/Gitを使用）。
Raspberry Pi OSの「ターミナル」アプリ（画面上部のアイコン、黒い四角のアイコン）を開いて実行します。

```bash
git clone https://github.com/inspectlab7q/ai-inspection-training.git
cd ai-inspection-training
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

USB Webカメラを接続していれば、`03_inference.py` はPCと同じコードのまま動作します。
