"""
[3] 推論プログラム (03_inference.py)

学習済みモデルを使って、Webカメラ映像からOK/NG判定を行う。
Windows PCでもRaspberry Piでも、CONFIGの値を変えるだけで同じコードが動く。

事前準備:
  - 02_train.py で作成したモデル (model/model.tflite) が必要
  - 検査範囲(ROI)が未設定の場合は、起動時にマウスで範囲を選択する

操作方法:
  R キー : 検査範囲(ROI)を選び直す（PCから転送してカメラ位置が変わった場合など）
  ESC    : 終了
"""

import json
import os
import sys

# cv2をインポートする前に設定する必要がある（Windows特有のカメラ起動遅延対策）
# https://github.com/opencv/opencv/issues/17687
os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

import cv2
import numpy as np
import tensorflow as tf

# ==================== CONFIG（ここを変える） ====================
MODEL_PATH = "model/model.tflite"    # 学習済みモデルのパス（02_train.py が出力する）
CAMERA_ID = 0                        # 使うカメラの番号。カメラが複数あるときは 1, 2… と変える
IMG_SIZE = (224, 224)                # モデルの入力サイズ（02_train.py と合わせる。基本は変更不要）
THRESHOLD = 0.5                      # OK/NGの判定しきい値（0.0〜1.0）。大きくするほどOK判定が厳しくなる
FRAME_WIDTH = 1280                   # カメラの取得解像度（幅）
FRAME_HEIGHT = 720                   # カメラの取得解像度（高さ）
CAMERA_FLIP = -1                     # カメラ映像の反転。None=反転なし / 0=上下反転 / 1=左右反転 / -1=上下左右反転
                                      # （カメラの取り付け向きに合わせて変える。01_capture_augment.py と揃えること）
ROI_CONFIG_PATH = "roi_config.json"  # 検査範囲(ROI)の保存先。01_capture_augment.py と共有する
# ================================================================


def draw_text_clamped(img, text, x, y, font_scale=0.7, color=(255, 255, 255), thickness=2):
    """画面からはみ出さないように位置を自動調整してテキストを描画する"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    h, w = img.shape[:2]
    x = max(5, min(x, w - text_w - 5))
    y = max(text_h + 5, min(y, h - 5))
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness)


def load_interpreter(model_path):
    """TFLiteモデルを読み込む"""
    if not os.path.exists(model_path):
        print(f"[エラー] モデルファイルが見つかりません: {model_path}")
        print("先に 02_train.py を実行してモデルを作成してください。")
        sys.exit(1)
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


def select_roi_live(cap, window_name="Select ROI"):
    """
    ライブ映像を見ながら2回のクリックで範囲を選ばせる（cv2.selectROIは静止画1枚しか
    見せないため、ワークの位置合わせがしづらい問題への対応）。
    1回目のクリック=始点、マウスを動かすと範囲が追従、2回目のクリック=終点でロック。
    ロック後にもう一度クリックするとやり直せる。Enter/Spaceで確定、ESCでキャンセル。
    戻り値は (x, y, w, h) または None。
    """
    state = {"start": None, "end": None, "locked": False}

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if state["start"] is None or state["locked"]:
                # 1回目のクリック（またはロック後の再クリック）: 始点をセットしてやり直す
                state["start"] = (x, y)
                state["end"] = (x, y)
                state["locked"] = False
            else:
                # 2回目のクリック: 終点を確定してロックする
                state["end"] = (x, y)
                state["locked"] = True
        elif event == cv2.EVENT_MOUSEMOVE:
            if state["start"] is not None and not state["locked"]:
                state["end"] = (x, y)

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse)

    print("1回目クリック:始点 → マウス移動 → 2回目クリック:終点確定 → Enter/Spaceで選択確定、ESCでキャンセル。")
    print("（確定前ならもう一度クリックでやり直せます）")

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
            color = (0, 200, 0) if state["locked"] else (0, 255, 255)
            cv2.rectangle(display, state["start"], state["end"], color, 2)
        guide = "2nd click:end pt -> Enter/Space:OK" if state["locked"] else \
            "1st click:start  2nd click:end" if state["start"] is None else \
            "Move mouse, click to set end"
        draw_text_clamped(display, f"{guide}  ESC:Cancel", 20, display.shape[0] - 20, font_scale=0.6)

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
    01_capture_augment.py と同じファイルを共有するので、撮影時と同じ範囲で判定できる
    （PCで撮影しラズパイに転送した場合など、カメラの設置位置が変わったときはRキーで選び直せる）。
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


def predict(interpreter, roi_image):
    """ROI画像を判定し、OKらしさのスコア(0〜1)を返す"""
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    img = cv2.resize(roi_image, IMG_SIZE)
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    interpreter.set_tensor(input_details[0]["index"], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]["index"])
    return float(output[0][0])


def main():
    interpreter = load_interpreter(MODEL_PATH)

    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"[エラー] カメラ(ID={CAMERA_ID})を開けませんでした。CONFIGのCAMERA_IDを確認してください。")
        sys.exit(1)

    x, y, w, h = load_or_select_roi(cap)

    print("判定を開始します。終了するにはウィンドウを選んで ESC キーを押してください。")
    print("検査範囲がずれている場合は R キーで選び直せます。")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[エラー] カメラからの映像取得に失敗しました。")
            break

        if CAMERA_FLIP is not None:
            frame = cv2.flip(frame, CAMERA_FLIP)

        roi_image = frame[y:y + h, x:x + w]
        score = predict(interpreter, roi_image)
        is_ok = score > THRESHOLD
        label = f"OK {score:.2f}" if is_ok else f"NG {score:.2f}"
        color = (0, 200, 0) if is_ok else (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
        draw_text_clamped(frame, label, x, max(y - 15, 25), font_scale=1.0, color=color)

        cv2.imshow("AI Inspection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key in (ord('r'), ord('R')):
            new_roi = select_roi(cap)
            if new_roi is not None:
                x, y, w, h = new_roi

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
