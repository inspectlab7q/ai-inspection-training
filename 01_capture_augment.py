"""
[1] 撮影・水増し保存プログラム (01_capture_augment.py)

Webカメラでワークを撮影し、OK/NG別に画像を保存する。
1回の撮影ごとに複数パターンの画像（回転・明るさ・コントラスト・反転・ノイズ）を
自動生成して保存する（＝水増し／augmentation）ので、少ない撮影回数でも
学習に必要な枚数を確保できる。

操作方法:
  O キー : 今の映像を OK（良品）として保存
  N キー : 今の映像を NG（不良品）として保存
  R キー : 検査範囲(ROI)を選び直す（間違えたときはこれでやり直せる）
  ESC    : 終了

事前準備:
  - 検査範囲(ROI)が未設定の場合は、起動時にマウスで範囲を選択する
    （選択結果は roi_config.json に保存され、03_inference.py と共有する）
"""

import datetime
import json
import os
import random
import sys

import cv2
import numpy as np

# ==================== CONFIG（ここを変える） ====================
CAMERA_ID = 0                        # 使うカメラの番号。カメラが複数あるときは 1, 2… と変える
FRAME_WIDTH = 1280                   # カメラの取得解像度（幅）
FRAME_HEIGHT = 720                   # カメラの取得解像度（高さ）
IMG_SIZE = (224, 224)                # 保存する画像のサイズ（02_train.py / 03_inference.py と揃える）
DATASET_DIR = "dataset/train"        # 画像の保存先ルート
ROI_CONFIG_PATH = "roi_config.json"  # 検査範囲(ROI)の保存先。03_inference.py と共有する
# ================================================================

GOOD_DIR = os.path.join(DATASET_DIR, "good")  # OK画像の保存先
BAD_DIR = os.path.join(DATASET_DIR, "bad")    # NG画像の保存先


def select_roi(frame):
    """マウスで検査範囲(ROI)を選択させ、roi_config.json に保存する（既存の設定があれば上書き）"""
    print("マウスで検査範囲をドラッグして選択し、Enter（またはSpace）で確定してください。")
    print("（何も選択せずEnterを押すと選び直しになります）")
    x, y, w, h = cv2.selectROI("Select ROI", frame, showCrosshair=True)
    cv2.destroyWindow("Select ROI")

    if w == 0 or h == 0:
        print("[エラー] 検査範囲が選択されませんでした。")
        return None

    roi = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
    with open(ROI_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(roi, f, ensure_ascii=False, indent=2)
    print(f"[情報] 検査範囲を {ROI_CONFIG_PATH} に保存しました: {roi}")

    return roi["x"], roi["y"], roi["w"], roi["h"]


def load_or_select_roi(cap):
    """
    roi_config.json があれば読み込み、なければ最初のフレームでマウス選択させて保存する。
    03_inference.py と同じファイルを共有するので、撮影時と同じ範囲で判定できる。
    """
    if os.path.exists(ROI_CONFIG_PATH):
        with open(ROI_CONFIG_PATH, "r", encoding="utf-8") as f:
            roi = json.load(f)
        return roi["x"], roi["y"], roi["w"], roi["h"]

    print(f"[情報] {ROI_CONFIG_PATH} が見つからないため、検査範囲を選択します。")
    ret, frame = cap.read()
    if not ret:
        print("[エラー] カメラからの映像取得に失敗しました。")
        sys.exit(1)

    roi = select_roi(frame)
    if roi is None:
        print("[エラー] 検査範囲が選択されなかったため、プログラムを終了します。")
        sys.exit(1)

    return roi


# ---------- 画像を水増しするための変換関数 ----------

def rotate_image(image, angle):
    h, w = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)


def adjust_brightness(image, value):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.int16)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] + value, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def adjust_contrast(image, factor):
    return cv2.convertScaleAbs(image, alpha=factor, beta=0)


def add_noise(image, stddev=15):
    noise = np.random.normal(0, stddev, image.shape)
    noisy = np.clip(image.astype(np.float32) + noise, 0, 255)
    return noisy.astype(np.uint8)


def augment_image(image):
    """1枚の画像から、水増しした複数パターンの画像リストを作る"""
    variants = [image]  # 元画像
    variants.append(rotate_image(image, random.uniform(2, 5)))
    variants.append(rotate_image(image, -random.uniform(2, 5)))
    variants.append(adjust_brightness(image, 25))
    variants.append(adjust_brightness(image, -25))
    variants.append(adjust_contrast(image, 1.2))
    variants.append(adjust_contrast(image, 0.8))
    variants.append(cv2.flip(image, 1))  # 左右反転
    variants.append(add_noise(image))
    return variants


# ---------- 保存処理 ----------

def save_capture(roi_image, save_dir):
    """ROI画像を水増しし、まとめてフォルダに保存する"""
    os.makedirs(save_dir, exist_ok=True)
    roi_resized = cv2.resize(roi_image, IMG_SIZE)
    variants = augment_image(roi_resized)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
    for i, img in enumerate(variants):
        path = os.path.join(save_dir, f"{timestamp}_{i}.png")
        cv2.imwrite(path, img)

    return len(variants)


def count_images(folder):
    if not os.path.exists(folder):
        return 0
    return len([f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))])


def main():
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"[エラー] カメラ(ID={CAMERA_ID})を開けませんでした。CONFIGのCAMERA_IDを確認してください。")
        sys.exit(1)

    x, y, w, h = load_or_select_roi(cap)

    print("撮影を開始します。")
    print("  O キー: OK(良品)として保存 / N キー: NG(不良品)として保存 / R キー: 検査範囲を選び直す / ESC: 終了")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[エラー] カメラからの映像取得に失敗しました。")
            break

        good_count = count_images(GOOD_DIR)
        bad_count = count_images(BAD_DIR)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"OK: {good_count}  NG: {bad_count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, "O:OK保存  N:NG保存  R:範囲やり直し  ESC:終了", (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Capture", frame)

        key = cv2.waitKey(1) & 0xFF
        roi_image = frame[y:y + h, x:x + w]

        if key in (ord('o'), ord('O')):
            n = save_capture(roi_image, GOOD_DIR)
            print(f"[保存] OK画像を {n} 枚保存しました。")
        elif key in (ord('n'), ord('N')):
            n = save_capture(roi_image, BAD_DIR)
            print(f"[保存] NG画像を {n} 枚保存しました。")
        elif key in (ord('r'), ord('R')):
            new_roi = select_roi(frame)
            if new_roi is not None:
                x, y, w, h = new_roi
        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"完了。OK: {count_images(GOOD_DIR)}枚 / NG: {count_images(BAD_DIR)}枚")


if __name__ == "__main__":
    main()
