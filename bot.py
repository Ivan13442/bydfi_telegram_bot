import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


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

    # Render пробрасывает внешний порт в $PORT (обычно 10000)
    port = int(os.getenv("PORT", 10000))

    # run_webhook сам:
    # 1) создаёт и крутит event loop
    # 2) поднимает HTTP-сервер
    # 3) регистрирует webhook в Telegram
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",  # путь на сервере
        # ПОЛНЫЙ внешний URL до /webhook:
        webhook_url=f"{os.getenv('WEBHOOK_URL')}/webhook" if os.getenv("WEBHOOK_URL") else None,
    )


if __name__ == "__main__":
    main()
