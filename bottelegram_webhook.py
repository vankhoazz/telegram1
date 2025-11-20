from flask import Flask, request
import telebot
import os
import time

# Lấy token từ biến môi trường trên Render (bắt buộc phải đặt trong Render Environment)
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

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

# ===== Bot commands =====
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "🎉 Bot is active via Webhook! 🎉")

# ===== Chạy app (chỉ chạy khi deploy thật, không cần hard-code URL nữa) =====
if __name__ == "__main__":
    # Tự động lấy URL của Render (Render cung cấp sẵn biến này)
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        # Nếu vì lý do gì đó không có thì dùng URL hiện tại của bạn làm dự phòng
        render_url = "https://telegram-webhook-9s6d.onrender.com"

    webhook_url = f"{render_url}/{TOKEN}"
    
    print(f"Đang đặt webhook: {webhook_url}")

    # Xóa webhook cũ trước
    bot.remove_webhook()
    time.sleep(2)  # Đure an toàn

    # Đặt webhook mới
    success = bot.set_webhook(url=webhook_url)
    
    if success:
        print("✅ Webhook đã được đặt thành công!")
    else:
        print("❌ Lỗi khi đặt webhook, kiểm tra lại token hoặc URL")

    # Chạy Flask server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
