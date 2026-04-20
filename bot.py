import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ОТКРЫТЬ", url=WEB_APP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже, чтобы открыть калькулятор BYDFi:",
        reply_markup=reply_markup,
    )


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    # держим приложение, пока его не остановят
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
