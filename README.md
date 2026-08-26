# AI外観検査 実践講習プログラム

初めて開発に携わる方向けの「AI外観検査 実践講習」で使用するプログラム一式です。
持参いただいたワーク（検査対象物）を撮影し、OK/NG判定モデルを作成、PCとRaspberry Piの両方で判定を再現します。

## プログラム構成

| ファイル | 役割 | 状態 |
|---|---|---|
| `01_capture_augment.py` | ワークを撮影し、画像を水増しして保存 | 作成済み |
| `02_train.py` | 保存した画像でOK/NG判定モデルを学習 | 作成済み |
| `03_inference.py` | 学習済みモデルでリアルタイム判定（PC / Raspberry Pi 共通） | 作成済み |

3つとも先頭に `CONFIG` ブロックがあり、現場ごとに変える値はそこにまとまっている。

## 環境構築

初めてこのPCで使う場合は [SETUP.md](SETUP.md)（Python・Gitのインストールから`git clone`まで）を参照。

導入済みの環境では、リポジトリ直下で以下を実行するだけでよい。

```bash
pip install -r requirements.txt
```

Raspberry Pi（64bit OS）でも同じコマンドで導入できる。

## 使い方（当日の流れ）

### 1. 撮影・水増し保存（`01_capture_augment.py`）

```bash
python 01_capture_augment.py
```

- 初回起動時にマウスで検査範囲（ROI）をドラッグ選択し、Enterで確定
  - 選択した範囲は `roi_config.json` に保存され、`03_inference.py` と共有される
- ワークをカメラに映し、`O`キーでOK（良品）、`N`キーでNG（不良品）として保存
  - 1回の撮影につき、回転・明るさ・コントラスト・反転・ノイズを加えた画像が自動生成され、`dataset/train/good` または `dataset/train/bad` にまとめて保存される
  - 画面上部にOK/NGそれぞれの保存枚数が表示される
- 検査範囲を選び間違えたときは `R`キー でいつでも選び直せる（`roi_config.json`が上書きされる）
- `ESC`キーで終了

### 2. 学習（`02_train.py`）

```bash
python 02_train.py
```

- `dataset/train/good`・`dataset/train/bad` の画像を使ってモデルを学習
- 学習済みモデルを `model/model.keras`（Keras形式）と `model/model.tflite`（軽量形式）として保存
- `model/model.tflite` を `03_inference.py` が読み込む

### 3. 推論（`03_inference.py`）

```bash
python 03_inference.py
```

- `model/model.tflite` を読み込み、カメラ映像上にOK/NGとスコアをリアルタイム表示
- `ESC`キーで終了
- **PCでもRaspberry Piでも同じコードがそのまま動く**（USB Webカメラ使用を前提）

## コードの中で変えてよい場所（CONFIG）

| ファイル | 変数 | 内容 |
|---|---|---|
| 共通 | `CAMERA_ID` | 使用するカメラ番号（複数カメラがある場合は 1, 2… に変更） |
| 共通 | `IMG_SIZE` | モデルの入力サイズ（3ファイルで揃える必要あり。基本は変更不要） |
| `01_capture_augment.py` | `DATASET_DIR` | 撮影画像の保存先 |
| `02_train.py` | `EPOCHS` | 学習の繰り返し回数（増やすと精度は上がるが時間もかかる） |
| `02_train.py` | `VALIDATION_SPLIT` | 検証用に取り分けるデータの割合 |
| `03_inference.py` | `MODEL_PATH` | 学習済みモデルのパス |
| `03_inference.py` | `THRESHOLD` | OK/NG判定のしきい値（0〜1、大きいほどOK判定が厳しくなる） |

## 注意点

- `roi_config.json`・`dataset/`・`model/` は現場ごとに生成される個別データのため、Gitでは管理しない（`.gitignore`済み）
- Raspberry Piに移植する際は、このリポジトリを `git clone`（またはPCから転送）し、同じ手順で `pip install -r requirements.txt` を実行する
