import numpy as np
import os
import json
import sys
import random

# 1. จัดการ Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controller import db_manager

# --- ตั้งค่า Matbot Pro ---
BOT_NAME = "Matbot_Pro"
MEMORY_FOLDER = 'memory'
MEMORY_FILE = os.path.join(MEMORY_FOLDER, 'mat_pro_weights.npy')

# ขนาดของสมอง: เราจะรับตัวเลข 2 ตัว และประเภทเครื่องหมาย 1 ตัว (รวมเป็น 3 Inputs)
INPUT_SIZE = 3 

# โหลดความจำเดิมมาเทรนต่อ
if os.path.exists(MEMORY_FILE):
    weights = np.load(MEMORY_FILE)
    if weights.shape[0] != INPUT_SIZE: # ป้องกันกรณีเปลี่ยนโครงสร้างสมอง
        weights = np.random.rand(INPUT_SIZE, 1) * 0.1
    print(f"🏋️ {BOT_NAME}: โหลดความจำมาฝึกซ้อมต่อ...")
else:
    weights = np.random.rand(INPUT_SIZE, 1) * 0.1
    print(f"✨ {BOT_NAME}: เริ่มสร้างกล้ามเนื้อสมองใหม่...")

def generate_training_data():
    """สุ่มโจทย์และระบุประเภทเครื่องหมาย"""
    n1 = random.randint(1, 20)
    n2 = random.randint(1, 20)
    op_type = random.choice(['+', '*']) # ลองฝึก 2 อย่างก่อนเพื่อความนิ่ง
    
    if op_type == '+':
        target = n1 + n2
        op_code = 1.0  # ให้เลข 1 แทนการบวก
    else:
        target = n1 * n2
        op_code = 2.0  # ให้เลข 2 แทนการคูณ
        
    return np.array([[float(n1), float(n2), op_code]]), target

# --- เริ่มการฝึกฝน (Training Loop) ---
epochs = 9999999 # ฝึกหนัก 5 หมื่นรอบ
learning_rate = 0.00001
print(f"🔄 กำลังเริ่มการฝึกฝน {epochs} รอบ... โปรดรอสักครู่")



for i in range(epochs):
    x_train, y_target = generate_training_data()
    
    # AI ทาย
    prediction = np.dot(x_train, weights)
    
    # คำนวณความผิดพลาดและปรับตัว
    error = y_target - prediction
    weights += x_train.T * error * learning_rate
    
    if (i + 1) % 10000 == 0:
        print(f"✅ ฝึกสำเร็จไปแล้ว {i + 1} รอบ...")

# --- บันทึกผลงาน ---
np.save(MEMORY_FILE, weights)
db_manager.save_bot_memory(json.dumps(weights.tolist()), BOT_NAME)
print(f"\n🎉 ฝึกเสร็จเรียบร้อย! บันทึกลง Database และไฟล์ {MEMORY_FILE} แล้ว")