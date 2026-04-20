import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ДОЛЖЕН БЫТЬ без /webhook на конце, только https://...onrender.com

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL is not set")

app = Flask(__name__)

# Создаём приложение PTB ОДИН РАЗ
telegram_app = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # На всякий случай проверяем, что message есть
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


telegram_app.add_handler(CommandHandler("start", start))


@app.route("/webhook", methods=["POST"])
def webhook():
    # Telegram шлёт JSON
    data = request.get_json(force=True)

    # Десериализуем update
    update = Update.de_json(data, telegram_app.bot)

    # Вместо того, чтобы создавать новый event loop на каждый запрос,
    # используем уже существующий loop у приложения.
    # Для простоты используем asyncio.create_task на глобальном loop.
    asyncio.get_event_loop().create_task(telegram_app.process_update(update))

    # Всегда сразу отвечаем 200 OK
    return "ok", 200


@app.route("/")
def index():
    return "Bot is running", 200


def setup_webhook():
    async def runner():
        # Инициализируем приложение, но НЕ запускаем run_polling / run_webhook
        await telegram_app.initialize()

        # Сбрасываем старый вебхук (на всякий случай)
        await telegram_app.bot.delete_webhook()

        # Ставим новый вебхук НА URL ЭТОГО СЕРВИСА
        # ВАЖНО: WEBHOOK_URL должен быть вида https://bydfi-telegram-bot.onrender.com
        await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

    asyncio.run(runner())


if __name__ == "__main__":
    # Один раз на старте настраиваем webhook и инициализируем приложение PTB
    setup_webhook()

    # Запускаем Flask. Без debug, без дополнительных event loop.
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
