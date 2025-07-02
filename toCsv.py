import os
import csv
from deepface import DeepFace

# แปลงไฟล์ภาพใน /faces เป็น.csv แล้ว map ภาพและ gender

# ----- CONFIG -----
folder_path = 'C:/Users/Boom/projects/fakeidcardGen/faces'
csv_path = os.path.join(folder_path, 'faces_list.csv')

# ----- READ EXISTING CSV -----
existing_files = set()
if os.path.exists(csv_path):
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_files.add(row['filename'])

# ----- FIND NEW FILES -----
all_files = os.listdir(folder_path)
new_files = [f for f in all_files if f not in existing_files and f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# ----- WRITE NEW ENTRIES -----
with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    # เขียน header ถ้าไฟล์ว่าง
    if os.path.getsize(csv_path) == 0:
        writer.writerow(['filename', 'gender'])

    for file_name in sorted(new_files):
        file_path = os.path.join(folder_path, file_name)
        try:
            result = DeepFace.analyze(img_path=file_path, actions=['gender'], enforce_detection=False)
            gender = result[0]['dominant_gender'].lower()
            if gender == 'man':
                gender = 'male'
            elif gender == 'woman':
                gender = 'female'
        except Exception as e:
            print(f"❌ วิเคราะห์ {file_name} ไม่ได้: {e}")
            gender = 'unknown'

        writer.writerow([file_name, gender])
        print(f"✅ เพิ่ม: {file_name}, gender = {gender}")


print(f"🎉 เสร็จสิ้น! พบไฟล์ใหม่ทั้งหมด {len(new_files)} ไฟล์ และเพิ่มลงใน {csv_path}")
