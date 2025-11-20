from flask import Flask, request
import telebot
import os

# Lấy token từ biến môi trường trên Render
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

# ===== Run Flask app =====
if __name__ == "__main__":
    # Xoá bất kỳ webhook cũ nào
    bot.remove_webhook()
    # Đặt webhook tới URL Render của bạn
    bot.set_webhook(url=f"https://YOUR-RENDER-URL/{TOKEN}")
    
    # Chạy Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
