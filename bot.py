import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8896810293:AAE-N3t_QP-04OpXUPdjwqTI5j2XuCNW9_8"
# Вказано правильне посилання на ваш GitHub Pages
WEB_APP_URL = "https://osovskijroman7-source.github.io/space-gift-bot/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

MESSAGES = {
    "uk": {
        "disclaimer": (
            "⚠️ **ВАЖЛИВА ІНФОРМАЦІЯ ТА ПРАВИЛА**\n\n"
            "1. **Розважальний характер:** Ця гра створена виключно задля забави та розваги. "
            "Вона не є способом заробітку чи інвестицій.\n\n"
            "2. **Виплати та Подарунки:** Усі виграші виплачуються у вигляді офіційних Подарунків Telegram (Gifts).\n\n"
            "3. **Конвертація в Зірки (Stars):** Ви можете обміняти отриманий подарунок назад у Telegram Stars прямо в налаштуваннях Telegram. "
            "Зверніть увагу, що Telegram стягує внутрішню комісію платформи (близько 15%) за таку конвертацію."
        ),
        "accept_btn": "✅ Я згоден і розумію правила",
        "menu": "🎮 **Головне меню:**\nНатисніть кнопку нижче, щоб відкрити космічну вежу.",
        "rules_btn": "📜 Правила",
        "play_btn": "🌌 Грати у Вежу 6x6",
        "back_btn": "⬅️ Назад"
    },
    "en": {
        "disclaimer": (
            "⚠️ **IMPORTANT INFORMATION & RULES**\n\n"
            "1. **For Entertainment Only:** This game is made purely for fun and entertainment.\n\n"
            "2. **Payouts & Gifts:** All winnings are paid out in official Telegram Gifts.\n\n"
            "3. **Conversion to Stars:** You can convert gifts back into Telegram Stars in Telegram settings (~15% fee)."
        ),
        "accept_btn": "✅ I agree and understand",
        "menu": "🎮 **Main Menu:**",
        "rules_btn": "📜 Rules",
        "play_btn": "🌌 Play Tower 6x6",
        "back_btn": "⬅️ Back"
    },
    "es": {
        "disclaimer": (
            "⚠️ **INFORMACIÓN IMPORTANTE Y REGLAS**\n\n"
            "1. Solo para entretenimiento.\n"
            "2. Pagos en Regalos oficiales de Telegram.\n"
            "3. Conversión a Estrellas en la configuración de Telegram (~15% comisión)."
        ),
        "accept_btn": "✅ Acepto y entiendo",
        "menu": "🎮 **Menú Principal:**",
        "rules_btn": "📜 Reglas",
        "play_btn": "🌌 Jugar Torre 6x6",
        "back_btn": "⬅️ Volver"
    },
    "de": {
        "disclaimer": (
            "⚠️ **WICHTIGE INFORMATIONEN UND REGELN**\n\n"
            "1. Nur zur Unterhaltung.\n"
            "2. Auszahlungen als Telegram-Geschenke.\n"
            "3. Umwandlung in Sterne in den Einstellungen (~15% Gebühr)."
        ),
        "accept_btn": "✅ Ich stimme zu",
        "menu": "🎮 **Hauptmenü:**",
        "rules_btn": "📜 Regeln",
        "play_btn": "🌌 Turm 6x6 Spielen",
        "back_btn": "⬅️ Zurück"
    },
    "fr": {
        "disclaimer": (
            "⚠️ **INFORMATIONS IMPORTANTE ET RÈGLES**\n\n"
            "1. Pour le divertissement uniquement.\n"
            "2. Gains sous forme de Cadeaux Telegram.\n"
            "3. Conversion en Étoiles possible (~15% commission)."
        ),
        "accept_btn": "✅ J'accepte et je comprends",
        "menu": "🎮 **Menu Principal :**",
        "rules_btn": "📜 Règles",
        "play_btn": "🌌 Jouer à la Tour 6x6",
        "back_btn": "⬅️ Retour"
    },
    "tr": {
        "disclaimer": (
            "⚠️ **ÖNEMLİ BİLGİ VE KURALLAR**\n\n"
            "1. Sadece Eğlence İçin.\n"
            "2. Ödemeler resmi Telegram Hediyeleri şeklindedir.\n"
            "3. Yıldızlara dönüştürme yapılabilir (~%15 komisyon)."
        ),
        "accept_btn": "✅ Kabul ediyorum",
        "menu": "🎮 **Ana Menü:**",
        "rules_btn": "📜 Kurallar",
        "play_btn": "🌌 Kule 6x6 Oyna",
        "back_btn": "⬅️ Geri"
    }
}

def init_db():
    with sqlite3.connect("game_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en'
            )
        """)
        conn.commit()

def set_user_language(user_id: int, lang: str):
    with sqlite3.connect("game_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, language) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
        """, (user_id, lang))
        conn.commit()

def get_user_language(user_id: int) -> str:
    with sqlite3.connect("game_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else "en"

def get_language_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr")]
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
    await message.answer(
        "🌐 Please select your language / Будь ласка, оберіть мову:",
        reply_markup=get_language_keyboard()
    )

@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id

    set_user_language(user_id, lang_code)
    texts = MESSAGES.get(lang_code, MESSAGES["en"])

    accept_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts["accept_btn"], callback_data="accept_rules")]
    ])

    await callback.message.edit_text(texts["disclaimer"], reply_markup=accept_kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "accept_rules")
@dp.callback_query(F.data == "back_to_menu")
async def show_main_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    texts = MESSAGES.get(lang, MESSAGES["en"])

    await callback.message.edit_text(texts["menu"], reply_markup=get_menu_keyboard(lang), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "show_rules")
async def show_rules_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    texts = MESSAGES.get(lang, MESSAGES["en"])

    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts["back_btn"], callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(texts["disclaimer"], reply_markup=back_kb, parse_mode="Markdown")
    await callback.answer()

async def main():
    init_db()
    print("Бот запущений та готовий до роботи!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
