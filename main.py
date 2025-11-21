from flask import Flask, request
import telebot
import os
import json
import time
import random
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

DB_FILE = "users.json"

# ===== Khởi tạo file nếu chưa có =====
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

# ===== Hàm lưu user =====
def save_user(user):
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data[str(user.id)] = {
        "username": user.username or "Không có",
        "fullname": user.full_name or "Không có"
    }

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ===== Inline buttons =====
button1 = InlineKeyboardButton(text="Nhiệm vụ 1", callback_data="nhiemvu1")
button2 = InlineKeyboardButton(text="Nhiệm vụ 2", callback_data="nhiemvu2")
inline_keyboard = InlineKeyboardMarkup(row_width=2)
inline_keyboard.add(button1, button2)

# ===== Danh sách mã nhiệm vụ 1 =====
MA_NHIEMVU1 = [
    "869949509369",
    "865846957325",
    "865687404322",
    "869451348757",
    "861327734371",
    "862847379139",
    "869873460440",
    "869142727421",
    "868700995822",
    "865367113247",
    "867157217526",
    "862758227609",
    "863868586275",
    "864082200631",
    "865119726753",
    "865363029118",
]

user_last_task1 = {}  # {user_id: timestamp}

# ===== Flask app =====
app = Flask(__name__)

# ===== Webhook endpoint =====
@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    json_data = request.get_json()
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

# ===== Test endpoint =====
@app.route("/")
def index():
    return "Bot is running!", 200

# ===== Bot handlers =====
@bot.message_handler(commands=['start'])
def start_bot(message):
    save_user(message.from_user)
    text = (
        f"🎉🎁 CHÀO MỪNG -{message.from_user.full_name}- ĐẾN VỚI CODENETWIN! 🎁🎉\n\n"
        "Dưới đây là các lệnh bạn có thể dùng:\n"
        "📝 /nhiemvu - Xem danh sách nhiệm vụ đang HOT \n"
        "🪄 /doithuong - Nhận giftcode random thông qua các nhiệm vụ có sẵn.\n"
        "📖 /help - Xem hướng dẫn và giải đáp thắc mắc.\n\n"
        "✨ Chúc bạn may mắn và vui vẻ khi sử dụng bot! ✨"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['nhiemvu', 'gift'])
def fiststep_bot(message):
    save_user(message.from_user)
    bot.reply_to(message, "🎉 Chọn một chức năng bên dưới để bắt đầu:", reply_markup=inline_keyboard)

@bot.callback_query_handler(func=lambda call: True)
def query_bot(call):
    save_user(call.from_user)
    user_id = call.from_user.id
    now = time.time()

    if call.data == "nhiemvu1":
        bot.answer_callback_query(call.id, text="Bạn đã chọn Nhiệm Vụ 1 ✅", show_alert=False)
        code_chosen = random.choice(MA_NHIEMVU1)
        link_chosen = f"https://vnshares.com/r/{code_chosen}"
        text = (
            f"📝 Hướng dẫn thực hiện Nhiệm Vụ 1:\n\n"
            f"1️⃣ Truy cập link: {link_chosen}\n"
            "2️⃣ Đăng ký tài khoản\n"
            "3️⃣ Nhập mã xác nhận từ email\n"
            "4️⃣ Hoàn thành nhiệm vụ 🎉"
        )
        bot.send_message(call.message.chat.id, text)
        user_last_task1[user_id] = now

    elif call.data == "nhiemvu2":
        if user_id in user_last_task1:
            elapsed = now - user_last_task1[user_id]
            if elapsed < 90:
                remaining = int(90 - elapsed)
                bot.answer_callback_query(
                    call.id,
                    text=f"⏳ Vui lòng đợi {remaining} giây trước khi làm Nhiệm Vụ 2",
                    show_alert=True
                )
                return
        bot.answer_callback_query(
            call.id,
            text="⏳ Hiện tại nhiệm vụ chưa khả dụng! Vui lòng thử lại sau 3-5 phút ⏳",
            show_alert=True
        )

@bot.message_handler(commands=['doithuong'])
def thirdstep_bot(message):
    bot.reply_to(message, "❌ Vui lòng hoàn thành ít nhất 2 nhiệm vụ để đổi code.")

@bot.message_handler(commands=['help'])
def thirdstep_bot(message):
    bot.reply_to(message, "Vui lòng liên hệ contact sau để được hỗ trợ: @accountcvk")

@bot.message_handler(commands=['users'])
def show_users(message):
    admin_id = 5617674327
    if message.from_user.id != admin_id:
        bot.reply_to(message, "❌ Bạn không có quyền xem danh sách người dùng.")
        return
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        bot.reply_to(message, "Chưa có ai dùng bot!")
        return
    text = "📜 Danh sách người dùng bot:\n\n"
    for uid, info in data.items():
        username = info.get('username', 'Không có')
        fullname = info.get('fullname', 'Không có')
        text += f"• ID: {uid} — @{username} ({fullname})\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: True)
def final_bot(message):
    bot.send_message(message.chat.id, "⚠️ Yêu cầu không hợp lệ! Vui lòng chọn lại một tùy chọn hợp lệ.")

# ===== Chạy Flask =====
if __name__ == "__main__":
    # Xoá webhook cũ
    bot.remove_webhook()
    # Đặt webhook tới URL Render của bạn
    bot.set_webhook(url=f"https://telegram-4-q1wt.onrender.com/{TOKEN}")
    # Chạy Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


