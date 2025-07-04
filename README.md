# 📘 **ขั้นตอนการรันไฟล์**

## ✅ 1. รัน `script.py` (อยู่ในโฟลเดอร์ `card_generator`)

🔧 กำหนดตัวเลขจำนวนที่ใช้รันที่ ``` NUM_CARDS = ... ``` โดยจำนวนรูปใน dataset ที่ได้จะเป็นประมาณ 4 เท่าของตัวเลขนี้
➡️ มันจะสร้าง image และไฟล์ `.json`  
📁 ซึ่งจะเก็บไว้ในโฟลเดอร์:  
`fake_generator/data/images`  
`fake_generator/data/annotations`

---

## ✅ 2. รัน `forgery_generator.py` (อยู่ในโฟลเดอร์ `fake_generator`)

🔧 ก่อนรัน ต้อง **แก้ path** ในบรรทัดเกือบล่างสุด:

``` gen = forgery_generator("C:\\Users\\Wasapa\\Documents\\card_detection_dataset_generation_2\\fakeIdCardGen\\fake_generator\\data") ```

📌 ให้เปลี่ยนเป็น path ที่ชี้ไปยังโฟลเดอร์ data ที่ได้จาก script.py ตามเครื่องของคุณ

🛠 จากนั้นปรับตัวเลขในบรรทัดนี้:

``` gen.create(25) ```
📌 ตัวเลขในวงเล็บคือจำนวน sample ที่ต้องการ ซึ่งควรปรับตัวเลขเป็นครึ่งนึงของ ตัวเลขที่ใช่ใน script.py
➡️ Output ที่ได้จะมีภาพประมาณ 2 เท่าของตัวเลขนี้

📁 จะได้โฟลเดอร์:
fake_generator/data/generated_dataset
ซึ่งประกอบด้วยทั้งภาพและ .json ของข้อมูลปลอมที่สร้างขึ้น

## ✅ 3. รัน run_visual_augmentation.py และ batch_augment.py (อยู่ใน `augmentation/visual_augmentation และ augmentation/augmentation ตามลำดับ`)

📁 Output สุดท้ายจะถูกเก็บไว้ใน:
fake_id_dataset
✅ พร้อมนำไปใช้ในการฝึกเทรนโมเดล
