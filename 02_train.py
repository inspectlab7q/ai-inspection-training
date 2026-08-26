"""
[2] 学習プログラム (02_train.py)

01_capture_augment.py で保存した画像を使って、OK/NG判定モデルを学習し、
Raspberry Piでも動く TFLite 形式で保存する。
"""

import os
import sys

import tensorflow as tf
from tensorflow.keras import layers, models

# ==================== CONFIG（ここを変える） ====================
DATASET_DIR = "dataset/train"      # 01_capture_augment.py が保存した画像のフォルダ（good/bad）
IMG_SIZE = (224, 224)              # モデルの入力サイズ（01_capture_augment.py / 03_inference.py と揃える）
BATCH_SIZE = 16
EPOCHS = 10                        # 学習の繰り返し回数。増やすほど精度は上がるが時間もかかる
VALIDATION_SPLIT = 0.2             # 検証用に取り分けるデータの割合
MODEL_DIR = "model"
MODEL_KERAS_PATH = os.path.join(MODEL_DIR, "model.keras")
MODEL_TFLITE_PATH = os.path.join(MODEL_DIR, "model.tflite")  # 03_inference.py が読み込むファイル
# ================================================================


def build_datasets():
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=VALIDATION_SPLIT,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="binary",
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=VALIDATION_SPLIT,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="binary",
    )

    # フォルダ名はアルファベット順にクラス番号が振られる: bad=0, good=1
    class_names = train_ds.class_names
    print(f"[情報] クラス割り当て: {class_names} (0={class_names[0]}, 1={class_names[1]})")
    if class_names != ["bad", "good"]:
        print(f"[警告] フォルダ名は 'good'/'bad' を想定しています（検出: {class_names}）。")

    normalize = layers.Rescaling(1.0 / 255)
    train_ds = train_ds.map(lambda x, y: (normalize(x), y)).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (normalize(x), y)).prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds


def build_model():
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=IMG_SIZE + (3,), include_top=False, weights="imagenet"
    )
    base_model.trainable = False  # ベースモデルは凍結（学習しない）→ 少ない画像枚数でも学習できる

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(1, activation="sigmoid"),  # OK/NGの2クラス分類（1に近いほどOK）
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def convert_to_tflite(model, output_path):
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open(output_path, "wb") as f:
        f.write(tflite_model)
    print(f"[情報] TFLiteモデルを保存しました: {output_path}")


def main():
    good_dir = os.path.join(DATASET_DIR, "good")
    bad_dir = os.path.join(DATASET_DIR, "bad")
    if not os.path.isdir(good_dir) or not os.path.isdir(bad_dir):
        print(f"[エラー] {good_dir} と {bad_dir} が見つかりません。")
        print("先に 01_capture_augment.py でOK/NG画像を撮影してください。")
        sys.exit(1)

    os.makedirs(MODEL_DIR, exist_ok=True)

    train_ds, val_ds = build_datasets()

    model = build_model()
    model.summary()

    print(f"[情報] 学習を開始します（epochs={EPOCHS}）...")
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

    loss, accuracy = model.evaluate(val_ds)
    print(f"[情報] 検証結果: Loss={loss:.4f}, Accuracy={accuracy:.4f}")

    model.save(MODEL_KERAS_PATH)
    print(f"[情報] モデルを保存しました: {MODEL_KERAS_PATH}")

    convert_to_tflite(model, MODEL_TFLITE_PATH)

    print("完了。03_inference.py で判定を確認してください。")


if __name__ == "__main__":
    main()
