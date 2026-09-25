import asyncio
import sqlite3
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

BOT_TOKEN = "8778529455:AAGxKB1IaXbRyrFX4RBO0GFfUWiENI5hhFo"
WEB_APP_URL = "https://space-gift-bot.onrender.com"
WALLET_ADDRESS = "UQBLhA0jSJthqPS8UNRAvuq6HMUMsM56vbQZtTPCPhKEyPM5"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

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

MESSAGES = {
    "uk": {
        "disclaimer": (
            "⚠️ **ПРАВИЛА ТА УМОВИ ГРИ**\n"
            "1. **Депозит:** Для участі в грі та відкриття комірок на балансі необхідний активний депозит.\n"
            "2. **Ризик (Бомби):** На полі заховані міни (💣). Якщо натрапите на бомбу — гра закінчується, а ставка згорає.\n"
            "3. **Виплати:** Виграші виплачуються у вигляді офіційних Telegram Gifts."
        ),
        "accept_btn": "✅ Поповнити баланс і грати",
        "menu": f"🎮 **Головне меню вежі 6х6:**\nГаманець для поповнення: `{WALLET_ADDRESS}`\nЗробіть депозит для активації гри нижче.",
        "rules_btn": "📜 Правила",
        "play_btn": "🚀 Відкрити Космічну Вежу",
        "deposit_btn": "💳 Зробити депозит",
        "back_btn": "⬅️ Назад"
    },
    "en": {
        "disclaimer": (
            "⚠️ **RULES & TERMS**\n"
            "1. **Deposit:** Active deposit is required to play and open cells.\n"
            "2. **Risk (Bombs):** Bombs (💣) are hidden on the grid. Hit one and lose your bet.\n"
            "3. **Payouts:** Winnings are paid as official Telegram Gifts."
        ),
        "accept_btn": "✅ Deposit & Play",
        "menu": f"🎮 **Tower 6x6 Main Menu:**\nDeposit Wallet: `{WALLET_ADDRESS}`\nMake a deposit to activate the game below.",
        "rules_btn": "📜 Rules",
        "play_btn": "🚀 Open Space Tower",
        "deposit_btn": "💳 Make Deposit",
        "back_btn": "⬅️ Back"
    }
}

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
        [InlineKeyboardButton(text=texts["deposit_btn"], callback_data="make_deposit")],
        [InlineKeyboardButton(text=texts["rules_btn"], callback_data="show_rules")]
    ]
    await callback.message.edit_text(texts["menu"], reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "make_deposit")
async def deposit_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user(user_id)
    lang = user_data["language"]
    
    text = (
        "💳 **Поповнення депозиту:**\n\n"
        f"Надішліть TON або зірки на гаманець:\n`{WALLET_ADDRESS}`\n\n"
        "Після переказу ваш баланс автоматично оновиться, і ви зможете грати у вежу!"
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
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

@app.get("/", response_class=HTMLResponse)
async def serve_webapp():
    return """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Space Gift - Вежа 6х6 з мінами</title>
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
            .cell.opened-star { background: rgba(0, 242, 254, 0.2); border-color: #00f2fe; box-shadow: 0 0 10px rgba(0, 242, 254, 0.4); }
            .cell.opened-bomb { background: rgba(255, 0, 0, 0.3); border-color: #ff4d4d; box-shadow: 0 0 10px rgba(255, 0, 0, 0.5); }
            .hint { font-size: 13px; color: #a0aec0; margin-top: 15px; }
            .btn-restart {
                background: linear-gradient(45deg, #00f2fe, #4facfe); border: none; border-radius: 12px;
                color: #fff; padding: 10px 20px; font-weight: bold; cursor: pointer; margin-top: 10px; display: none;
            }
        </style>
    </head>
    <body>
        <div class="stars"></div>
        <div class="container">
            <h1>🚀 Space Tower 6x6</h1>
            <div class="balance-card">
                <div class="balance-title">Депозит / Баланс</div>
                <div class="balance-value" id="balance">100</div>
                <div style="font-size: 11px; color: #718096;">Обережно: на полі є бомби! 💣</div>
            </div>
            <div class="grid-tower" id="grid"></div>
            <div class="hint" id="status-text">Обирай комірки обережно, оминай бомби та збирай зірки!</div>
            <button class="btn-restart" id="restartBtn" onclick="initGame()">Спробувати знову</button>
        </div>
        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();
            
            let balance = 100; // Початковий тестовий баланс (депозит)
            let gameOver = false;
            let bombs = [];
            const gridElement = document.getElementById('grid');
            const balanceElement = document.getElementById('balance');
            const statusText = document.getElementById('status-text');
            const restartBtn = document.getElementById('restartBtn');

            function initGame() {
                gridElement.innerHTML = '';
                gameOver = false;
                restartBtn.style.display = 'none';
                statusText.innerText = 'Обирай комірки обережно, оминай бомби та збирай зірки!';
                
                // Рандомно розкидаємо 6 бомб по 36 комірках за допомогою випадкового рандому
                bombs = [];
                while(bombs.length < 6) {
                    let r = Math.floor(Math.random() * 36);
                    if(!bombs.includes(r)) bombs.push(r);
                }

                for (let i = 0; i < 36; i++) {
                    const cell = document.createElement('div');
                    cell.classList.add('cell');
                    cell.dataset.index = i;
                    cell.innerHTML = '❓';
                    cell.addEventListener('click', () => handleCellClick(cell, i));
                    gridElement.appendChild(cell);
                }
            }

            function handleCellClick(cell, index) {
                if (gameOver || cell.classList.contains('opened-star') || cell.classList.contains('opened-bomb')) return;

                if (balance < 10) {
                    statusText.innerText = '⚠️ Недостатньо коштів на депозиті! Поповніть баланс через бота.';
                    return;
                }

                balance -= 5; // вартість спроби
                balanceElement.innerText = balance;

                if (bombs.includes(index)) {
                    // Натрапив на бомбу! Рандом спрацював проти гравця
                    cell.classList.add('opened-bomb');
                    cell.innerHTML = '💣';
                    gameOver = true;
                    statusText.innerText = '💥 Ви натрапили на бомбу! Гра закінчена.';
                    if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('error');
                    revealAll();
                } else {
                    // Знайшов подарунок/зірку
                    cell.classList.add('opened-star');
                    cell.innerHTML = '⭐';
                    balance += 15; // виграш
                    balanceElement.innerText = balance;
                    statusText.innerText = '🎉 Чудово! Ви знайшли космічну зірку (+15)!';
                    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
                }
            }

            function revealAll() {
                const cells = document.querySelectorAll('.cell');
                cells.forEach((c, idx) => {
                    if (bombs.includes(idx)) {
                        c.classList.add('opened-bomb');
                        c.innerHTML = '💣';
                    }
                });
                restartBtn.style.display = 'block';
            }

            initGame();
        </script>
    </body>
    </html>
    """

async def run_bot():
    init_db()
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())
