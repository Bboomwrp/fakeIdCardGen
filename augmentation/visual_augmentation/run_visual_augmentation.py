import os
import random
from PIL import Image
from visual_augmentation import apply_visual_augmentation


BASE_DIR = os.path.dirname(os.path.abspath(__file__))     
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..")) 
FAKE_GEN_DIR = os.path.join(PROJECT_ROOT, "fake_generator")  

REAL_INPUT_DIR = os.path.join(FAKE_GEN_DIR, "data", "Images")
FAKE_INPUT_DIR = os.path.join(FAKE_GEN_DIR, "data", "generated_dataset", "image")

REAL_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "fake_id_dataset", "real")
FAKE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "fake_id_dataset", "fake")

os.makedirs(REAL_OUTPUT_DIR, exist_ok=True)
os.makedirs(FAKE_OUTPUT_DIR, exist_ok=True)

NUM_IMAGES = 50  # จำนวนภาพที่ต้องการประมวลผล


def save_visual_aug(input_dir, output_dir, Type):

    # หาไฟล์ทั้งหมดใน input folder
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    if len(image_files) == 0:
        print(f"❌ ไม่พบไฟล์ในโฟลเดอร์ {input_dir}")
    else:
    
        # ตรวจสอบ index ล่าสุดใน OUTPUT_FOLDER
        existing_aug_files = [f for f in os.listdir(output_dir) if f.startswith("visual_aug_") and f.endswith(".jpg")]
        existing_indices = []

        for f in existing_aug_files:
            try:
                num = int(f.split("_")[2].split(".")[0])
                existing_indices.append(num)
            except:
                continue

        start_index = max(existing_indices) + 1 if existing_indices else 1
        # print(start_index)

        for i in range(NUM_IMAGES):
            filename = random.choice(image_files)  # ✅ ใช้รูปซ้ำได้
            input_path = os.path.join(input_dir, filename)
            output_index = start_index + i
            output_filename = f"visual_aug_{output_index:04d}_{Type}.jpg"
            output_path = os.path.join(output_dir, output_filename)

            original = Image.open(input_path).convert("RGB")
            augmented = apply_visual_augmentation(original)
            augmented.save(output_path)

            print(f"✅ Saved: {output_path}")

save_visual_aug(REAL_INPUT_DIR, REAL_OUTPUT_DIR, 'real')
save_visual_aug(FAKE_INPUT_DIR, FAKE_OUTPUT_DIR, 'fake')
