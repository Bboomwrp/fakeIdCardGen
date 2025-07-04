import matplotlib.pyplot as plt

from transform_img import transform_img 
from utils.util   import *
from typing import *
from unicodedata import name
from PIL import ImageFont, ImageDraw, Image

import os
import random
import tqdm


class forgery_generator(transform_img):

    #__slots__ = ["_img_loader", "_classes", "_fake_template", "_transformations","_fake_img_loader","_annotations_path","_imgs_path","_delta_boundary","_static_path", "_flag"]

    def __init__(self, absolute_path:str, fake_template:dict = None, delta_boundary:int=4):

        super().__init__(absolute_path)

        self._static_path_images = "data/Images"
        self._static_path_annotations = "data/Annotations"
                
        if fake_template is None:
            self._fake_template = super().MetaData

        self._delta_boundary = delta_boundary
        self._annotations_path = super().get_img_annotations_path()
        self._imgs_path = super().get_template_path()
        self._img_loader = []

        self.create_loader()

    def create_annotations_bucket(self):

        annotation_bucket = []
   
        for annotation in os.listdir(self._annotations_path):
            annotation_bucket.append(os.path.join(self._annotations_path,annotation))   
       
        return annotation_bucket    
            
    def create_loader(self) -> List[object]:
        
        annotation_bucket = self.create_annotations_bucket()

        for i, im in enumerate(os.listdir(self._imgs_path)):
            name_img = im
            src_img = os.path.join(self._static_path_images, im)
            img = read_img(os.path.join(self._imgs_path, im))

            class_template = read_json(annotation_bucket[i])
            self._img_loader.append(super(forgery_generator, self).Img(img, class_template, name_img, src_img))


    def create(self,sample) -> List[Image.Image]:

        img_bucket = self._img_loader

        for idx in tqdm.tqdm(range(int(sample*0.6))): # ทำให้จำนวนรูป Impaint and rewrite balance กับ crop and replace

                img = random.choice(img_bucket)

                img_id = int(img._name.split("_")[-1].split(".")[0])
                fake_img, field =  super().Inpaint_and_Rewrite(img=img._img,img_id=img_id,info=img._meta)
                name_fake_generated =  "fake_" + img._name.split(".")[0] + "_" + str(idx)

                fake_meta = vars(self._fake_template(src=img._relative_path, type_transformation="Inpaint_and_Rewrite",field=field,loader="data",name=name_fake_generated))

                generated_img = super().Img(img._img, img._meta, img._name)

                generated_img.fake_meta = fake_meta
                generated_img.fake_name = fake_meta["name"]
                generated_img.fake_img = fake_img

                self._fake_img_loader.append(generated_img)

        for smpl in tqdm.tqdm(range(sample)):

            img = random.choice(img_bucket)
            img_id = int(img._name.split("_")[-1].split(".")[0])

            name_fake_generated =  "fake_" + img._name.split(".")[0]

            transformation = random.choice(self._transformations)
            name_transform = (transformation.__name__).split(".")[-1]

            if name_transform == "Inpaint_and_Rewrite":
                fake_img, field = super().Inpaint_and_Rewrite(img=img._img, img_id=img_id,info=img._meta)


                fake_meta = vars(self._fake_template(src=img._relative_path, type_transformation=name_transform,field=field,loader="data",name=name_fake_generated))


                generated_img = super().Img(img._img, img._meta, img._name)

                generated_img.fake_meta = fake_meta
                generated_img.fake_name = fake_meta["name"]
                generated_img.fake_img = fake_img

                self._fake_img_loader.append(generated_img)

            else: # Crop_and_Replace

                delta1 = random.sample(range(self._delta_boundary),2)
                delta2 = random.sample(range(self._delta_boundary),2)

                img2 = random.choice(img_bucket)
                img_id2 = int(img2._name.split("_")[-1].split(".")[0])

                field_list = ['id_number', 'name_th', 'name_en', 'surname_en', 'dob_th', 'dob_en', 'address_1', 'address_2', 'serial_number']             
                selected_field = random.choice(field_list)              

                raw_img1_result, raw_img2_result, field, field2 = super().Crop_and_Replace(
                    img1=img._img, img2=img2._img, info=img._meta, additional_info=None,
                    img_id1=img_id, img_id2=img_id2, delta1=delta1, delta2=delta2, mark=selected_field
                )

                fake_img1 = raw_img1_result
                fake_img2 = raw_img2_result

                name_fake_generated_1 = "fake_" + img._name.split(".")[0] + "_output1_" + str(smpl)
                fake_meta_1 = vars(self._fake_template(
                    src=img._relative_path, second_src=img2._relative_path, shift=(delta1,delta2),
                    type_transformation=name_transform, field=field, second_field=field2,
                    loader="data", name=name_fake_generated_1
                ))

                generated_img = super().Img(img._img, img._meta, img._name)
                generated_img.fake_meta = fake_meta_1
                generated_img.fake_name = fake_meta_1["name"]
                generated_img.fake_img = fake_img1
                generated_img.complement_img = fake_img2
                self._fake_img_loader.append(generated_img)


                name_fake_generated_2 = "fake_" + img2._name.split(".")[0] + "_output2_" + str(smpl)
                fake_meta_2 = vars(self._fake_template(
                    second_src=img._relative_path, src=img2._relative_path, shift=(delta1,delta2),
                    type_transformation=name_transform, second_field=field, field=field2,
                    loader="data", name=name_fake_generated_2
                ))

                generated_img2 = super().Img(img2._img, img2._meta, img2._name)
                generated_img2.fake_meta = fake_meta_2
                generated_img2.fake_name = fake_meta_2["name"]
                generated_img2.fake_img = fake_img2
                generated_img2.complement_img = fake_img1
                self._fake_img_loader.append(generated_img2)

    def store_generated_dataset(self, path_store: Optional[str] = None):

        if path_store is None:
            path = self.absoulute_path+ "/generated_dataset"
        else:
            path = path_store

        print(f"Data beeing stored in the path: {path}")
        store(self._fake_img_loader, path_store=path)



if __name__ == "__main__":
    gen = forgery_generator("C:\\Users\\Wasapa\\Documents\\card_detection_dataset_generation_2\\fakeIdCardGen\\fake_generator\\data")
    
    gen.create(25)
    
    gen.store_generated_dataset()