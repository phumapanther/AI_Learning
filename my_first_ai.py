import numpy as np
import os

# 1. กำหนดตำแหน่งที่เก็บไฟล์
MEMORY_FOLDER = 'memory'
MEMORY_FILE = os.path.join(MEMORY_FOLDER, 'mat_pro_weights.npy')

if not os.path.exists(MEMORY_FOLDER):
    os.makedirs(MEMORY_FOLDER)

# 2. กำหนดค่า Weights ที่ "ฉลาด" มาแล้ว
# [น้ำหนักตัวเลขที่ 1, น้ำหนักตัวเลขที่ 2, น้ำหนักรหัสเครื่องหมาย]
# หมายเหตุ: ค่าเหล่านี้ถูกคำนวณมาเพื่อเน้นการบวก/ลบเป็นหลัก 
# เนื่องจากการคูณ/หารในโครงสร้างชั้นเดียวจะมีความคลาดเคลื่อนสูง
trained_values = np.array([
    [1.0000],  # Weight สำหรับตัวเลขที่ 1
    [1.0000],  # Weight สำหรับตัวเลขที่ 2
    [0.0000]   # Weight สำหรับปรับค่าตามเครื่องหมาย (Bias-like)
])

# 3. บันทึกเป็นไฟล์ .npy
np.save(MEMORY_FILE, trained_values)

print(f"✨ สร้างไฟล์สมองสำเร็จที่: {MEMORY_FILE}")
print("🧠 พร้อมสำหรับการคำนวณใน mat_ai.py แล้วครับ!")