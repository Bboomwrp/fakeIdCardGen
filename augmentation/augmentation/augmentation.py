from PIL import Image, ImageFont, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import string
import json
import csv
import cv2

# Data augmentation
def data_aug(image, technique, margin = 0.2, diff = False):
  
  if technique == "rotation":
    print("Data Aug Technique = Rotation")
    angle = 5
    
    # grab the dimensions of the image and then determine the
    # centre
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    image = cv2.warpAffine(image, M, (nW, nH))

    return image

  elif technique == "shearing":
    print("Data Aug Technique = Shearing")
    shear_factor = 0.1
    shear_factor = random.uniform(shear_factor,0.2)

    w,h = image.shape[1], image.shape[0]


    M = np.array([[1, abs(shear_factor), 0],[0,1,0]])

    nW =  image.shape[1] + abs(shear_factor*image.shape[0])


    image = cv2.warpAffine(image, M, (int(nW), image.shape[0]))


    image = cv2.resize(image, (w,h))

    scale_factor_x = nW / w

    return image

  elif technique == "scaling":
    print("Data Aug Technique = Scaling")
    if type(margin) == tuple:
      assert len(margin) == 2, "Invalid range"
      assert margin[0] > -1, "Scale factor can't be less than -1"
      assert margin[1] > -1, "Scale factor can't be less than -1"
    else:
      assert margin > 0, "Please input a positive float"
      margin = (max(-1, -margin), margin)
  
    img_shape = image.shape

    if diff:
      scale_x = random.uniform(*margin)
      scale_y = random.uniform(*margin)
    else:
      scale_x = random.uniform(*margin)
      scale_y = scale_x

    resize_scale_x = 1 + scale_x
    resize_scale_y = 1 + scale_y

    image=  cv2.resize(image, None, fx = resize_scale_x, fy = resize_scale_y)

    #bboxes[:,:4] *= [resize_scale_x, resize_scale_y, resize_scale_x, resize_scale_y]



    canvas = np.zeros(img_shape, dtype = np.uint8)

    y_lim = int(min(resize_scale_y,1)*img_shape[0])
    x_lim = int(min(resize_scale_x,1)*img_shape[1])

    print(y_lim, x_lim)

    canvas[:y_lim,:x_lim,:] =  image[:y_lim,:x_lim,:]

    image = canvas
    #bboxes = clip_box(bboxes, [0,0,1 + img_shape[1], img_shape[0]], 0.25)


    return image
    
  elif technique == "translation":
    print("Data Aug Technique = Translation")
    if type(margin) == tuple:
      assert len(margin) == 2, "Invalid range"  
      assert margin[0] > 0 and margin[0] < 1
      assert margin[1] > 0 and margin[1] < 1
    else:
      assert margin > 0 and margin < 1
      margin = (-margin, margin)
      
    #Chose a random digit to scale by 
    img_shape = image.shape
    
    #translate the image
    
    #percentage of the dimension of the image to translate
    translate_factor_x = random.uniform(*margin)
    translate_factor_y = random.uniform(*margin)
    
    if not diff:
      translate_factor_y = translate_factor_x
        
    canvas = np.zeros(img_shape).astype(np.uint8)


    corner_x = int(translate_factor_x*image.shape[1])
    corner_y = int(translate_factor_y*image.shape[0])
    
    #change the origin to the top-left corner of the translated box
    orig_box_cords =  [max(0,corner_y), max(corner_x,0), min(img_shape[0], corner_y + image.shape[0]), min(img_shape[1],corner_x + image.shape[1])]

    mask = image[max(-corner_y, 0):min(image.shape[0], -corner_y + img_shape[0]), max(-corner_x, 0):min(image.shape[1], -corner_x + img_shape[1]),:]
    canvas[orig_box_cords[0]:orig_box_cords[2], orig_box_cords[1]:orig_box_cords[3],:] = mask
    img = canvas
    
    #bboxes[:,:4] += [corner_x, corner_y, corner_x, corner_y]
    
    #bboxes = clip_box(bboxes, [0,0,img_shape[1], img_shape[0]], 0.25)
    
    return img #, bboxes

    
# Color augmentaions
def color_aug(image, technique):
  contrast = 0.5
  brightness = 0

  if technique == "blur":
    print("Color Aug Technique = Blur")
    image = cv2.GaussianBlur(image, (3, 3), 0)

  elif technique == "saturation":
    print("Color Aug Technique = Saturation")
    saturation = 50
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    v = image[:, :, 2]
    v = np.where(v <= 255 - saturation, v + saturation, 255)
    image[:, :, 2] = v

    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
  elif technique == "contrast":
    print("Color Aug Technique = Contrast")
    contrast = 50
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    v = image[:, :, 2].astype(np.int16)  # ป้องกัน overflow
    v = np.where(v < 190, np.clip(v - contrast, 0, 255), np.clip(v + contrast, 0, 255))
    image[:, :, 2] = v.astype(np.uint8)  # กลับมาเป็น uint8
    
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
  elif technique == "brightness":
    image = cv2.addWeighted(image, 2, np.zeros(image.shape, image.dtype),0, 2)

  return image

# img = cv2.imread(os.path.join("output_fake_ids", "thai_id_000.jpg"))
# if img is None:
#     print("❌ ไม่พบไฟล์ภาพ")
#     exit()
# color_techniques = ['blur', 'saturation','contrast', 'brightness']
# techniques = ['rotation', 'shearing', 'scaling', 'translation']
# num = np.random.randint(len(techniques))
# img = data_aug(img,techniques[num])
# img = color_aug(img, color_techniques[2])


#cv2_imshow(img)
#img = color_aug(img, color_techniques[3])
#cv2_imshow(img)

# cv2.imshow("Augmented", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

