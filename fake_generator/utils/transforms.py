from .util import *
from typing import *
import inspect
from PIL import ImageFont, ImageDraw, Image
import textwrap
from deep_translator import GoogleTranslator
from pythainlp.transliterate import romanize
from faker import Faker

import random
import copy
import cv2
import names

from utils import util as ut
import numpy as np


def inpaint_image(img: np.ndarray, coord:np.ndarray, mask: np.ndarray,field_name:str, text_str: str):
    
    inpaint = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    fake_text_image = copy.deepcopy(inpaint)
    x0, y0, w, h = coord
   
    color = (0, 0, 0) 

    if field_name in ['name_en', 'surname_en', 'dob_en', 'id_number']:
        color = (24, 18, 187)
    else:
        color = (0, 0, 0)   

    if field_name in ['name_th', 'id_number']:
        font_size = 29
    elif field_name == 'serial_number':
        font_size = 19
    else:
        font_size = 24

    font = ImageFont.truetype("THSarabun.ttf", font_size)

    img_pil = Image.fromarray(fake_text_image)
    draw = ImageDraw.Draw(img_pil)
    draw.text(((x0, y0)), text_str, font=font, fill=color)
    fake_text_image = np.array(img_pil)

    return fake_text_image


def crop_replace(im_a: np.ndarray, im_b: np.ndarray, coord_a: np.ndarray, H: np.matrix, dx1: int, dy1: int, dx2: int, dy2: int):
    dim_issue = False
    mask_a = np.zeros_like(im_a)
    cv2.drawContours(mask_a, [coord_a.astype(int)], -1, color=(255, 255, 255), thickness=cv2.FILLED)
    y_a, x_a = np.where((mask_a[..., 0] / 255).astype(int) == 1)

    coordh_a = np.ones((3, len(x_a)), dtype=np.float32())
    coordh_a[0, :] = x_a
    coordh_a[1, :] = y_a

    coordh_b = H @ coordh_a
    coordh_b = coordh_b / coordh_b[-1, ...]

    x_b = coordh_b.T[:, 0].astype(int)
    y_b = coordh_b.T[:, 1].astype(int)

    im_rep = copy.deepcopy(im_b)

    try:
        im_rep[y_b + dy1, x_b + dx1, ...] = im_a[y_a + dy2, x_a + dx2, ...]
    except Exception as e:
        dim_issue = True

    return im_rep, dim_issue


# Functions for forgery on-the-fly
def copy_paste(image:np.ndarray, coord_a:List[int], coord_b:List[int], shift_copy:int) -> Tuple[np.ndarray, bool]:

    im_rep = copy.deepcopy(image)
    r_noise = random.randint(5, shift_copy)

    x1, y1, w1, h1 = coord_a
    source = image[y1:y1 + h1, x1:x1 + w1]
    x2, y2, w2, h2 = coord_b

    try:
        im_rep[y2 + r_noise:y2 + r_noise + h1, x2 + r_noise:x2 + r_noise + w1] = source
        dim_issue = False
    except:
        dim_issue = True
        print('COPY PASTE ERROR')

    return im_rep, dim_issue

def copy_paste_on_document(im_a, coord_a, coord_b, shift_copy):

    im_rep = copy.deepcopy(im_a)
    r_noise = random.randint(5,shift_copy)
    
    x1, y1, w1, h1 = coord_a['x'], coord_a['y'], coord_a['width'], coord_a['height']
    source = im_a[y1:y1+h1, x1:x1+w1]
    
    x2, y2, w2, h2 = coord_b['x'], coord_b['y'], coord_b['width'], coord_b['height']
    
    try:
        im_rep[y2 + r_noise:y2 + r_noise + h1, x2 + r_noise:x2 + r_noise + w1] = source
        dim_issue = False
    except:
        dim_issue = True
        print('COPY PASTE ERROR')

    
    return im_rep, dim_issue

def copy_paste_on_two_documents(im_a, coord_a, im_b, coord_b, shift_crop):

    im_rep = copy.deepcopy(im_a)
    r_noise = random.randint(5,shift_crop)
    
    x1, y1, w1, h1 = coord_b['x'], coord_b['y'], coord_b['width'], coord_b['height']
    source = im_b[y1:y1+h1, x1:x1+w1]
    
    x2, y2, w2, h2 = coord_a['x'], coord_a['y'], coord_a['width'], coord_a['height']
    source = cv2.resize(source, (w2,h2))
    
    try:
        im_rep[y2 + r_noise:y2 + r_noise + h2, x2 + r_noise:x2 + r_noise + w2] = source
        dim_issue = False
    except:
        dim_issue = True

    
    return im_rep, dim_issue

def CopyPaste(images, annotations, shift_copy):

    list_text_field = list(annotations.keys())
    
    dim_issue = True
    while dim_issue:
        source_field_to_change_txt = random.choice(list_text_field)
        target_field_to_change_txt = random.choice(list_text_field)
        source_info_txt = annotations[source_field_to_change_txt]
        target_info_txt = annotations[target_field_to_change_txt]
        img_tr, dim_issue = copy_paste_on_document(images, source_info_txt, target_info_txt, shift_copy)
    
    return img_tr

def CropReplace(image, annotations, image_target, annotations_target, list_image_field, shift_crop):

    field_to_change = random.choice(list_image_field)
    info_source = annotations[field_to_change]
    info_target = annotations_target[field_to_change]
    img_tr, dim_issue = copy_paste_on_two_documents(image, info_source, image_target, info_target, shift_crop)
    return img_tr, dim_issue

def InpaintingText(field_to_change):

    fake = Faker('th_TH')

    id_number = generate_id_number()
    serial_number = generate_card_serial_number_full()

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

    name_parts = full_name_th.strip().split()
    if len(name_parts) >= 2:
        first_th = name_parts[0]
        last_th = name_parts[1]
    else:
        first_th = name_th
        last_th = ""

    name_en_part = safe_romanize(first_th)
    surname_en = safe_romanize(last_th)
    name_en = f"{prefix_en} {name_en_part}"
    
    # name_en = romanize(first_th).capitalize()
    # surname_en = romanize(last_th).capitalize()
    # name_en = f"{prefix_en} {name_en}"

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
    wrapped = textwrap.wrap(address, width=38) 
    
    if field_to_change == 'name_th':
        text_str = name_th
    elif field_to_change == 'name_en':
        text_str = name_en
    elif field_to_change == 'surname_en':
        text_str = surname_en
    elif field_to_change == 'dob_th':
        text_str = dob_str_th
    elif field_to_change == 'dob_en':
        text_str = dob_str_en
    elif field_to_change == 'address_1':
        text_str = wrapped[0]
    elif field_to_change == 'address_2':
        text_str = wrapped[1] if len(wrapped) > 1 else ' '
    elif field_to_change == 'id_number':
        text_str = id_number
    elif field_to_change == 'serial_number':
        text_str = serial_number

    return text_str