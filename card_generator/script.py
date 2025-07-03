import json
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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DATA = os.path.join(BASE_DIR, "..", "fake_generator", "data")
OUTPUT_DATA = os.path.abspath(OUTPUT_DATA) 

OUTPUT_DIR = os.path.join(OUTPUT_DATA, "Images")
OUTPUT_JSON = os.path.join(OUTPUT_DATA, "Annotations")
NUM_CARDS = 50  # จำนวนภาพที่จะสร้าง
IMG_SIZE = (640, 413)  # ขนาดบัตร

ID_NUMBER = []
NAME_TH = []
NAME_EN = []
SURNAME_EN = []
DOB_TH = []
DOB_EN = []
ADDRESS_1 = []
ADDRESS_2 = []
SERIAL_NUM = []

# ----- INITIAL -----
os.makedirs(OUTPUT_DATA, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_JSON, exist_ok=True)

fake = Faker('th_TH')
font_bold = ImageFont.truetype(FONT_PATH, 30)
font_medium = ImageFont.truetype(FONT_PATH, 24)
font_small = ImageFont.truetype(FONT_PATH, 20)

existing_files = [
    f for f in os.listdir(OUTPUT_DIR) 
    if f.startswith("thai_id_") and f.endswith(".jpg")
]
existing_indices = []
for f in existing_files:
    try:
        index = int(f.split("_")[2].split(".")[0])
        existing_indices.append(index)
    except:
        pass

start_index = max(existing_indices) + 1 if existing_indices else 0

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
    if not word:
        return ""
    try:
        return romanize(word, engine="thai2rom").capitalize()
    except Exception:
        return ""

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
        full_name_th = fake.name_male().replace("ด.ช.", "")
    elif gender == 'female':
        prefix_th = random.choice(["นาง", "นางสาว"])
        prefix_en = "Mrs."
        full_name_th = fake.name_female().replace("ด.ญ.", "")    
    name_th = f"{prefix_th} {full_name_th}"

    # name_en = fake.first_name().upper()
    # surname_en = fake.last_name().upper()
    name_parts = full_name_th.strip().split()
    if len(name_parts) >= 2:
        first_th = name_parts[0]
        last_th = name_parts[1]
    else:
        first_th = name_parts[0]
        last_th = ""

    # name_en = romanize(first_th).capitalize()
    # surname_en = romanize(last_th).capitalize()
    # name_en = f"{prefix_en} {name_en}"

    name_en_part = safe_romanize(first_th)
    surname_en = safe_romanize(last_th)
    name_en = f"{prefix_en} {name_en_part}"

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

    serial_number = generate_card_serial_number_full()
    draw.text((461, 332), serial_number, font=font_small, fill="black")

    ID_NUMBER.append(id_number)
    NAME_TH.append(name_th)
    NAME_EN.append(name_en)
    SURNAME_EN.append(surname_en)
    DOB_TH.append(dob_str_th)
    DOB_EN.append(dob_str_en)
    ADDRESS_1.append(wrapped[0])

    if len(wrapped) > 1:
        ADDRESS_2.append(wrapped[1])
    else:
        ADDRESS_2.append('')

    SERIAL_NUM.append(serial_number)

    # ----- Save -----
    out_path = os.path.join(OUTPUT_DIR, f"thai_id_{start_index + index:04}.jpg")
    card.save(out_path)
    print(f"✅ Created: {out_path}")

# ----- สร้าง metadata json เพื่อใช้สร้างการปลอม -----
def generate_card_metadata(id_number, name_th, name_en, surname_en, dob_th, dob_en, address_1, address_2, serial_num):
    card_data = {
        "id_number": {
            "value": id_number, 
            "quad": [[300, 78], [470, 78], [470, 100], [300, 100]]
        },
        "name_th": {
            "value": name_th,
            "quad": [[215, 105], [520, 105], [520, 140], [215, 140]]
        },
        "name_en": {
            "value": name_en,
            "quad": [[265, 142], [415, 142], [415, 163], [265, 163]]
        },
        "surname_en": {
            "value": surname_en,
            "quad": [[294, 163], [460, 163], [460, 186], [294, 186]]
        },
        "dob_th": {
            "value": dob_th,
            "quad": [[285, 187], [390, 187], [390, 207], [285, 207]]
        },
        "dob_en": {
            "value": dob_en,
            "quad": [[322, 211], [430, 211], [430, 233], [322, 233]]
        },
        "address_1": {
            "value": address_1,
            "quad": [[145, 255], [425, 255], [425, 285], [145, 285]]
        },
        "address_2": {
            "value": address_2,
            "quad": [[112, 279], [375, 279], [375, 307], [112, 307]]
        },
        "serial_number": {
            "value": serial_num,
            "quad": [[461, 337], [585, 337], [585, 350], [461, 350]]
        }
    }
    return card_data

# ----- Run -----
for i in range(NUM_CARDS):
    draw_fake_id(i)
    card_metadata = generate_card_metadata(ID_NUMBER[i], NAME_TH[i], NAME_EN[i], SURNAME_EN[i], DOB_TH[i], DOB_EN[i], ADDRESS_1[i], ADDRESS_2[i], SERIAL_NUM[i])
    
    json_filename = f"card_{i+1:04}.json" 
    json_filepath = os.path.join(OUTPUT_JSON, json_filename)

    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(card_metadata, f, ensure_ascii=False, indent=4)

    print(f"✅ Generated metadata json: {json_filename}")

#draw_fake_id(1)
# print(start_index)
# img = get_random_face_with_background()
# img.show()
# print(face.size)