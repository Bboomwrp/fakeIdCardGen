from .transforms import *

from importlib.resources import path
from typing import *
from PIL import ImageFont, ImageDraw, Image
from pythainlp.transliterate import romanize

import json
import random
import cv2
import os
import imageio
import inspect

import numpy as np
from utils import transforms as t

def generate_id_number():
    nums = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(11)]
    checksum = (11 - sum([x * (13 - i) for i, x in enumerate(nums)]) % 11) % 10
    return '{} {}{}{}{} {}{}{}{}{} {}{} {}'.format(*map(str, nums + [checksum]))

def generate_card_serial_number_full():

    office_code = random.randint(1000, 1299)
    subcode = random.randint(0, 99)
    serial_number = random.randint(0, 99999999)

    return f"{office_code:04d}-{subcode:02d}-{serial_number:08d}"

def safe_romanize(word):
    if not word:
        return ""
    try:
        return romanize(word).capitalize()
    except IndexError:
        return ""
    except Exception:
        return ""

def mask_from_info(img:np.ndarray, shape:np.ndarray):

    def midpoint(x1, y1, x2, y2):
        x_mid = int((x1 + x2) / 2)
        y_mid = int((y1 + y2) / 2)
        return (x_mid, y_mid)

    x0, x1, x2, x3 = shape[0][0], shape[1][0], shape[2][0], shape[3][0]
    y0, y1, y2, y3 = shape[0][1], shape[1][1], shape[2][1], shape[3][1]


    xmid0, ymid0 = midpoint(x1, y1, x2, y2)
    xmid1, ymid1 = midpoint(x0, y0, x3, y3)

    thickness = int(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv2.line(mask, (xmid0, ymid0), (xmid1, ymid1), 255, thickness)

    masked = cv2.bitwise_and(img, img, mask=mask)

    return mask, masked


def read_img(path: str):
    img = np.array(imageio.imread(path, pilmode="RGB"))


    if img.shape[-1] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    else:
        return img

def read_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(data:dict, path:str, name:str=None):
    if name is None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    else:
        path_to_save = os.path.join(path,name+".json")
        with open(path_to_save, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


def store(img_loader: list, path_store: str = None):
    
    if path_store is None:
        path_store = os.path.join(os.getcwd(), "generated_dataset")

    advisor = len(img_loader) // 10

    joined_img_path = os.path.join(path_store, 'image')
    joined_json_path = os.path.join(path_store, 'json')

    os.makedirs(joined_img_path, exist_ok=True)
    os.makedirs(joined_json_path, exist_ok=True)

    for idx, image in enumerate(img_loader):

        path_to_save = os.path.join(joined_img_path, image.fake_name + ".jpg")
        imageio.imwrite(path_to_save, image.fake_img)
        write_json(image.fake_meta, joined_json_path, image.fake_name)

        if (idx % advisor) == 0:
            print(f"{(idx // advisor) * 10} % of the dataset stored")

    print("Data Successfuly stored")

def bbox_to_coord(x, y, w, h):
    
    x_f = x + w
    y_f = y + h

    c1, c2, c3, c4 = [x, y], [x_f, y], [x_f, y_f], [x, y_f]

    return [c1, c2, c3, c4]

def bbox_info(info) -> Tuple[int,...]:

    try:
        shape = info["quad"]  
        x0, x1, x2, x3 = shape[0][0], shape[1][0], shape[2][0], shape[3][0]
        y0, y1, y2, y3 = shape[0][1], shape[1][1], shape[2][1], shape[3][1]

        w = np.max([x0, x1, x2, x3]) - np.min([x0, x1, x2, x3])
        h = np.max([y0, y1, y2, y3]) - np.min([y0, y1, y2, y3])

    except:
        shape = info["shape_attributes"]
        x0 = shape["x"]
        y0 = shape["y"]
        w = shape["width"]
        h = shape["height"]

    return x0, y0, w, h

def replace_info_documents(im0:np.ndarray, im1:np.ndarray, coord0:np.ndarray, coord1:np.ndarray, delta1:np.ndarray, delta2:np.ndarray):

    H, _ = compute_homography(coord0, coord1)

    dx1,dy1 = delta1
    dx2,dy2 = delta2

    im_rep, dim_issue = t.crop_replace(im1, im0, coord1, H, dx1,dy1,dx2,dy2)

    return im_rep, dim_issue

def compute_homography(coord0:np.ndarray, coord1:np.ndarray):

    H, mask = cv2.findHomography(coord1, coord0, cv2.RANSAC, 1.0)

    return H, mask