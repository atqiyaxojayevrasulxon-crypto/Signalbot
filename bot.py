import telebot
import random
import json
import time
from telebot import types

TOKEN = "8465880630:AAFZ4vOo317l_bjSDaA64Q14Dh2h3yRAIJQ"
ADMIN_USERNAME = "Muxammadali_7000"
CHANNEL_USERNAME = "galaba_uzb"  # Majburiy obuna

bot = telebot.TeleBot(TOKEN)

# -----------------------
# Foydalanuvchilarni hisoblash
started_users = set()   # /start bosgan foydalanuvchilar
blocked_users = set()   # botni bloklagan foydalanuvchilar

# -----------------------
# Tasdiqlangan foydalanuvchilar va signal tarixini fayldan yuklash
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"verified": {}, "history": {}}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)

data = load_data()  # {"verified": {username: True}, "history": {username: [signals]}}

# -----------------------
# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    started_users.add(message.from_user.username)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("1win APK 📲", "Signal olish 🎰")
    markup.row("Men hamma shartni bajardim ✅", "Ro‘yxatdan o‘tish ✅")
    bot.send_message(
        message.chat.id,
        "Salom! 👋\nBotimizga xush kelibsiz.\nSignal olish uchun ro'yxatdan o'tishingiz kerak.",
        reply_markup=markup
    )

# -----------------------
# Ro'yxatdan o'tish
@bot.message_handler(func=lambda m: m.text == "Ro‘yxatdan o‘tish ✅")
def register_user(message):
    bot.send_message(
        message.chat.id,
        "Ro'yxatdan o'tish uchun ALIWIN1 promokodini ishlating va skrishot yuboring.\n"
        "Admin sizni tasdiqlaganda signal olishingiz mumkin.\n\n"
        "Bot to'liq ishlashi uchun video qo'llanma:\n"
        "1) Telegram orqali: https://t.me/galaba_uzb/1\n"
        "2) YouTube orqali: https://youtu.be/jcrTrYXSreU?si=n5QiTu_BoLkde4wd"
    )

# -----------------------
# Admin foydalanuvchini tasdiqlash
@bot.message_handler(commands=['verify'])
def verify_user(message):
    if message.from_user.username == ADMIN_USERNAME:
        args = message.text.split()
        if len(args) == 2:
            username = args[1].replace("@", "")
            data["verified"][username] = True
            save_data(data)
            bot.send_message(message.chat.id, f"✅ Foydalanuvchi @{username} tasdiqlandi!")
        else:
            bot.send_message(message.chat.id, "❌ Foydalanuvchi username kiritilmadi. /verify <username>")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

# -----------------------
# Admin foydalanuvchini tasdiqdan chiqarish
@bot.message_handler(commands=['unverify'])
def unverify_user(message):
    if message.from_user.username == ADMIN_USERNAME:
        args = message.text.split()
        if len(args) == 2:
            username = args[1].replace("@", "")
            if username in data["verified"]:
                data["verified"].pop(username)
                save_data(data)
                bot.send_message(message.chat.id, f"❌ Foydalanuvchi @{username} tasdiqdan chiqarildi!")
            else:
                bot.send_message(message.chat.id, f"❌ @{username} tasdiqlanmagan foydalanuvchi.")
        else:
            bot.send_message(message.chat.id, "❌ Foydalanuvchi username kiritilmadi. /unverify <username>")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

# -----------------------
# Majburiy obuna tekshirish
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status != 'left'
    except:
        return False

# -----------------------
# Signal olish
@bot.message_handler(func=lambda m: m.text == "Signal olish 🎰")
def send_signal(message):
    username = message.from_user.username
    if not check_subscription(message.from_user.id):
        blocked_users.add(username)
        bot.send_message(
            message.chat.id,
            f"❌ Signal olish uchun kanalimizga majburiy obuna bo‘lishingiz kerak:\nhttps://t.me/{CHANNEL_USERNAME}"
        )
        return

    if data["verified"].get(username):
        wait_msg = bot.send_message(message.chat.id, "⏳ 2…3 soniya, signal aniqlanmoqda…")
        time.sleep(3)

        numbers = random.sample(range(1, 26), 5)
        emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟",
                  "1️⃣1️⃣","1️⃣2️⃣","1️⃣3️⃣","1️⃣4️⃣","1️⃣5️⃣","1️⃣6️⃣","1️⃣7️⃣","1️⃣8️⃣","1️⃣9️⃣",
                  "2️⃣0️⃣","2️⃣1️⃣","2️⃣2️⃣","2️⃣3️⃣","2️⃣4️⃣","2️⃣5️⃣"]
        numbers_emoji = [emojis[n-1] for n in numbers]
        descriptions = ["Kuchli signal", "Aniq signal", "Eng yaxshi raqamlar", "Ishonchli tanlov", "Mines uchun tayyor"]

        signal_text = "🎰 Sizning Mines signal raqamlari:\n"
        for i in range(len(numbers_emoji)):
            signal_text += f"{numbers_emoji[i]} - {descriptions[i % len(descriptions)]}\n"

        # Signal tarixini saqlash (maks 9999)
        if username not in data["history"]:
            data["history"][username] = []
        data["history"][username].append(signal_text)
        if len(data["history"][username]) > 9999:
            data["history"][username].pop(0)
        save_data(data)

        bot.delete_message(message.chat.id, wait_msg.message_id)
        bot.send_message(message.chat.id, signal_text)
    else:
        bot.send_message(
            message.chat.id,
            "❌ Siz hali ro‘yxatdan o‘tmagansiz yoki admin tomonidan tasdiqlanmadingiz!"
        )

# -----------------------
# “Men hamma shartni bajardim” tugmasi
@bot.message_handler(func=lambda m: m.text == "Men hamma shartni bajardim ✅")
def all_done(message):
    bot.send_message(
        message.chat.id,
        f"🎯 Agar siz hamma shartni bajargan bo‘lsangiz, adminga ALIWIN1 promokodi orqali ro'yxatdan o'tgan skrishotni yuboring: @{ADMIN_USERNAME}"
    )

# -----------------------
# 1win APK
@bot.message_handler(func=lambda m: m.text == "1win APK 📲")
def apk_link(message):
    bot.send_message(
        message.chat.id,
        "📲 1win APK faylini yuklab olish uchun rasmiy kanalimizga o'ting:\nhttps://t.me/galaba_uzb/36"
    )

# -----------------------
# Statistikani faqat admin ko‘radi
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.username == ADMIN_USERNAME:
        total_started = len(started_users)
        total_verified = len(data["verified"])
        total_blocked = len(blocked_users)

        history_count = {user: len(sigs) for user, sigs in data["history"].items()}

        text = f"📊 Botga /start bosgan foydalanuvchilar: {total_started}\n"
        text += f"✅ Tasdiqlangan foydalanuvchilar: {total_verified}\n"
        text += f"❌ Botni bloklagan foydalanuvchilar: {total_blocked}\n"
        text += f"📈 Signal tarixlari:\n"

        for user, count in history_count.items():
            display_count = count if count <= 9999 else 9999
            text += f"@{user}: {display_count} signal\n"

        CHUNK_SIZE = 4000
        for i in range(0, len(text), CHUNK_SIZE):
            bot.send_message(message.chat.id, text[i:i+CHUNK_SIZE])
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

# -----------------------
# Botni ishga tushirish
if __name__ == "__main__":
    print("Bot ishga tushmoqda...")
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=60)
        except Exception as e:
            print("Xatolik:", e)
            time.sleep(5)
