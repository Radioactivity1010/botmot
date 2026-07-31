from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8860174708:AAEIG3YvfdWq6fFXgE14g8BJhFIgwRlZyKQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await Update.message.reply_text("سلام در خدمتم چه کمکی از من ساخته هست")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
