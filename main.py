"""
Oddiy Telegram bot — "Level Checker" (A1-C2).
Ishga tushirish:
1) TELEGRAM BOT TOKEN ni @BotFather orqali oling.
2) TOKEN ni Muhit o'zgaruvchisi sifatida yoki .env faylga yozing.
3) pip install -r requirements.txt (requirements: python-telegram-bot)

Bu bot 12 ta savol beradi (multiple-choice). Foydalanuvchi javoblariga qarab CEFR darajasini taxminiy hisoblab beradi.

Muallif: Siz — GitHubga joylashga mos oddiy va tushunarli kod.
"""

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import os

# --- SOZLAMALAR ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')  # muhitdan o'qishni tavsiya qilinadi

# State for ConversationHandler
ASKING = 1

# Savollar ro'yxati: har bir element (savol, [variantlar], to'g'ri_index)
QUESTIONS = [
    ("1) Choose the correct sentence:", ["I am go to school.", "I go to school.", "I going to school."], 1),
    ("2) Pick the correct past form of 'eat':", ["eated", "ate", "eaten"], 1),
    ("3) Which is a synonym of 'big'?:", ["small", "large", "thin"], 1),
    ("4) Choose the correct question:", ["Where you are?", "Where are you?", "You are where?"], 1),
    ("5) Complete: I ___ a book now.", ["read", "am reading", "reads"], 1),
    ("6) Which word is a verb?:", ["beautiful", "run", "happiness"], 1),
    ("7) Past participle of 'go' is:", ["goed", "gone", "went"], 1),
    ("8) Choose the correct article: ___ apple", ["A", "An", "The"], 1),
    ("9) Which number is written correctly?:", ["fifty-two", "fifty two-two", "fiftytwo"], 0),
    ("10) Choose correct preposition: She lives ___ London.", ["in", "on", "at"], 0),
    ("11) Which sentence is conditional (possible)?", ["If I see him, I will tell him.", "If I saw him, I would tell him.", "If I will see him, I tell him."], 0),
    ("12) Choose the best word to complete: He is the ___ player in the team.", ["good", "better", "best"], 2),
]

# Thresholds: score -> CEFR suggestion
# 0-2 A1, 3-5 A2, 6-7 B1, 8-9 B2, 10-11 C1, 12 C2
def level_from_score(score: int) -> str:
    if score <= 2:
        return "A1 (Beginner)"
    if score <= 5:
        return "A2 (Elementary)"
    if score <= 7:
        return "B1 (Intermediate)"
    if score <= 9:
        return "B2 (Upper-Intermediate)"
    if score <= 11:
        return "C1 (Advanced)"
    return "C2 (Proficiency)"

# /start komandi
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}!\n\n"
        "Men oddiy ingliz tili darajasini aniqlaydigan botman. Sizga 12 ta savol beraman.\n"
        "Har bir savolda bitta tugmani tanlang. Boshlash uchun /begin buyrug'ini bering."
    )
    return ConversationHandler.END

# /begin bosilganda testni boshlash
def begin(update: Update, context: CallbackContext) -> int:
    # initialize user data
    context.user_data['score'] = 0
    context.user_data['index'] = 0
    update.message.reply_text("Test boshlanadi — har bir savolda variantlardan birini tanlang.")
    return ask_question(update, context)

# Savolni yuborish
def ask_question(update: Update, context: CallbackContext) -> int:
    idx = context.user_data.get('index', 0)
    if idx >= len(QUESTIONS):
        # test tugadi
        score = context.user_data.get('score', 0)
        level = level_from_score(score)
        update.message.reply_text(
            f"Test tugadi!\nSizning natijangiz: {score}/{len(QUESTIONS)}\nTaxminiy CEFR darajasi: {level}",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    q, options, _ = QUESTIONS[idx]
    # Keyboard
    keyboard = [[opt] for opt in options]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(q, reply_markup=reply_markup)
    return ASKING

# Foydalanuvchi javob berganda
def handle_answer(update: Update, context: CallbackContext) -> int:
    text = update.message.text.strip()
    idx = context.user_data.get('index', 0)

    # Safety: agar test tugagan bo'lsa qayta boshlash
    if idx >= len(QUESTIONS):
        return ConversationHandler.END

    q, options, correct_idx = QUESTIONS[idx]
    # topilgan varianti indeksini aniqlash
    try:
        chosen_idx = options.index(text)
    except ValueError:
        # foydalanuvchi variantlardan tashqari yozdi
        update.message.reply_text("Iltimos, variantlardan birini tanlang (klik qiling).")
        return ASKING

    if chosen_idx == correct_idx:
        context.user_data['score'] = context.user_data.get('score', 0) + 1

    context.user_data['index'] = idx + 1
    return ask_question(update, context)

# /cancel
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Test bekor qilindi.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler('begin', begin)],
        states={
            ASKING: [MessageHandler(Filters.text & ~Filters.command, handle_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(conv)

    print('Bot ishga tushmoqda...')
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
