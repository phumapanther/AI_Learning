import numpy as np
import os
import json
import sys
import re

# 1. จัดการ Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controller import db_manager

# --- ตั้งค่า Matbot ---
BOT_NAME = "Matbot"
MEMORY_FOLDER = 'memory'
MEMORY_FILE = os.path.join(MEMORY_FOLDER, 'mat_pro_weights.npy')

if not os.path.exists(MEMORY_FOLDER):
    os.makedirs(MEMORY_FOLDER)

# --- ระบบสมอง (Weights) ---
# เพื่อให้รับสมการยาวๆ ได้ เราจะสมมติว่ารับตัวเลขสูงสุด 5 ตัวในหนึ่งสมการ
INPUT_SIZE = 5 
if os.path.exists(MEMORY_FILE):
    weights = np.load(MEMORY_FILE)
    print(f"🧠 {BOT_NAME}: โหลดความจำสำเร็จ")
else:
    # สุ่ม Weights สำหรับตัวเลข 5 ตำแหน่ง
    weights = np.random.rand(INPUT_SIZE, 1) * 0.1
    print(f"✨ {BOT_NAME}: สร้างสมองใหม่พร้อมลุยสมการ")

def solve_and_learn(equation, weights):
    try:
        # 1. หาคำตอบจริง
        target = eval(equation)
        
        # 2. แยกตัวเลข (เอาแค่ 2 ตัวแรกมาใช้)
        nums = [float(n) for n in re.findall(r'\d+', equation)]
        if len(nums) < 2:
            print("⚠️ ใส่ตัวเลขอย่างน้อย 2 ตัวนะ")
            return weights
            
        # 3. ตรวจสอบเครื่องหมาย (มองหาตัวแรกที่เจอ)
        op_code = 1.0 # Default เป็นบวก
        if '*' in equation: op_code = 2.0
        elif '-' in equation: op_code = 3.0
        elif '/' in equation: op_code = 4.0

        # 4. เตรียม Input ให้เหลือแค่ 3 ช่อง (เลข1, เลข2, รหัสเครื่องหมาย)
        input_vector = np.array([[nums[0], nums[1], op_code]])

        # 5. AI ทาย (ตอนนี้ Shape จะตรงกันแล้วคือ (1,3) เจอกับ (3,1))
        prediction = np.dot(input_vector, weights)
        print(f"🤖 บอททาย: {prediction[0][0]:.4f} | ✅ คำตอบจริง: {target:.4f}")

        # 6. เรียนรู้แบบเบาๆ
        error = target - prediction
        weights += input_vector.T * error * 0.000001
        
        return weights
    except Exception as e:
        print(f"❌ พลาดท่า! : {e}")
        return weights

# --- Loop การทำงาน ---
print(f"\n--- 🔢 {BOT_NAME} : ระบบคำนวณสมการซับซ้อน ---")
while True:
    user_input = input("\nกรอกสมการ (เช่น 10+2*5) หรือ 'exit': ").strip()
    if user_input.lower() == 'exit': break
    
    weights = solve_and_learn(user_input, weights)
    
    # บันทึกทุกครั้งที่สอน
    np.save(MEMORY_FILE, weights)
    db_manager.save_bot_memory(json.dumps(weights.tolist()), BOT_NAME)