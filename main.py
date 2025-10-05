import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Boshlanish komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["A1", "A2"], ["B1", "B2"], ["C1", "C2"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum! 👋\nIngliz tili darajangizni aniqlash uchun birini tanlang:",
        reply_markup=reply_markup
    )

# Daraja tanlash
async def level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_level = update.message.text
    await update.message.reply_text(f"Siz tanlagan daraja: {user_level}", reply_markup=ReplyKeyboardRemove())

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, level))

    app.run_polling()

if __name__ == "__main__":
    main()
