from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os
import threading
import psycopg2
from datetime import datetime
from flask import Flask


# =====================
# Environment Variables
# =====================

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = int(os.getenv("ID"))


# =====================
# Flask for Render
# =====================

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


# =====================
# PostgreSQL
# =====================

def init_db():

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        username TEXT,
        message TEXT,
        created_at TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()



def save_message(user_id, username, message):

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO messages
        (user_id, username, message, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (
            user_id,
            username if username else "بدون یوزرنیم",
            message,
            datetime.now()
        )
    )

    conn.commit()

    cur.close()
    conn.close()



# =====================
# Start Command
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "سلام 👋\n\n"
        "پیام خود را برای U-Tr3x ارسال کنید.\n"
        "پیام شما ذخیره خواهد شد."
    )



# =====================
# Receive Messages
# =====================

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



# =====================
# Admin Messages
# =====================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ شما دسترسی ندارید."
        )
        return


    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()


    cur.execute("""
    SELECT id, username, user_id, message
    FROM messages
    ORDER BY id DESC
    LIMIT 10
    """)


    rows = cur.fetchall()


    cur.close()
    conn.close()



    if not rows:

        await update.message.reply_text(
            "هنوز پیامی ذخیره نشده."
        )

        return



    text = "📩 آخرین پیام‌ها:\n\n"


    for msg_id, username, user_id, message in rows:
    
        text += (
            f"🆔 {msg_id}\n"
            f"👤 {username}\n"
            f"🆔 کاربر: {user_id}\n"
            f"💬 {message}\n"
            "──────────\n"
        )


    await update.message.reply_text(text)


async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ شما دسترسی ندارید.")
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "استفاده صحیح:\n"
            "/delete ID\n"
            "یا\n"
            "/delete all"
        )
        return

    target = context.args[0]


    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()


    # حذف همه پیام‌ها
    if target.lower() == "all":

        cur.execute("DELETE FROM messages")

        deleted = cur.rowcount

        conn.commit()

        await update.message.reply_text(
            f"✅ همه پیام‌ها پاک شدند.\n"
            f"تعداد حذف شده: {deleted}"
        )


    # حذف یک پیام خاص
    else:

        try:
            message_id = int(target)

        except:
            await update.message.reply_text(
                "❌ آیدی پیام باید عدد باشد."
            )

            cur.close()
            conn.close()
            return


        cur.execute(
            "DELETE FROM messages WHERE id = %s",
            (message_id,)
        )

        conn.commit()


        if cur.rowcount == 0:
            await update.message.reply_text(
                "❌ چنین پیامی پیدا نشد."
            )

        else:
            await update.message.reply_text(
                "✅ پیام حذف شد."
            )


    cur.close()
    conn.close()

# =====================
# Run Bot
# =====================

init_db()


app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    CommandHandler(
        "messages",
        messages
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_message
    )
)

app.add_handler(
    CommandHandler(
        "delete",
        delete_message
    )
)



threading.Thread(
    target=run_server
).start()



app.run_polling()
