import random

import sys
import os

# เพิ่มบรรทัดนี้เพื่อให้ Python มองเห็นโฟลเดอร์หลัก
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller import db_managai  # ✅ เรียกข้ามโฟลเดอร์แบบนี้

distance_moved = 1
total_reward = 0  # 1. เพิ่มตัวแปรเก็บคะแนนรวมไว้ข้างนอก Loop

for step in range(10): # วน 10 รอบ (0-9)
    height = random.uniform(0.1, 1.0) 
    distance_moved = distance_moved + 0.3
    
    print(f"--- ก้าวที่ {step} | ความสูง: {height:.2f} เมตร ---")

    if height < 0.5:
        total_reward = total_reward - 100 # 2. หักคะแนนถ้าล้ม
        print(f"Penalty: -100 (Robot Fell!!)")
        break 
    else:
        total_reward = total_reward + 10 # 3. บวกคะแนนถ้าเดินได้
        print(f"Reward: +10 (คะแนนรวมตอนนี้: {total_reward})")

print("==============================")
print(f"จบการทดลอง! คะแนนสุทธิของคุณคือ: {total_reward}")
print("==============================")