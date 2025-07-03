#Description This file has the super classes with the image class, the video class and the façade of the Midv500 loader
from utils.transforms import *
from utils.util   import *

from ast import Constant
from dataclasses import dataclass
from PIL import Image
from typing import *


import inspect
import sys


class transform_img():

    __slots__ = ["_absolute_path","_img_loader", "_fake_img_loader","_transformations"]

    def __init__(self, path: str):
        self._absolute_path = path

        # PlaceHolders for the fake imgs
        self._img_loader = []
        self._fake_img_loader = []
        self._transformations = [self.Crop_and_Replace, self.Inpaint_and_Rewrite]
        self._flag = 1 if os.path.dirname(inspect.getframeinfo(sys._getframe(1)).filename).split("/")[-1] == "data" else 0


    @property
    def absoulute_path(self):
        return self._absolute_path
    
    
    def get_template_path(self):
        print(self._absolute_path)
        assert os.path.exists(os.path.join(self.absoulute_path, "Images")), "There's not any image folder in this directory"
        return os.path.join(self.absoulute_path, "Images")

    def get_video_path(self):
        assert os.path.exists(os.path.join(self.absoulute_path, "Images")), "There's not any image folder in this directory"

        return os.path.join(self.absoulute_path, "clips")

    def get_img_annotations_path(self):
        assert os.path.exists(os.path.join(self.absoulute_path, "Annotations")), "There's not any metadata (.json) folder in this directory"

        return os.path.join(self._absolute_path, "Annotations")

    def _get_all_field_names(self, info: dict, img_id: Optional[int] = None, force_flag: int = 1) -> List[str]:
        """Helper to get all valid field names from metadata based on context."""
        if (self._flag != 1 or force_flag != 1): 
            return list(info.keys())
        else:
            assert type(img_id) is int
            if "_via_img_metadata" not in info or len(list(info["_via_img_metadata"])) <= img_id:
                return [] 
            selected = list(info["_via_img_metadata"])[img_id]
            regions = info["_via_img_metadata"][selected]["regions"]
           
            return [r["region_attributes"].get("field_name") for r in regions if "region_attributes" in r and r["region_attributes"].get("field_name") is not None]      
        
    def get_field_info(self, info:dict, img_id1:int=None, mark:str = None, force_flag:int=1) -> Tuple[Dict, Constant]:
        assert type(info) is dict
        
        if (self._flag != 1 or force_flag != 1): 
            fields = list(np.unique(list(info.keys())))
            
            if not mark or mark == None:
                if fields:
                    field_to_change = random.choice(fields)
                    swap_info = info[field_to_change]
                    field_to_return = field_to_change
                else:
                    raise ValueError("No fields found in metadata for selection in Midv500 context.")
            else:
                if mark in info:
                    swap_info = info[mark]
                    field_to_return = mark
                else:
                    raise ValueError(f"Mark '{mark}' not found as a direct field in info for Midv500 context.")
            return swap_info, field_to_return

        else: 
            assert type(img_id1) is int
            
            selected = list(info["_via_img_metadata"])[img_id1]
            regions = info["_via_img_metadata"][selected]["regions"]

            if not mark or mark == None:
                if regions:
                    field_to_change_idx = random.randint(0, len(regions) - 1) 
                    swap_info = regions[field_to_change_idx]
                    field_to_return = swap_info["region_attributes"].get("field_name", str(field_to_change_idx))
                else:
                    raise ValueError(f"No regions found for img_id {img_id1} in Midv2020 context.")
            else: 
                try:
                    swap_info = regions[mark] 
                    field_to_return = swap_info["region_attributes"].get("field_name", str(mark))
                except (TypeError, IndexError) as e:
                    raise ValueError(f"Invalid 'mark' ({mark}) provided for regions in img_id {img_id1} in Midv2020 context (expected int index): {e}")
    
            return swap_info, field_to_return
    
    def Crop_and_Replace(self, img1: np.ndarray, img2: np.ndarray, info: dict, additional_info: dict, img_id1: int = None, img_id2: int = None, delta1: list = [2, 2], delta2: list = [2, 2], mark: str = None, force_flag: int = 1) -> Tuple[Image.Image, Image.Image, Any, Any]:
        sInfo = True if (np.random.randint(100) > 5) or (mark is not None) else False
        mixed = False

        if bool(self._flag) is True or bool(force_flag) is True:

            if additional_info is None:
                if mark is None:
                    swap_info_1, field_to_return1 = self.get_field_info(info=info, img_id1=img_id1)
                    swap_info_2, field_to_return2 = self.get_field_info(info=info, img_id1=img_id2)
                    if not sInfo and (swap_info_1 == swap_info_2):
                        while(swap_info_1 == swap_info_2):
                            swap_info_2, field_to_return2 = self.get_field_info(info=info, img_id1=img_id2)
                else:
                    swap_info_1, field_to_return1 = self.get_field_info(info=info, img_id1=img_id1, mark=mark)
                    swap_info_2, field_to_return2 = self.get_field_info(info=info, img_id1=img_id2, mark=mark)
            else:
                if mark is not None:
                    swap_info_1, field_to_return1 = self.get_field_info(info=info, img_id1=img_id1, mark=mark)
                    swap_info_2, field_to_return2 = self.get_field_info(info=additional_info, img_id1=img_id2, mark=mark)
                else:
                    fields_in_info = self._get_all_field_names(info=info, img_id=img_id1, force_flag=force_flag)
                    fields_in_additional_info = self._get_all_field_names(info=additional_info, img_id=img_id2, force_flag=force_flag)
                    common_fields = list(set(fields_in_info) & set(fields_in_additional_info))
                    if not common_fields:
                        return img1, img2, None, None
                    chosen_common_field = random.choice(common_fields)
                    swap_info_1, field_to_return1 = self.get_field_info(info=info, img_id1=img_id1, mark=chosen_common_field)
                    swap_info_2, field_to_return2 = self.get_field_info(info=additional_info, img_id1=img_id2, mark=chosen_common_field)
        else:
            assert additional_info != None, "When use Midv500 additional template information must be supplied"
            mixed = True if (type(img_id1) is int) or (type(img_id2) is int) else False
            if mixed:
                idd = img_id1 if type(img_id1) is int else img_id2
                try:
                    swap_info_1, field_to_return1 = self.get_field_info(info=info, img_id1=idd)
                    swap_info_2, field_to_return2 = self.get_field_info(info=additional_info, force_flag=0)
                except:
                    swap_info_1, field_to_return1 = self.get_field_info(info=additional_info, img_id1=idd)
                    swap_info_2, field_to_return2 = self.get_field_info(info=info, force_flag=0)
            else:
                if mark is not None:
                    swap_info_1, field_to_return1 = self.get_field_info(info=info, force_flag=0, mark=mark)
                    swap_info_2, field_to_return2 = self.get_field_info(info=additional_info, force_flag=0, mark=mark)
                else:
                    fields_in_info = self._get_all_field_names(info=info, force_flag=0)
                    fields_in_additional_info = self._get_all_field_names(info=additional_info, force_flag=0)
                    common_fields = list(set(fields_in_info) & set(fields_in_additional_info))
                    if not common_fields:
                        print(f"Skipping Crop_and_Replace: No common field names found between documents in Midv500 context.")
                        return img1, img2, None, None
                    chosen_common_field = random.choice(common_fields)
                    swap_info_1, field_to_return1 = self.get_field_info(info=info, force_flag=0, mark=chosen_common_field)
                    swap_info_2, field_to_return2 = self.get_field_info(info=additional_info, force_flag=0, mark=chosen_common_field)

        try:
            from utils.util import replace_info_documents, bbox_info, bbox_to_coord
        except ImportError:
            print("ERROR: Could not import 'replace_info_documents', 'bbox_info', or 'bbox_to_coord' from 'utils.util'. Please ensure the import path is correct.")
            return img1, img2, None, None

    # Get bounding box information
        x0, y0, w0, h0 = bbox_info(swap_info_1)
        x1, y1, w1, h1 = bbox_info(swap_info_2)
        coord0 = np.array(bbox_to_coord(x0, y0, w0, h0), dtype=np.float32())
        coord1 = np.array(bbox_to_coord(x1, y1, w1, h1), dtype=np.float32())

        if 'mixed' in locals() and mixed:
           fake_document1, dim_issue_flag = replace_info_documents(img1, img2, coord0, coord1, delta1, delta2)
           fake_document2, dim_issue_flag = replace_info_documents(img2, img1, coord1, coord0, delta1, delta2)
        else:
           fake_document1, dim_issue_flag = replace_info_documents(img1, img2, coord0, coord1, delta1, delta2)
           fake_document2, dim_issue_flag = replace_info_documents(img2, img1, coord1, coord0, delta1, delta2)

        if dim_issue_flag:
            print(f"dim_issue_flag is True. Original images returned.")
            return img1, img2, field_to_return1, field_to_return2

        return fake_document1, fake_document2, field_to_return1, field_to_return2

    def Inpaint_and_Rewrite(self,img: np.ndarray, info: dict,img_id: int=None, mark:str=None, force_flag:int=1, enable_debug: bool = False) -> Tuple[Image.Image, Constant]: # เพิ่ม enable_debug
        if bool(self._flag) is True or bool(force_flag) is True:
            swap_info, field_to_change = self.get_field_info(info=info,img_id1=img_id, mark=mark)

        else:
            swap_info, field_to_change = self.get_field_info(info=info, mark=mark)  

        x0, y0, w, h = bbox_info(swap_info)

        shape = bbox_to_coord(x0, y0, w, h)

        if field_to_change in ['name_en', 'surname_en', 'dob_th', 'dob_en','serial_number', 'id_number']:
            coord = [x0, y0-5, w, h]

        elif field_to_change in ['name_th', 'address_1']:
            coord = [x0, y0+3, w, h]

        else:
            coord = [x0, y0, w, h]
        
        mask, _ = mask_from_info(img, shape)
        text_str = InpaintingText(field_to_change)
        
        fake_text_image =  inpaint_image(img=img, coord=coord, mask=mask, field_name=field_to_change, text_str=text_str)
        return fake_text_image, field_to_change

    ####################################################################################################
    class Img(object):

        __slots__ = ["_img", "_meta","_name" ,"_fake_name","_fake_img", "_fake_meta", "_complement_img","_relative_path"]

        def __init__(self, img:np.ndarray, metadades: dict, name:str, relative_path:str=None):
            self._img = img
            self._meta = metadades
            self._name = name
            self._relative_path = relative_path

            #still not declared
            self._fake_name = None
            self._fake_img =  None
            self._fake_meta = None

            self._complement_img = []


        #GETTERS AND SETTERS
        @property
        def fake_name(self):
            return self._fake_name

        @fake_name.setter
        def fake_name(self, name):
            self._fake_name = name

        @property
        def fake_img(self):
            return self._fake_img

        @fake_img.setter
        def fake_img(self, img):
            self._fake_img = img



        @property
        def fake_meta(self):
            return self._fake_meta

        @fake_meta.setter
        def fake_meta(self, meta):
            self._fake_meta = meta


        @property
        def complement_img(self):
            return self._complement_img
        @complement_img.setter
        def complement_img(self, img):
            self._complement_img = img


    ####################################################################################################
    @dataclass
    class MetaData:
        name:str =None
        src:str=None
        second_src:str=None
        loader:str=None
        field:str=None 
        second_field:str = None 
        shift:list=None 
        type_transformation:str=None