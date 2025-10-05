import os
import telebot
from dotenv import load_dotenv

# .env fayldan token olish
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# Har bir daraja uchun savollar
questions = {
    "A1": [
        {"q": "1️⃣ 'Hello' so‘zining tarjimasi qaysi?", "a": ["Salom", "Rahmat", "Xayr"], "correct": "Salom"},
        {"q": "2️⃣ 'Book' so‘zi qanday tarjima qilinadi?", "a": ["Kitob", "Stol", "Uy"], "correct": "Kitob"},
    ],
    "A2": [
        {"q": "1️⃣ 'I am reading a book' tarjimasi?", "a": ["Men kitob o‘qiyapman", "Men maktabdaman", "Men uxlayapman"], "correct": "Men kitob o‘qiyapman"},
        {"q": "2️⃣ 'She is a teacher' tarjimasi?", "a": ["U o‘qituvchi", "U shifokor", "U talabasi"], "correct": "U o‘qituvchi"},
    ],
    "B1": [
        {"q": "1️⃣ 'If I were you, I ...' jumlasini to‘ldiring:", "a": ["would go", "go", "going"], "correct": "would go"},
        {"q": "2️⃣ 'He has been working ... morning.'", "a": ["since", "for", "at"], "correct": "since"},
    ],
    "B2": [
        {"q": "1️⃣ 'Despite ... tired, he continued working.'", "a": ["being", "to be", "be"], "correct": "being"},
        {"q": "2️⃣ 'She succeeded ... passing the exam.'", "a": ["in", "on", "at"], "correct": "in"},
    ],
    "C1": [
        {"q": "1️⃣ 'Hardly had I arrived ... it started to rain.'", "a": ["when", "than", "then"], "correct": "when"},
        {"q": "2️⃣ 'No sooner ... the phone rang.'", "a": ["had he left", "he had left", "was he leaving"], "correct": "had he left"},
    ],
    "C2": [
        {"q": "1️⃣ 'Were it not for your help, ...'", "a": ["I would have failed", "I fail", "I will fail"], "correct": "I would have failed"},
        {"q": "2️⃣ 'Scarcely had she spoken ...'", "a": ["when he interrupted", "than he interrupted", "then he interrupted"], "correct": "when he interrupted"},
    ],
}

# Foydalanuvchi tanlovi va test jarayonini saqlash uchun
user_state = {}

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

# Tanlovni qayta ishlash
@bot.message_handler(func=lambda msg: msg.text in ["A1", "A2", "B1", "B2", "C1", "C2"])
def choose_level(message):
    level = message.text
    user_state[message.chat.id] = {"level": level, "q_index": 0, "score": 0}
    bot.send_message(message.chat.id, f"✅ Siz {level} darajasini tanladingiz. Keling, testni boshlaymiz!")
    ask_question(message.chat.id)

# Savol berish funksiyasi
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
        # Test tugadi
        score = state["score"]
        total = len(questions[level])
        level = state["level"]
        name = bot.get_chat(chat_id).first_name  # foydalanuvchi ismini olish

        # "CERTIFICATE" chiqarish
        cert_text = (
            "🎓 *CERTIFICATE*\n\n"
            f"👤 Ism: *{name}*\n"
            f"📘 Level: *{level}*\n"
            f"📊 Natija: *{score}/{total}*\n\n"
            "✅ Tabriklaymiz! Siz muvaffaqiyatli testdan o'tdingiz."
        )

        bot.send_message(chat_id, cert_text, parse_mode="Markdown")
        user_state.pop(chat_id)

# Javoblarni tekshirish
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
