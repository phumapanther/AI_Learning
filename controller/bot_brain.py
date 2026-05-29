import random

import sys
import os

# เพิ่มบรรทัดนี้เพื่อให้ Python มองเห็นโฟลเดอร์หลัก
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller import db_manager  # ✅ เรียกข้ามโฟลเดอร์แบบนี้

class BlackjackBot:
    def __init__(self):
        #พอมีการเรียกใช้ class BlackjackBot เริ่มฟังชั้น __init__ ตัวแปร self เอาไว้เก็บค่าโดยที่ self.q_table เป้นค่าว่าง
        # self.q_table = {} 

        # แต่แทนที่จะเริ่มจากค่าว่าง {} เสมอ 
        # ให้ไปถาม Database ว่า "มีความจำเก่าของฉันไหม?"
        raw_data = db_manager.load_bot_memory('AlphaBot') 
        
        # ตรวจสอบว่าได้ข้อมูลมาไหม และข้อมูลที่ได้มาเป็น String หรือเปล่า
        if raw_data:
            import json
            # แปลงจาก JSON String กลับมาเป็น Dictionary สำหรับ Blackjack
            self.q_table = json.loads(raw_data)
            print("🧠 AlphaBot: โหลดความจำ Q-Table เรียบร้อย!")
        else:
            self.q_table = {}
            print("✨ AlphaBot: เริ่มต้นสมองใหม่ (ว่างเปล่า)")
            
        if not self.q_table:
            self.q_table = {} # ถ้าไม่มีจริงๆ ค่อยเริ่มจากศูนย์

    def get_action(self, player_score, dealer_upcard, epsilon=0.1):
        # สร้าง Key ใหม่ที่รวมข้อมูล 2 ฝั่ง เช่น "15-10" (เรา 15 เจ้ามือโชว์ 10)
        state = f"{player_score}-{dealer_upcard}"
        
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0]
        
        if random.random() < epsilon:
            return random.choice(["!hit", "!c"])

        if self.q_table[state][0] >= self.q_table[state][1]:
            return "!c"
        else:
            return "!hit"

    # ฟังก์ชันนี้ไว้ให้บอท "เรียนรู้" หลังจบเกม (Train)
    def learn(self, player_score, dealer_upcard, action, reward):
        state = f"{player_score}-{dealer_upcard}"
        action_idx = 1 if action == "!hit" else 0
        
        old_value = self.q_table[state][action_idx]
        self.q_table[state][action_idx] = old_value + 0.1 * (reward - old_value)