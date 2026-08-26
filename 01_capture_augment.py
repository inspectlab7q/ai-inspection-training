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

# cv2をインポートする前に設定する必要がある（Windows特有のカメラ起動遅延対策）
# https://github.com/opencv/opencv/issues/17687
os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

import cv2
import numpy as np

# ==================== CONFIG（ここを変える） ====================
CAMERA_ID = 0                        # 使うカメラの番号。カメラが複数あるときは 1, 2… と変える
FRAME_WIDTH = 1280                   # カメラの取得解像度（幅）
FRAME_HEIGHT = 720                   # カメラの取得解像度（高さ）
CAMERA_FLIP = -1                     # カメラ映像の反転。None=反転なし / 0=上下反転 / 1=左右反転 / -1=上下左右反転
                                      # （カメラの取り付け向きに合わせて変える。03_inference.py と揃えること）
IMG_SIZE = (224, 224)                # 保存する画像のサイズ（02_train.py / 03_inference.py と揃える）
DATASET_DIR = "dataset/train"        # 画像の保存先ルート
ROI_CONFIG_PATH = "roi_config.json"  # 検査範囲(ROI)の保存先。03_inference.py と共有する
# ================================================================

GOOD_DIR = os.path.join(DATASET_DIR, "good")  # OK画像の保存先
BAD_DIR = os.path.join(DATASET_DIR, "bad")    # NG画像の保存先


def select_roi_live(cap, window_name="Select ROI"):
    """
    ライブ映像を見ながらマウスドラッグで範囲を選ばせる（cv2.selectROIは静止画1枚しか
    見せないため、ワークの位置合わせがしづらい問題への対応）。
    Enter/Spaceで確定、ESCでキャンセル。戻り値は (x, y, w, h) または None。
    """
    state = {"start": None, "end": None}

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            state["start"] = (x, y)
            state["end"] = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and state["start"] is not None:
            state["end"] = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            state["end"] = (x, y)

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse)

    print("マウスをドラッグして範囲を選択し、Enter（またはSpace）で確定、ESCでキャンセルしてください。")

    result = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[エラー] カメラからの映像取得に失敗しました。")
            break
        if CAMERA_FLIP is not None:
            frame = cv2.flip(frame, CAMERA_FLIP)

        display = frame.copy()
        if state["start"] and state["end"]:
            cv2.rectangle(display, state["start"], state["end"], (0, 255, 255), 2)
        cv2.putText(display, "ドラッグで範囲選択 → Enter/Space:確定  ESC:キャンセル",
                    (20, display.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow(window_name, display)
        key = cv2.waitKey(1) & 0xFF

        if key in (13, 32):  # Enter or Space
            if state["start"] and state["end"]:
                x1, y1 = state["start"]
                x2, y2 = state["end"]
                x, y = min(x1, x2), min(y1, y2)
                w, h = abs(x2 - x1), abs(y2 - y1)
                if w > 0 and h > 0:
                    result = (x, y, w, h)
                    break
        elif key == 27:  # ESC
            break

    cv2.destroyWindow(window_name)
    return result


def select_roi(cap):
    """マウスで検査範囲(ROI)を選択させ、roi_config.json に保存する（既存の設定があれば上書き）"""
    roi_rect = select_roi_live(cap)
    if roi_rect is None:
        print("[エラー] 検査範囲が選択されませんでした。")
        return None

    x, y, w, h = roi_rect
    roi = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
    with open(ROI_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(roi, f, ensure_ascii=False, indent=2)
    print(f"[情報] 検査範囲を {ROI_CONFIG_PATH} に保存しました: {roi}")

    return roi["x"], roi["y"], roi["w"], roi["h"]


def load_or_select_roi(cap):
    """
    roi_config.json があれば読み込み、なければライブ映像でマウス選択させて保存する。
    03_inference.py と同じファイルを共有するので、撮影時と同じ範囲で判定できる。
    """
    if os.path.exists(ROI_CONFIG_PATH):
        with open(ROI_CONFIG_PATH, "r", encoding="utf-8") as f:
            roi = json.load(f)
        return roi["x"], roi["y"], roi["w"], roi["h"]

    print(f"[情報] {ROI_CONFIG_PATH} が見つからないため、検査範囲を選択します。")
    roi = select_roi(cap)
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

        if CAMERA_FLIP is not None:
            frame = cv2.flip(frame, CAMERA_FLIP)

        # 保存用のROI画像は、枠や文字を描画する前のきれいな映像から切り出す
        roi_image = frame[y:y + h, x:x + w].copy()

        good_count = count_images(GOOD_DIR)
        bad_count = count_images(BAD_DIR)

        # 画面表示用は別のコピーに描画する（frame自体には描画しない）
        display_frame = frame.copy()
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(display_frame, f"OK: {good_count}  NG: {bad_count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(display_frame, "O:OK保存  N:NG保存  R:範囲やり直し  ESC:終了", (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Capture", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key in (ord('o'), ord('O')):
            n = save_capture(roi_image, GOOD_DIR)
            print(f"[保存] OK画像を {n} 枚保存しました。")
        elif key in (ord('n'), ord('N')):
            n = save_capture(roi_image, BAD_DIR)
            print(f"[保存] NG画像を {n} 枚保存しました。")
        elif key in (ord('r'), ord('R')):
            new_roi = select_roi(cap)
            if new_roi is not None:
                x, y, w, h = new_roi
        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"完了。OK: {count_images(GOOD_DIR)}枚 / NG: {count_images(BAD_DIR)}枚")


if __name__ == "__main__":
    main()
