from PIL import Image, ImageDraw, ImageFont
from faker import Faker
import os
import random
import requests
from io import BytesIO
from IPython.display import display
import csv
import numpy as np
import textwrap
from deep_translator import GoogleTranslator
from pythainlp.transliterate import romanize

# ----- CONFIG -----
TEMPLATE_PATH = "thai_id_template.png"
FONT_PATH = "THSarabun.ttf"
#FONT_PATH = "Sarabun-Bold.ttf"
FACE_DIR = "faces"  # ใช้ไฟล์ภาพในโฟลเดอร์นี้ หรือดึงจากเว็บ
OUTPUT_DIR = "output_fake_ids"
NUM_CARDS = 111  # จำนวนภาพที่จะสร้าง
IMG_SIZE = (640, 413)  # ขนาดบัตร

# ----- INITIAL -----
os.makedirs(OUTPUT_DIR, exist_ok=True)
fake = Faker('th_TH')
font_bold = ImageFont.truetype(FONT_PATH, 30)
font_medium = ImageFont.truetype(FONT_PATH, 24)
font_small = ImageFont.truetype(FONT_PATH, 20)

# ----- HELPER: Fake 13-digit ID -----
def generate_id_number():
    nums = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(11)]
    checksum = (11 - sum([x * (13 - i) for i, x in enumerate(nums)]) % 11) % 10
    return '{} {}{}{}{} {}{}{}{}{} {}{} {}'.format(*map(str, nums + [checksum]))

# ----- HELPER: โหลดภาพใบหน้าคนปลอม -----
def get_random_face(gender: str):
    face_candidates = []

    # โหลดข้อมูลจาก CSV
    with open(os.path.join(FACE_DIR, 'faces_list.csv'), newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['gender'] == gender:
                face_candidates.append(row['filename'])

    if face_candidates:
        chosen_file = random.choice(face_candidates)
        face_path = os.path.join(FACE_DIR, chosen_file)
        face = Image.open(face_path).convert("RGB")
    else:
        # fallback ถ้าไม่มีภาพเพศตรง
        print(f"No local face images found for gender: {gender}, downloading from internet...")
        response = requests.get("https://thispersondoesnotexist.com", timeout=10)
        face = Image.open(BytesIO(response.content)).convert("RGB")

    return face.resize((117, 137))

def generate_card_serial_number_full():
    # รหัสหน่วยงานที่ออกบัตร: 1000–1299
    office_code = random.randint(1000, 1299)

    # รหัสสาขาหรือรหัสย่อย: 00–99
    subcode = random.randint(0, 99)

    # เลขทะเบียนบัตร: 00000000–99999999
    serial_number = random.randint(0, 99999999)

    # รวมรหัสเป็นรูปแบบ XXXX-XX-XXXXXXXX
    return f"{office_code:04d}-{subcode:02d}-{serial_number:08d}"

def safe_romanize(word):
    try:
        return romanize(word).capitalize()
    except Exception as e:
        print(f"⚠️ Romanize error on '{word}': {e}")
        return "Unknown"

# ----- วาดบัตรประชาชนปลอม -----
def draw_fake_id(index):
    card = Image.open(TEMPLATE_PATH).convert("RGB").resize(IMG_SIZE)
    draw = ImageDraw.Draw(card)

    # ข้อมูลปลอม
    id_number = generate_id_number()

    gender = random.choice(['male', 'female'])
    
    if gender == 'male':
        prefix_th = "นาย"
        prefix_en = "Mr."
        full_name_th = fake.name_male()
    elif gender == 'female':
        prefix_th = random.choice(["นาง", "นางสาว"])
        prefix_en = "Mrs."
        full_name_th = fake.name_female()    
    name_th = f"{prefix_th} {full_name_th}"

    # name_en = fake.first_name().upper()
    # surname_en = fake.last_name().upper()
    name_parts = full_name_th.strip().split()
    if len(name_parts) >= 2:
        first_th = name_parts[0]
        last_th = name_parts[1]
    else:
        first_th = name_th
        last_th = ""

    name_en = romanize(first_th).capitalize()
    surname_en = romanize(last_th).capitalize()
    name_en = f"{prefix_en} {name_en}"

    dob = fake.date_of_birth(minimum_age=18, maximum_age=60)
    dob_str_th = dob.strftime("%d %b")
    thai_months = {
        "Jan": "ม.ค.", "Feb": "ก.พ.", "Mar": "มี.ค.",
        "Apr": "เม.ย.", "May": "พ.ค.", "Jun": "มิ.ย.",
        "Jul": "ก.ค.", "Aug": "ส.ค.", "Sep": "ก.ย.",
        "Oct": "ต.ค.", "Nov": "พ.ย.", "Dec": "ธ.ค."
    }
    for eng, thai in thai_months.items():
        dob_str_th = dob_str_th.replace(eng, thai)

    buddhist_year = dob.year + 543
    dob_str_th += f" {buddhist_year}"
    dob_str_en = dob.strftime("%d %b %Y")
    
    address = fake.address().replace('\n', ' ')
    wrapped = textwrap.wrap(address, width=38)  # ปรับ width ตามตำแหน่งแนวนอนที่ไม่ชนรูป

    # ----- วาดข้อความ -----
    draw.text((300, 70), id_number, font=font_bold, fill=(0, 0, 139))                    # เลขบัตร
    draw.text((215, 107), name_th, font=font_bold, fill=(0, 0, 0))                     # ชื่อ นามสกุล
    draw.text((265, 137), f"{name_en}", font=font_medium, fill=(0, 0, 139))          # ชื่ออังกฤษ
    draw.text((294, 160), f"{surname_en}", font=font_medium, fill=(0, 0, 139))  # นามสกุลอังกฤษ
    draw.text((285, 183), f"{dob_str_th}", font=font_medium, fill=(0, 0, 0)) # วันเกิดไทย
    draw.text((322, 206), f"{dob_str_en}", font=font_medium, fill=(0, 0, 139)) # วันเกิดEng
    draw.text((145, 257), wrapped[0], font=font_medium, fill=(0, 0, 0)) # ที่อยู่
    # draw.text((112, 280), wrapped[1], font=font_medium, fill=(0, 0, 0))
    if len(wrapped) > 1:
        draw.text((112, 280), wrapped[1], font=font_medium, fill=(0, 0, 0))

    # ----- ใส่รูปหน้าคน (พร้อมพื้นหลังเส้นวัด) -----
    face_img = get_random_face(gender)
    # bg_height = create_height_background()
    # bg_height.paste(face_img, (0, 0))
    card.paste(face_img, (461, 197))

    draw.text((461, 332), generate_card_serial_number_full(), font=font_small, fill="black")

    # ----- Save -----
    out_path = os.path.join(OUTPUT_DIR, f"thai_id_{index+396:03}.jpg")
    card.save(out_path)
    print(f"✅ Created: {out_path}")

# ----- Run -----
for i in range(NUM_CARDS):
    draw_fake_id(i)

#draw_fake_id(1)

# img = get_random_face_with_background()
# img.show()
# print(face.size)