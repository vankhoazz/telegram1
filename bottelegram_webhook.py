from flask import Flask, request
import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")  # Lấy token từ biến môi trường trên Render
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    json_data = request.get_json()
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!", 200

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello! Bot is alive.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://YOUR-RENDER-URL/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
