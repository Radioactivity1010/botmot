from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os
import json
import threading
from flask import Flask


ADMIN_ID = os.getenv("ID")
TOKEN = os.getenv("TOKEN")


# -------------------
# Flask برای Render
# -------------------

server = Flask(__name__)


@server.route("/")
def home():
    return "U-Tr3x Bot is running!"


def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(
        host="0.0.0.0",
        port=port
    )


# -------------------
# ذخیره پیام‌ها
# -------------------

FILE = "messages.json"


def save_message(user_id, username, message):

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    except:
        data = []


    data.append({

        "user_id": user_id,

        "username": username
        if username else "بدون یوزرنیم",

        "message": message

    })


    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )



# -------------------
# دستور Start
# -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "سلام 👋\n\n"
        "پیام خود را برای U-Tr3x ارسال کنید.\n"
        "پیام شما ذخیره خواهد شد."
    )



# -------------------
# دریافت پیام
# -------------------

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user


    save_message(

        user.id,

        user.username,

        update.message.text

    )


    await update.message.reply_text(
        "✅ پیام شما با موفقیت ذخیره شد."
    )

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ شما دسترسی ندارید."
        )
        return


    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    except:
        await update.message.reply_text(
            "هنوز پیامی ذخیره نشده."
        )
        return


    text = "📩 پیام‌های ذخیره شده:\n\n"


    for item in data[-10:]:
        text += (
            f"👤 {item['username']}\n"
            f"🆔 {item['user_id']}\n"
            f"💬 {item['message']}\n"
            "──────────\n"
        )


    await update.message.reply_text(text)



# -------------------
# ساخت بات
# -------------------

app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_message
    )
)



# اجرای Flask
threading.Thread(
    target=run_server
).start()

app.add_handler(
    CommandHandler(
        "messages",
        messages
    )
)


# اجرای تلگرام
app.run_polling()
