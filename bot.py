import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

BOT_TOKEN = "8896810293:AAE-N3t_QP-040pXUPdjwqTI"
# Замініть на ваше актуальне посилання з Render, коли розгорнете вебчастину
WEB_APP_URL = "https://space-gift-bot.onrender.com"
WALLET_ADDRESS = "UQBLhA0jSJthqPS8UNRAvuq6HMUMsM56vbQZtTPCPhKEyPM5"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

MESSAGES = {
    "uk": {
        "disclaimer": (
            "⚠️ **ВАЖЛИВА ІНФОРМАЦІЯ ТА ПРАВИЛА**\n"
            "1. **Розважальний характер:** Ця гра створена виключно задля забави та розваги.\n"
            "2. **Виплати та Подарунки:** Усі виграші виплачуються у вигляді офіційних Подарунків Telegram (Gifts).\n"
            "3. **Конвертація в Зірки (Stars):** Ви можете обміняти отриманий подарунок назад у Telegram Stars."
        ),
        "accept_btn": "✅ Я згоден і розумію правила",
        "menu": f"🎮 **Головне меню:**\nВаш гаманець: `{WALLET_ADDRESS}`\nНатисніть кнопку нижче, щоб відкрити Космічну Вежу 6х6.",
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

def get_language_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_menu_keyboard(lang: str):
    texts = MESSAGES.get(lang, MESSAGES["en"])
    buttons = [
        [InlineKeyboardButton(text=texts["play_btn"], web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text=texts["rules_btn"], callback_data="show_rules")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    init_db()
    await message.answer(
        "🌐 Please select your language / Будь ласка, оберіть мову:",
        reply_markup=get_language_keyboard()
    )

@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    # Зберігаємо мову та прикріплюємо гаманець користувача
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
    
    await callback.message.edit_text(texts["menu"], reply_markup=get_menu_keyboard(lang), parse_mode="Markdown")
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

async def main():
    init_db()
    print("Бот запущений та готовий до роботи!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
