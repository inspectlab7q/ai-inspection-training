# AI外観検査 実践講習プログラム

初めて開発に携わる方向けの「AI外観検査 実践講習」で使用するプログラム一式です。
持参いただいたワーク（検査対象物）を撮影し、OK/NG判定モデルを作成、PCとRaspberry Piの両方で判定を再現します。

## プログラム構成（予定）

| ファイル | 役割 | 状態 |
|---|---|---|
| `01_capture_augment.py` | ワークを撮影し、画像を水増しして保存 | 未着手 |
| `02_train.py` | 保存した画像でOK/NG判定モデルを学習 | 未着手 |
| `03_inference.py` | 学習済みモデルでリアルタイム判定（PC / Raspberry Pi 共通） | 作成済み |

## 環境構築

```bash
pip install -r requirements.txt
```

Raspberry Pi（64bit OS）でも同じコマンドで導入できます。

## 使い方（03_inference.py）

1. `02_train.py` で作成した `model/model.tflite` を用意する
2. `python 03_inference.py` を実行
3. 初回はマウスで検査範囲（ROI）をドラッグ選択し、Enterで確定
   - 選択した範囲は `roi_config.json` に保存され、次回以降は自動で読み込まれる
4. ESCキーで終了

## コードの中で変えてよい場所

`03_inference.py` の先頭にある `CONFIG` ブロックだけで、多くの現場差分に対応できます。

| 変数 | 内容 |
|---|---|
| `MODEL_PATH` | 学習済みモデルのパス |
| `CAMERA_ID` | 使用するカメラ番号（複数カメラがある場合） |
| `THRESHOLD` | OK/NG判定のしきい値（0〜1） |
| `FRAME_WIDTH` / `FRAME_HEIGHT` | カメラの取得解像度 |

---
このリポジトリは講習準備のため作成中です。
