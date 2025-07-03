import os
import cv2
import random
from augmentation import data_aug, color_aug

# ----- CONFIG -----
INPUT_DIR = "output_fake_ids"
OUTPUT_DIR = "augmented_fake_ids"
NUMBER = 7500

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----- Techniques -----
data_techniques = ['rotation', 'shearing', 'scaling', 'translation']
color_techniques = ['blur', 'saturation', 'contrast', 'brightness']

# ----- Get all image filenames -----
all_images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.png'))]

# ----- Find start index -----
existing_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("aug_")]
existing_indices = []

for f in existing_files:
    try:
        idx = int(f.split("_")[1].split(".")[0])
        existing_indices.append(idx)
    except:
        continue

start_idx = max(existing_indices, default=-1) + 1

# print(existing_indices)

# loop augmentation
for i in range(NUMBER):
    filename = random.choice(all_images)
    img_path = os.path.join(INPUT_DIR, filename)
    img = cv2.imread(img_path)

    if img is None:
        print(f"❌ Failed to load {filename}")
        continue

    # technique = random.choice(['rotation', 'shearing', 'scaling', 'translation'])
    # color = random.choice(['blur', 'saturation', 'contrast', 'brightness'])

    # img_aug = data_aug(img.copy(), technique)
    # img_aug = color_aug(img_aug, color)

    # ✅ ใช้ 1–3 data_techniques แบบสุ่ม
    for tech in random.sample(data_techniques, random.randint(1, 3)):
        img = data_aug(img, tech)

    # ✅ ใช้ 1–2 color_techniques แบบสุ่ม
    for color in random.sample(color_techniques, random.randint(1, 2)):
        img = color_aug(img, color)

    save_path = os.path.join(
        OUTPUT_DIR,
        f"aug_{start_idx + i:04}.jpg"
    )
    cv2.imwrite(save_path, img)
    print(f"✅ Saved: {save_path}")

# ----- Loop through all images -----
# for filename in os.listdir(INPUT_DIR):
#     if filename.lower().endswith(('.jpg', '.png')):
#         img_path = os.path.join(INPUT_DIR, filename)
#         img = cv2.imread(img_path)

#         if img is None:
#             print(f"❌ Failed to load {filename}")
#             continue

#         # ----- Apply random data augmentation -----
#         technique = random.choice(data_techniques)
#         img_aug = data_aug(img.copy(), technique)

#         # ----- Apply random color augmentation -----
#         color = random.choice(color_techniques)
#         img_aug = color_aug(img_aug, color)

#         # ----- Save new image -----
#         save_path = os.path.join(OUTPUT_DIR, f"aug_{technique}_{color}_{filename}")
#         cv2.imwrite(save_path, img_aug)
#         print(f"✅ Saved: {save_path}")