import os
import cv2
import random
from augmentation import data_aug, color_aug  # ✅ Import ฟังก์ชันจากอีกไฟล์

# ----- CONFIG -----
REAL_INPUT_DIR = "fake_generator/data/Images"
FAKE_INPUT_DIR = "fake_generator/data/generated_dataset/image"
REAL_OUTPUT_DIR = "fake_id_dataset/real"
FAKE_OUTPUT_DIR = "fake_id_dataset/fake"
os.makedirs(REAL_OUTPUT_DIR, exist_ok=True)
os.makedirs(FAKE_OUTPUT_DIR, exist_ok=True)

# ----- Techniques -----
data_techniques = ['rotation', 'shearing', 'scaling', 'translation']
color_techniques = ['blur', 'saturation', 'contrast', 'brightness']

# ----- Loop through all images -----
def save_augmentation(input_dir, output_dir):

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.png')):
            img_path = os.path.join(input_dir, filename)
            img = cv2.imread(img_path)

            if img is None:
                print(f"❌ Failed to load {filename}")
                continue

            # ----- Apply random data augmentation -----
            technique = random.choice(data_techniques)
            img_aug = data_aug(img.copy(), technique)

            # ----- Apply random color augmentation -----
            color = random.choice(color_techniques)
            img_aug = color_aug(img_aug, color)

            # ----- Save new image -----
            save_path = os.path.join(output_dir, f"aug_{technique}_{color}_{filename}")
            cv2.imwrite(save_path, img_aug)
            print(f"✅ Saved: {save_path}")

save_augmentation(REAL_INPUT_DIR, REAL_OUTPUT_DIR)
save_augmentation(FAKE_INPUT_DIR, FAKE_OUTPUT_DIR)
