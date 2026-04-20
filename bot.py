import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://bydfi-telegram-bot-vkbb.onrender.com

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL is not set")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    keyboard = [
        [InlineKeyboardButton("ОТКРЫТЬ калькулятор", url=WEB_APP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже, чтобы открыть калькулятор BYDFi:",
        reply_markup=reply_markup,
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    # Render прокидывает внешний порт в переменную окружения PORT
    port = int(os.getenv("PORT", 10000))

    # run_webhook:
    # 1) создаёт и крутит event loop
    # 2) поднимает HTTP-сервер
    # 3) регистрирует webhook в Telegram
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )


if __name__ == "__main__":
    main()
