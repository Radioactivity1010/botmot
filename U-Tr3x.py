from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import threading
from flask import Flask

TOKEN = os.getenv("TOKEN")

# سرور کوچک برای Render
server = Flask(__name__)

@server.route("/")
def home():
    return "Bot is running!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

# دستور /start تلگرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام در خدمتم، چه کمکی از من ساخته است؟")

# اجرای بات
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

# اجرای Flask در یک نخ جدا
threading.Thread(target=run_server).start()

# اجرای تلگرام
app.run_polling()
