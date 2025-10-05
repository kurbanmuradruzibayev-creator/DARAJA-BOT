import os
import telebot
from dotenv import load_dotenv

# .env fayldan token olish
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("A1", "A2", "B1", "B2", "C1", "C2")
    bot.send_message(
        message.chat.id,
        "👋 Assalomu alaykum!\nIngliz tili darajangizni aniqlash uchun variantlardan birini tanlang:",
        reply_markup=markup
    )

# Foydalanuvchi javobi
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    if message.text in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        bot.send_message(message.chat.id, f"✅ Sizning tanlovingiz: {message.text}")
    else:
        bot.send_message(message.chat.id, "Iltimos, menyudan darajani tanlang.")

if __name__ == "__main__":
    print("🤖 Bot ishga tushdi...")
    bot.polling(none_stop=True)
