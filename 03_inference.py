"""
[3] 推論プログラム (03_inference.py)

学習済みモデルを使って、Webカメラ映像からOK/NG判定を行う。
Windows PCでもRaspberry Piでも、CONFIGの値を変えるだけで同じコードが動く。

事前準備:
  - 02_train.py で作成したモデル (model/model.tflite) が必要
  - 検査範囲(ROI)が未設定の場合は、起動時にマウスで範囲を選択する
"""

import json
import os
import sys

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
ROI_CONFIG_PATH = "roi_config.json"  # 検査範囲(ROI)の保存先。01_capture_augment.py と共有する
# ================================================================


def load_interpreter(model_path):
    """TFLiteモデルを読み込む"""
    if not os.path.exists(model_path):
        print(f"[エラー] モデルファイルが見つかりません: {model_path}")
        print("先に 02_train.py を実行してモデルを作成してください。")
        sys.exit(1)
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


def load_or_select_roi(cap):
    """
    roi_config.json があれば読み込み、なければ最初のフレームでマウス選択させて保存する。
    01_capture_augment.py と同じファイルを共有するので、撮影時と同じ範囲で判定できる。
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

    print("マウスで検査範囲をドラッグして選択し、Enter（またはSpace）で確定してください。")
    x, y, w, h = cv2.selectROI("Select ROI", frame, showCrosshair=True)
    cv2.destroyWindow("Select ROI")

    if w == 0 or h == 0:
        print("[エラー] 検査範囲が選択されませんでした。プログラムを終了します。")
        sys.exit(1)

    roi = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
    with open(ROI_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(roi, f, ensure_ascii=False, indent=2)
    print(f"[情報] 検査範囲を {ROI_CONFIG_PATH} に保存しました: {roi}")

    return roi["x"], roi["y"], roi["w"], roi["h"]


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

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[エラー] カメラからの映像取得に失敗しました。")
            break

        roi_image = frame[y:y + h, x:x + w]
        score = predict(interpreter, roi_image)
        is_ok = score > THRESHOLD
        label = f"OK {score:.2f}" if is_ok else f"NG {score:.2f}"
        color = (0, 200, 0) if is_ok else (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
        cv2.putText(frame, label, (x, max(y - 15, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        cv2.imshow("AI Inspection", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
