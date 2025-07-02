import os
import cv2
import random
from augmentation import data_aug, color_aug

# ----- CONFIG -----
INPUT_DIR = "output_fake_ids"
OUTPUT_DIR = "augmented_fake_ids"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----- Techniques -----
data_techniques = ['rotation', 'shearing', 'scaling', 'translation']
color_techniques = ['blur', 'saturation', 'contrast', 'brightness']

# ----- Loop through all images -----
for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(('.jpg', '.png')):
        img_path = os.path.join(INPUT_DIR, filename)
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
        save_path = os.path.join(OUTPUT_DIR, f"aug_{technique}_{color}_{filename}")
        cv2.imwrite(save_path, img_aug)
        print(f"✅ Saved: {save_path}")
