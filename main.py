import os
import telebot
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# .env fayldan token olish
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# Savollar
questions = {
    "A1": [
        {"q": "1️⃣ 'Hello' so‘zining tarjimasi qaysi?", "a": ["Salom", "Rahmat", "Xayr"], "correct": "Salom"},
        {"q": "2️⃣ 'Book' so‘zi qanday tarjima qilinadi?", "a": ["Kitob", "Stol", "Uy"], "correct": "Kitob"},
    ],
    "A2": [
        {"q": "1️⃣ 'I am reading a book' tarjimasi?", "a": ["Men kitob o‘qiyapman", "Men maktabdaman", "Men uxlayapman"], "correct": "Men kitob o‘qiyapman"},
        {"q": "2️⃣ 'She is a teacher' tarjimasi?", "a": ["U o‘qituvchi", "U shifokor", "U talabasi"], "correct": "U o‘qituvchi"},
    ],
}

# Foydalanuvchi state
user_state = {}

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("A1", "A2")
    bot.send_message(
        message.chat.id,
        "👋 Assalomu alaykum!\nIngliz tili darajangizni aniqlash uchun variantlardan birini tanlang:",
        reply_markup=markup
    )

# Level tanlash
@bot.message_handler(func=lambda msg: msg.text in ["A1", "A2"])
def choose_level(message):
    level = message.text
    user_state[message.chat.id] = {"level": level, "q_index": 0, "score": 0}
    bot.send_message(message.chat.id, f"✅ Siz {level} darajasini tanladingiz. Testni boshlaymiz!")
    ask_question(message.chat.id)

# Savol berish
def ask_question(chat_id):
    state = user_state.get(chat_id)
    if not state:
        return

    level = state["level"]
    q_index = state["q_index"]

    if q_index < len(questions[level]):
        q = questions[level][q_index]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for ans in q["a"]:
            markup.add(ans)
        bot.send_message(chat_id, q["q"], reply_markup=markup)
    else:
        # Test tugadi → PDF sertifikat yaratish
        score = state["score"]
        total = len(questions[level])
        level = state["level"]
        name = bot.get_chat(chat_id).first_name

        file_name = f"certificate_{chat_id}.pdf"
        create_certificate(file_name, name, level, score, total)

        with open(file_name, "rb") as pdf:
            bot.send_document(chat_id, pdf, caption="🎓 Sizning sertifikatingiz tayyor!")

        os.remove(file_name)  # vaqtinchalik faylni o‘chirish
        user_state.pop(chat_id)

# PDF yaratish funksiyasi
def create_certificate(filename, name, level, score, total):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Sarlavha
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height-100, "CERTIFICATE")

    # Foydalanuvchi ma’lumotlari
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height-180, f"This is to certify that")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height-220, name)

    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height-270, f"has successfully completed")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-310, f"English Level Test: {level}")

    # Natija
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-360, f"Score: {score}/{total}")

    # Pastki yozuv
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width/2, 100, "Issued by Telegram English Bot")

    c.showPage()
    c.save()

# Javobni tekshirish
@bot.message_handler(func=lambda msg: True)
def handle_answer(message):
    state = user_state.get(message.chat.id)
    if not state:
        bot.send_message(message.chat.id, "Iltimos, /start buyrug‘i bilan boshlang.")
        return

    level = state["level"]
    q_index = state["q_index"]
    q = questions[level][q_index]

    if message.text == q["correct"]:
        bot.send_message(message.chat.id, "✅ To‘g‘ri javob!")
        state["score"] += 1
    else:
        bot.send_message(message.chat.id, f"❌ Noto‘g‘ri. To‘g‘ri javob: {q['correct']}")

    state["q_index"] += 1
    ask_question(message.chat.id)

if __name__ == "__main__":
    print("🤖 Bot ishga tushdi...")
    bot.polling(none_stop=True)
