# セットアップ手順（Windows PC）

このリポジトリはPublicなので、GitHubアカウントは不要です。
**Python** と **Git** の2つを導入すれば、講習当日でも、持ち帰った後の会社PCでも同じ手順で使えます。

## 1. Pythonのインストール

インストーラー実行時、最初の画面で **「Add python.exe to PATH」に必ずチェック** を入れてください。

```bash
winget install --id Python.Python.3.11 -e
```

（winget が使えない場合は [python.org](https://www.python.org/downloads/) から3.11系をダウンロード）

## 2. Gitのインストール

```bash
winget install --id Git.Git -e
```

インストール後、一度ターミナル（コマンドプロンプトやPowerShell）を閉じて開き直してください。

## 3. プログラムの取得

```bash
git clone https://github.com/inspectlab7q/ai-inspection-training.git
cd ai-inspection-training
```

## 4. ライブラリの導入

```bash
pip install -r requirements.txt
```

インストールには数分かかります。ネット回線が遅い場合は特に、事前（前日まで）に済ませておくことを強く推奨します。

## 5. 事前に確認しておくこと

- **カメラのプライバシー設定**：Windowsの「設定 → プライバシーとセキュリティ → カメラ」で
  「デスクトップアプリがカメラにアクセスすることを許可する」がONになっているか確認してください。
  OFFのままだと `cv2.VideoCapture(0)` が映像を取得できません。
- **`DLL load failed` エラーが出た場合**：
  [Visual C++ 再頒布可能パッケージ](https://aka.ms/vs/17/release/vc_redist.x64.exe) を導入してください。
- **Webカメラが複数ある場合**：各プログラムの `CONFIG` 内 `CAMERA_ID` を `0` → `1`, `2`… と変更してください。

## 6. 動作確認

セットアップが終わったら、順番に実行して動くことを確認してください（詳しい使い方は [README.md](README.md) 参照）。

```bash
python 01_capture_augment.py
python 02_train.py
python 03_inference.py
```

---

## Raspberry Piの場合

手順は同じです（`winget`の代わりにRaspberry Pi OSに標準搭載のPython/Gitを使用）。

```bash
git clone https://github.com/inspectlab7q/ai-inspection-training.git
cd ai-inspection-training
pip install -r requirements.txt
```

USB Webカメラを接続していれば、`03_inference.py` はPCと同じコードのまま動作します。
