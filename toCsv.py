import os
import csv

# ระบุ path ของโฟลเดอร์
folder_path = 'C:/Users/Boom/projects/fakeidcardGen/faces'  # เช่น 'C:/Users/Weeraphat/Documents/myfiles'

# ดึงรายชื่อไฟล์ทั้งหมด
file_list = os.listdir(folder_path)

# เขียนรายชื่อไฟล์ลง CSV
with open('faces_list.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename'])  # หัวตาราง
    for file_name in file_list:
        writer.writerow([file_name])
