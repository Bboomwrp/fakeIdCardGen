import os
import random
from PIL import Image
from visual_augmentation import apply_visual_augmentation

# ตั้งค่าพารามิเตอร์
INPUT_FOLDER = "output_fake_ids"
OUTPUT_FOLDER = "visual_augmented"
NUM_IMAGES = 7500  # จำนวนภาพที่ต้องการประมวลผล

# สร้างโฟลเดอร์ output ถ้ายังไม่มี
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# หาไฟล์ทั้งหมดใน input folder
image_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

if len(image_files) == 0:
    print(f"❌ ไม่พบไฟล์ในโฟลเดอร์ {INPUT_FOLDER}")
else:
    
    # ตรวจสอบ index ล่าสุดใน OUTPUT_FOLDER
    existing_aug_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.startswith("visual_aug_") and f.endswith(".jpg")]
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
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_index = start_index + i
        output_filename = f"visual_aug_{output_index:04d}.jpg"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        original = Image.open(input_path).convert("RGB")
        augmented = apply_visual_augmentation(original)
        augmented.save(output_path)

        print(f"✅ Saved: {output_path}")
