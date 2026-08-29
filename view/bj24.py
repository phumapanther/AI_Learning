import random
import json
import sys
import os

# เพิ่มบรรทัดนี้เพื่อให้ Python มองเห็นโฟลเดอร์หลัก
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller.bot_brain import BlackjackBot
from controller import db_manager
from view.simulate import simulate_training  # ✅ เรียกข้ามโฟลเดอร์แบบนี้

def create_deck():
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    values = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
    deck = []
    for _ in range(4):
        for r in ranks:
            deck.append((r, values[r]))
    random.shuffle(deck)
    return deck

# สร้างบอทไว้ข้างนอก
bot_brain = BlackjackBot()

def start_game(balance, brain):
    print(f"\n💰 เงินคงเหลือของคุณ: {balance} บาท")
    
    while True:
        user_input = input(f"ระบุเงินเดิมพัน (1 - {balance}) หรือ 'exit' เพื่อออก: ").lower().strip()
        if user_input == 'exit':
            return -1
            
        try:
            bet = int(user_input)
            if 1 <= bet <= balance:
                balance -= bet
                print(f"💸 วางเดิมพันแล้วคงเหลือ: {balance} บาท")
                break
            else:
                print("❌ จำนวนเงินไม่ถูกต้อง!")
        except ValueError:
            print("❌ กรุณาใส่ตัวเลขเดิมพันเท่านั้น")

    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    
    # --- ตาของผู้เล่น ---
    while True:
        player_score = sum(card[1] for card in player_hand)
        print(f"\nไพ่ในมือคุณ: {[c[0] for c in player_hand]} | แต้มรวม: {player_score}")
        
        if player_score > 24:
            print(f"💥 เกิน 24! คุณแพ้ (Bust)")
            # สอนบอท: ถ้าเราแพ้ (Bust) บอทจะยังไม่ทันได้เล่น แต่บอทชนะโดยปริยาย
            return balance 
        
        if player_score == 24:
            break
            
        action = input("พิมพ์ '!hit' เพื่อจั่ว, '!c' เพื่อหยุด: ").lower().strip()
        if action == '!hit':
            player_hand.append(deck.pop())
        elif action == '!c':
            break

    # --- ตาของบอท ---
    print("\n--- ตาของบอทแล้ว ---")
    bot_hand = [deck.pop(), deck.pop()]
    bot_history = []
    
    while True:
        bot_score = sum(card[1] for card in bot_hand)
        if bot_score > 24:
            break
            
        action = brain.get_action(bot_score, player_hand[0][1])
        bot_history.append((bot_score, action))
        
        if action == "!hit":
            print(f"🤖 บอทตัดสินใจ: จั่วเพิ่ม (!hit)")
            bot_hand.append(deck.pop())
        else:
            print(f"🤖 บอทตัดสินใจ: พอแล้ว (!c)")
            break
    
    print(f"ไพ่บอท: {[c[0] for c in bot_hand]} | แต้มบอท: {bot_score}")

    # --- สรุปผลการแข่งและสอนบอท (จุดแก้ไขหลัก) ---
    print("\n=== สรุปผลการแข่ง ===")
    
    # คำนวณ Reward สำหรับบอท
    reward = 0
    if bot_score > 24 or (player_score <= 24 and player_score > bot_score):
        reward = -1  # บอทแพ้
        print(f"🏆 คุณชนะ! ได้รับเงินรางวัล {bet * 2} บาท")
        final_balance = balance + (bet * 2)
    elif player_score < bot_score or player_score > 24:
        reward = 1   # บอทชนะ
        print("❌ บอทแต้มสูงกว่า! คุณแพ้")
        final_balance = balance
    else:
        reward = 0.1 # เสมอ (ให้รางวัลนิดหน่อยที่ยืนระยะได้)
        print("🤝 เสมอ! คืนเงินเดิมพัน")
        final_balance = balance + bet

    # สอนบอทตามประวัติที่เล่นมาในตานี้
    for score, act in bot_history:
        brain.learn(score, player_hand[0][1], act, reward)
    
    # เซฟสมองลง MySQL
    memory_to_save = json.dumps(brain.q_table) # แปลง dict เป็น string
    db_manager.save_bot_memory(memory_to_save, 'AlphaBot') # ระบุชื่อบอทชัดเจน

    return final_balance

# ส่วนเริ่มและจบโปรแกรม
if __name__ == "__main__":
    my_balance = int(db_manager.get_balance())
    bot_brain = BlackjackBot()

    print("--- 🃏 Blackjack 24 ML System ---")
    print("1: โหมดเล่นเอง (Manual Play)")
    print("2: โหมดบอทเทรนตัวเอง (Self-Training Simulation)")
    
    choice = input("เลือกโหมดที่ต้องการ: ").strip()

    if choice == "2":
        try:
            num_rounds = int(input("ต้องการให้บอทเทรนตัวเองกี่รอบ?: "))
            simulate_training(num_rounds, bot_brain)
            print("--- ✅ การเทรนเสร็จสิ้น บันทึกความจำแล้ว ---")
            # จบการทำงานตรงนี้เลย ไม่ไปเข้า Loop เล่นเอง
            sys.exit() 
        except ValueError:
            print("❌ กรุณาใส่จำนวนรอบเป็นตัวเลข")
    
    # --- โหมดเล่นเอง (Manual) จะทำงานต่อเมื่อไม่ได้เลือกโหมด 2 ---
    print("\n--- เริ่มโหมดเล่นเอง ---")
    while my_balance > 0:
        updated_val = start_game(my_balance, bot_brain)
        
        if updated_val == -1:
            print("👋 ขอบคุณที่มาใช้บริการ!")
            break
            
        my_balance = updated_val
        db_manager.update_balance(my_balance)

        if my_balance <= 0:
            print("\n💀 เงินหมดตัวแล้ว! เกมโอเวอร์")
            break

        if input("\nเล่นต่อไหม? (y/n): ").lower() != 'y':
            print(f"💰 คุณกลับบ้านพร้อมเงิน {my_balance} บาท")
            break