import asyncio
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

BOT_TOKEN = "8896810293:AAE-N3t_QP-040pXUPdjwqTI"
# Замініть на ваше реальне посилання на Render
WEB_APP_URL = "https://space-gift-bot.onrender.com"
WALLET_ADDRESS = "UQBLhA0jSJthqPS8UNRAvuq6HMUMsM56vbQZtTPCPhKEyPM5"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# База даних
def init_db():
    with sqlite3.connect("game_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en',
                balance INTEGER DEFAULT 0,
                wallet TEXT DEFAULT ''
            )
        """)
        conn.commit()

def save_user(user_id: int, lang: str, wallet: str):
    with sqlite3.connect("game_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, language, wallet) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language = ?, wallet = ?
        """, (user_id, lang, wallet, lang, wallet))
        conn.commit()

def get_user(user_id: int):
    with sqlite3.connect("game_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT language, balance, wallet FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {"language": row[0], "balance": row[1], "wallet": row[2]}
        return {"language": "en", "balance": 0, "wallet": ""}

# Тексти та переклади
MESSAGES = {
    "uk": {
        "disclaimer": (
            "⚠️ **ВАЖЛИВА ІНФОРМАЦІЯ ТА ПРАВИЛА**\n"
            "1. **Розважальний характер:** Ця гра створена виключно задля забави та розваги.\n"
            "2. **Виплати та Подарунки:** Усі виграші виплачуються у вигляді офіційних Подарунків Telegram (Gifts).\n"
            "3. **Конвертація в Зірки (Stars):** Ви можете обміняти отриманий подарунок назад у Telegram Stars."
        ),
        "accept_btn": "✅ Я згоден і розумію правила",
        "menu": f"🎮 **Головне меню:**\nГаманець: `{WALLET_ADDRESS}`\nНатисніть кнопку нижче, щоб відкрити Космічну Вежу 6х6.",
        "rules_btn": "📜 Правила",
        "play_btn": "🚀 Грати у Вежу 6х6",
        "back_btn": "⬅️ Назад"
    },
    "en": {
        "disclaimer": (
            "⚠️ **IMPORTANT INFORMATION & RULES**\n"
            "1. **For Entertainment Only:** This game is created for fun.\n"
            "2. **Payouts & Gifts:** All winnings are paid as official Telegram Gifts.\n"
            "3. **Conversion to Stars:** You can convert gifts back to Telegram Stars."
        ),
        "accept_btn": "✅ I agree and understand",
        "menu": f"🎮 **Main Menu:**\nWallet: `{WALLET_ADDRESS}`\nClick the button below to open Space Tower 6x6.",
        "rules_btn": "📜 Rules",
        "play_btn": "🚀 Play Tower 6x6",
        "back_btn": "⬅️ Back"
    }
}

# Телеграм хендлери
@dp.message(Command("start"))
async def start_command(message: types.Message):
    init_db()
    buttons = [
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ]
    await message.answer(
        "🌐 Please select your language / Будь ласка, оберіть мову:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    save_user(user_id, lang_code, WALLET_ADDRESS)
    
    texts = MESSAGES.get(lang_code, MESSAGES["en"])
    accept_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts["accept_btn"], callback_data="accept_rules")]
    ])
    await callback.message.edit_text(texts["disclaimer"], reply_markup=accept_kb)
    await callback.answer()

@dp.callback_query(F.data.in_({"accept_rules", "back_menu"}))
async def show_main_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user(user_id)
    lang = user_data["language"]
    texts = MESSAGES.get(lang, MESSAGES["en"])
    
    buttons = [
        [InlineKeyboardButton(text=texts["play_btn"], web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text=texts["rules_btn"], callback_data="show_rules")]
    ]
    await callback.message.edit_text(texts["menu"], reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "show_rules")
async def show_rules_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user(user_id)
    lang = user_data["language"]
    texts = MESSAGES.get(lang, MESSAGES["en"])
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts["back_btn"], callback_data="back_menu")]
    ])
    await callback.message.edit_text(texts["disclaimer"], reply_markup=back_kb, parse_mode="Markdown")
    await callback.answer()

# FastAPI маршрут для красивого інтерфейсу міні-додатка (Сітка 6х6 + космос)
@app.get("/", response_class=HTMLResponse)
async def serve_webapp():
    return """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Space Gift - Вежа 6х6</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {
                margin: 0; padding: 0;
                background: radial-gradient(circle at center, #1b1b3a 0%, #0b091a 100%);
                color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex; flex-direction: column; align-items: center; min-height: 100vh; overflow-x: hidden;
            }
            .stars {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: transparent url('https://www.script-tutorials.com/demos/360/images/stars.png') repeat;
                z-index: -1; opacity: 0.6;
            }
            .container { width: 100%; max-width: 400px; padding: 20px; box-sizing: border-box; text-align: center; }
            h1 {
                font-size: 24px; margin: 10px 0;
                background: linear-gradient(45deg, #00f2fe, #4facfe);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                text-shadow: 0 0 15px rgba(79, 172, 254, 0.4);
            }
            .balance-card {
                background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px; padding: 15px; margin: 15px 0; backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }
            .balance-title { font-size: 14px; color: #a0aec0; text-transform: uppercase; letter-spacing: 1px; }
            .balance-value { font-size: 32px; font-weight: bold; color: #ffd700; margin: 5px 0; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
            .grid-tower {
                display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px; margin: 20px 0;
                background: rgba(15, 12, 41, 0.6); padding: 10px; border-radius: 16px; border: 1px solid rgba(79, 172, 254, 0.2);
            }
            .cell {
                aspect-ratio: 1; background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02));
                border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; display: flex; align-items: center;
                justify-content: center; font-size: 18px; cursor: pointer; transition: all 0.2s ease; user-select: none;
            }
            .cell:active { transform: scale(0.9); background: rgba(79, 172, 254, 0.3); }
            .cell.opened { background: rgba(0, 242, 254, 0.2); border-color: #00f2fe; box-shadow: 0 0 10px rgba(0, 242, 254, 0.4); }
            .hint { font-size: 13px; color: #a0aec0; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="stars"></div>
        <div class="container">
            <h1>🚀 Space Gift 6x6</h1>
            <div class="balance-card">
                <div class="balance-title">Ваш Баланс</div>
                <div class="balance-value" id="balance">0</div>
                <div style="font-size: 11px; color: #718096;">Гаманець: UQBL...yPM5</div>
            </div>
            <div class="grid-tower" id="grid"></div>
            <div class="hint">Тисни на комірки вежі, збирай космічні подарунки та збільшуй баланс!</div>
        </div>
        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();
            let score = 0;
            const gridElement = document.getElementById('grid');
            const balanceElement = document.getElementById('balance');

            for (let i = 0; i < 36; i++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.innerHTML = '🎁';
                cell.addEventListener('click', () => {
                    if (!cell.classList.contains('opened')) {
                        cell.classList.add('opened');
                        cell.innerHTML = '⭐';
                        score += 10;
                        balanceElement.innerText = score;
                        if (tg.HapticFeedback) {
                            tg.HapticFeedback.impactOccurred('medium');
                        }
                    }
                });
                gridElement.appendChild(cell);
            }
        </script>
    </body>
    </html>
    """

# Фоновий запуск бота разом із сервером
async def run_bot():
    init_db()
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())
