import os

import flet as ft
import random
import asyncio

# ฟังก์ชันหลักทำงานในโหมด async เพื่อรองรับระบบหน่วงเวลา (asyncio.sleep) บนเว็บเบราว์เซอร์
async def main(page: ft.Page):
    # ตั้งค่าหน้าเว็บ / หน้าต่างแอป
    page.title = "Game Guess Go"
    page.window_width = 700
    page.window_height = 750
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f0f8ff"  # สีพื้นหลังหน้าเว็บ

    # --- ข้อมูลและสถานะเกม ---
    word_dict = {
        'kong': {'category': 'คนเขียนโปรแกรมนี้', 'hint': ['ใส่แว่น', 'สารสนเทศ', 'victus']},
        'apple': {'category': 'ผลไม้', 'hint': ['สีแดง', 'เปรี้ยว', 'หวาน']},
        'sound': {'category': 'อีกชื่อนึง', 'hint': ['ภาษาอังกฤษ', 'เสียง', 'คำเดียว']},
        'python': {'category': 'ภาษาโปรแกรมมิ่ง', 'hint': ['สัตว์เลื้อยคลาน', 'ชื่อภาษาโปรแกรม', 'งู']},
        'banana': {'category': 'ผลไม้', 'hint': ['สีเหลือง', 'ยาว', 'กินได้']}
    }

    # ประกาศตัวแปรจัดการสถานะแบบ Dictionary
    state = {
        "words": list(word_dict.keys()),
        "secret_word": "",
        "clue": [],
        "score": 0,
        "lives": 3,
        "game_finished": False
    }

    # ฟังก์ชั่นสุ่มคำและสร้าง clue
    def get_new_secret_word():
        if not state["words"]:
            return None, None
        secret = random.choice(state["words"])
        state["words"].remove(secret)
        clue_list = list('?' * len(secret))
        return secret, clue_list

    # เริ่มคำแรกเมื่อเปิดแอป
    state["secret_word"], state["clue"] = get_new_secret_word()

    # --- GUI Components (Flet Controls) ---
    show_status = ft.Text(
        value=f"Score: {state['score']} | Lives: {'❤️' * state['lives']}",
        size=18, color="#2f4f4f", weight=ft.FontWeight.BOLD
    )
    
    show_category = ft.Text(
        value=f"หมวดหมู่: {word_dict[state['secret_word']]['category']}",
        size=26, color="#4682b4", weight=ft.FontWeight.BOLD
    )
    
    show_clue = ft.Text(
        value=' | '.join(state['clue']),
        size=36, color="#2e8b57", weight=ft.FontWeight.BOLD
    )

    hint_title = ft.Text(value="คำใบ้:", size=20, color="#2f4f4f", weight=ft.FontWeight.BOLD)
    
    initial_hints = '\n'.join([f"• {h}" for h in word_dict[state['secret_word']]['hint']])
    show_hints = ft.Text(value=initial_hints, size=16, color="#696969", text_align=ft.TextAlign.CENTER)

    show_result = ft.Text(value="", size=16, color="#ff4500", weight=ft.FontWeight.BOLD)

    # ฟังก์ชันสลับสถานะการเปิดปิดของ UI
    def set_ui_state(disabled: bool):
        textentry.disabled = disabled
        submit_btn.disabled = disabled

    # ฟังก์ชันหลักตอนส่งคำตอบ (ลบ await ออกจาก page.update แล้วเพื่อแก้บั๊ก NoneType)
    async def update_screen(e):
        if state["game_finished"]:
            return

        guess = textentry.value.strip().lower()
        textentry.value = ""  # ล้างข้อความในกล่อง
        
        if not guess:
            show_result.value = "กรุณากรอกตัวอักษร!"
            page.update() 
            return

        secret_word = state["secret_word"]

        if guess in secret_word:
            show_result.value = "✓ ถูกต้อง! ✓"
            show_result.color = "#2e8b57"
            
            # อัพเดตคำใบ้ในตัวแปรโลคอล
            for i in range(len(secret_word)):
                if secret_word[i] == guess:
                    state["clue"][i] = guess
            show_clue.value = ' | '.join(state['clue'])
            win = ''.join(state['clue']) == secret_word
            
            if win:
                state["score"] += 1
                show_clue.value = f"✓ {secret_word} ✓"
                hint_title.value = ""
                show_hints.value = ""
                set_ui_state(True)
                page.update()
                
                # หน่วงเวลาสั้นๆ ให้ผู้เล่นดูคำตอบก่อนขึ้นคำใหม่
                await asyncio.sleep(1.5)
                
                if not state["words"]:
                    state["game_finished"] = True
                    show_clue.value = "🎉 Congrats! คุณชนะแล้ว! 🎉"
                    show_category.value = "เกมจบแล้ว!"
                else:
                    state["secret_word"], state["clue"] = get_new_secret_word()
                    if state["secret_word"]:
                        show_category.value = f"หมวดหมู่: {word_dict[state['secret_word']]['category']}"
                        show_clue.value = ' | '.join(state['clue'])
                        hint_title.value = "คำใบ้:"
                        show_hints.value = '\n'.join([f"• {h}" for h in word_dict[state['secret_word']]['hint']])
                        show_result.value = ""
                        set_ui_state(False)
                    else:
                        state["game_finished"] = True
                        show_clue.value = "🎉 Congrats! คุณชนะแล้ว! 🎉"
                        show_category.value = "เกมจบแล้ว!"
                
                show_status.value = f"Score: {state['score']} | Lives: {'❤️' * state['lives']}"
                page.update()
                return
        else:
            state["lives"] -= 1
            show_result.value = "❌ ผิด! เลือดลด! ❌"
            show_result.color = "#ff4500"
            
            if state["lives"] <= 0:
                state["game_finished"] = True
                show_clue.value = "❌ Game Over! ❌"
                show_category.value = f"คำตอบคือ: {secret_word}"
                hint_title.value = ""
                show_hints.value = ""
                set_ui_state(True)

        show_status.value = f"Score: {state['score']} | Lives: {'❤️' * state['lives']}"
        page.update()

    # รีสตาร์ทเกม
    def restart_game(e):
        state["game_finished"] = False
        state["score"] = 0
        state["lives"] = 3
        state["words"] = list(word_dict.keys())
        state["secret_word"], state["clue"] = get_new_secret_word()
        
        show_status.value = f"Score: {state['score']} | Lives: {'❤️' * state['lives']}"
        show_category.value = f"หมวดหมู่: {word_dict[state['secret_word']]['category']}"
        show_clue.value = ' | '.join(state['clue'])
        hint_title.value = "คำใบ้:"
        show_hints.value = '\n'.join([f"• {h}" for h in word_dict[state['secret_word']]['hint']])
        show_result.value = ""
        
        set_ui_state(False)
        page.update()

    # กล่องข้อความใส่คำตอบ 
    textentry = ft.TextField(
        width=150, text_size=28, text_align=ft.TextAlign.CENTER,
        bgcolor="#fffacd", color="#2f4f4f", border_radius=10,
        border_width=2, border_color="#4682b4", max_length=15,
        on_submit=update_screen
    )

    # ปุ่มส่งคำตอบ
    submit_btn = ft.ElevatedButton(
        content=ft.Text("Submit", color="white", weight=ft.FontWeight.BOLD),
        bgcolor="#32cd32", on_click=update_screen, 
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
    )
    
    # ปุ่มเริ่มใหม่
    restart_btn = ft.ElevatedButton(
        content=ft.Text("Restart", color="white", weight=ft.FontWeight.BOLD),
        bgcolor="#1e90ff", on_click=restart_game, 
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
    )

    # จัดโครงสร้างหน้าจอ (ลบ await ออกจาก page.add เรียบร้อยตามรูปแบบสากลของ Flet)
    page.add(
        ft.Column(
            controls=[
                show_status,
                ft.Divider(height=10, color="transparent"),
                show_category,
                show_clue,
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([hint_title, show_hints], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15, width=400, alignment=ft.Alignment(0, 0) 
                    ),
                    bgcolor="#ffffff" 
                ),
                show_result,
                textentry,
                ft.Row([submit_btn, restart_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
    )

# สั่งรันขึ้นเว็บเบราว์เซอร์อัตโนมัติ
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)