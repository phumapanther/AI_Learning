import sys
import os
import json

# เพิ่มบรรทัดนี้เพื่อให้ Python มองเห็นโฟลเดอร์หลัก
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controller import db_manager 

def simulate_training(rounds, brain):
    from view.bj24 import create_deck  # ป้องกัน Circular Import
    print(f"🤖 กำลังเริ่มโหมดเทรนตัวเอง (เวอร์ชั่นดูไพ่เจ้ามือ) จำนวน {rounds} รอบ...")
    
    for i in range(rounds):
        deck = create_deck()
        
        # --- เตรียมไพ่เจ้ามือ (หงายใบแรกให้บอทดู) ---
        dealer_hand = [deck.pop(), deck.pop()]
        dealer_upcard = dealer_hand[0][1] # ไพ่ใบแรกของเจ้ามือ

        # 1. ตาของบอทฝั่งผู้เล่น
        player_hand = [deck.pop(), deck.pop()]
        player_history = []
        while True:
            player_score = sum(card[1] for card in player_hand)
            if player_score >= 24: break
            
            # ✅ ส่งแต้มเรา และ ไพ่หน้าเปิดเจ้ามือ ให้บอทตัดสินใจ
            action = brain.get_action(player_score, dealer_upcard) 
            player_history.append((player_score, dealer_upcard, action))
            
            if action == "!hit":
                player_hand.append(deck.pop())
            else:
                break
        player_score = sum(card[1] for card in player_hand)

        # 2. ตาของเจ้ามือ (เล่นตามกฎเดิม หรือใช้ AI ช่วยก็ได้)
        while True:
            bot_score = sum(card[1] for card in dealer_hand)
            if bot_score < 18: # กฎพื้นฐานเจ้ามือ: ต่ำกว่า 18 ต้องจั่ว
                dealer_hand.append(deck.pop())
            else:
                break
        bot_score = sum(card[1] for card in dealer_hand)

        # 3. สรุปผลและให้รางวัล
        if player_score > 24:
            reward = -1
        elif bot_score > 24 or player_score > bot_score:
            reward = 1
        elif player_score < bot_score:
            reward = -1
        else:
            reward = 0.1

        # ✅ สอนบอทด้วย State ใหม่ (แต้มเรา-แต้มเจ้ามือ)
        for p_score, d_up, act in player_history:
            brain.learn(p_score, d_up, act, reward)

       # ✅ แก้ไขจุดเซฟในลูป (ทุก 1,000 รอบ)
        if (i + 1) % 1000 == 0:
            print(f"✅ เทรนสำเร็จแล้ว {i + 1} รอบ... (Data States: {len(brain.q_table)})")
            # แปลงเป็น JSON ก่อนเซฟ (ตามโครงสร้างใหม่ของเรา)
            memory_to_save = json.dumps(brain.q_table) 
            db_manager.save_bot_memory(memory_to_save, 'AlphaBot')
    
    memory_to_save = json.dumps(brain.q_table)
    db_manager.save_bot_memory(memory_to_save, 'AlphaBot')
    print("💾 บันทึกความฉลาดของ AlphaBot ลง Database เรียบร้อย!")