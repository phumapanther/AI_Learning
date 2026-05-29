import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import db_config  # ✅ เรียกหาไฟล์ที่อยู่โฟลเดอร์ด้านนอก

def get_balance():
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        
        # ✅ แปลงเป็น int ตรงนี้เลยก่อน return
        if result:
            return int(result[0]) 
        return 1000
    except Exception as e:
        print(f"⚠️ Error ดึงข้อมูล: {e}")
        return 1000

def update_balance(new_balance):
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = %s WHERE id = 1", (new_balance,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error บันทึกข้อมูล: {e}")

def load_bot_memory(bot_name='AlphaBot'): # กำหนด Default เป็น AlphaBot เพื่อไม่ให้กระทบโค้ด BJ เดิม
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        # เปลี่ยนจาก 'AlphaBot' เป็น %s เพื่อรับชื่อบอทตัวไหนก็ได้
        cursor.execute("SELECT memory FROM bot_data WHERE bot_name = %s", (bot_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # Matbot จะได้ข้อมูลเป็น List ส่วน AlphaBot จะได้เป็น Dict
            # json.loads จัดการให้เองอัตโนมัติครับ
            return result[0] 
        return None
    except Exception as e:
        print(f"⚠️ โหลดความจำบอท {bot_name} ไม่ได้: {e}")
        return None

def save_bot_memory(memory_data, bot_name='AlphaBot'):
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        # กำหนด ID ตามชื่อบอท
        bot_id = 1 if bot_name == 'AlphaBot' else 2
        
        # ใส่ id กลับเข้าไปใน INSERT และ ON DUPLICATE KEY
        sql = """
            INSERT INTO bot_data (id, bot_name, memory) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE memory = %s
        """
        
        # ส่งค่าให้ครบ 4 จุด (id, bot_name, memory, memory_update)
        cursor.execute(sql, (bot_id, bot_name, memory_data, memory_data))
        
        conn.commit()
        conn.close()
        # print(f"✅ บันทึกความจำ {bot_name} สำเร็จ") 
        
    except Exception as e:
        print(f"⚠️ บันทึกความจำบอท {bot_name} ไม่ได้: {e}")