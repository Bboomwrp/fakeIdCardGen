ขั้นตอนการรันไฟล์

1.รัน script.py จะได้ image กับ json แยกเป็น 2 folder เก็บไว้ใน fake_generator/data

2.รัน forgery_generator.py ซึ่งอยู่ใน fake_generator โดยก่อนรันให้เปลี่ยน path ตรงบรรทัด 
  gen = forgery_generator("C:\\Users\\Wasapa\\Documents\\card_detection_dataset_generation_2\\fakeIdCardGen\\fake_generator\\data") 
  ซึ่งอยู่เกือบบรรทัดสุดท้าย ให้เป็นของเครื่องตัวเอง และเป็น path ที่ไปยัง data ที่ gen มาจาก script.py
  และ ปรับตัวเลขในบรรทัด gen.create(25) ซึ่งอยู่เกือบบรรทัดสุดท้าย ให้เป็นตามจำนวนที่ต้องการ โดยจะได้ภาพเป็นประมาณ 2 เท่าของตัวเลขที่ใส่
  ซึ่งจะได้ image กับ json แยกเป็น 2 folder อยู่ใน fake_generator/data/generated_dataset

3.รัน run_visual_augmentation.py และ batch_augment.py ซึ่งจะได้ dataset เก็บอยู่ใน fake_id_dataset พร้อมนำไปเทรนโมเดล

