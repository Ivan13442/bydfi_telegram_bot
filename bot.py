import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # полный https-URL этого сервиса на Render

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ОТКРЫТЬ", url=WEB_APP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже, чтобы открыть калькулятор BYDFi:",
        reply_markup=reply_markup,
    )


telegram_app.add_handler(CommandHandler("start", start))


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"


@app.route("/")
def index():
    return "Bot is running", 200


async def set_webhook():
    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL is not set")
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")


def main():
    import asyncio

    async def runner():
        await set_webhook()
        await telegram_app.initialize()
        await telegram_app.start()
        # update_queue будет обрабатываться в фоне
        await telegram_app.updater.start_polling(drop_pending_updates=True)

    asyncio.get_event_loop().create_task(runner())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))


if __name__ == "__main__":
    main()
