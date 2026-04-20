import os
import asyncio
import threading
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ДОЛЖЕН быть БЕЗ /webhook на конце, только https://...onrender.com

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL is not set")

app = Flask(__name__)

# Глобальный event loop и приложение бота
telegram_app = Application.builder().token(BOT_TOKEN).build()
loop = asyncio.new_event_loop()


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


telegram_app.add_handler(CommandHandler("start", start))


def start_bot_loop():
    """Фоновый поток, в котором крутится event loop телеграм-приложения."""
    asyncio.set_event_loop(loop)

    async def runner():
        # Инициализируем и запускаем приложение
        await telegram_app.initialize()
        await telegram_app.start()

    loop.run_until_complete(runner())
    loop.run_forever()


@app.route("/webhook", methods=["POST"])
def webhook():
    # Telegram шлёт JSON
    data = request.get_json(force=True)

    # Десериализуем update
    update = Update.de_json(data, telegram_app.bot)

    # Отправляем обработку апдейта в уже работающий event loop
    asyncio.run_coroutine_threadsafe(telegram_app.process_update(update), loop)

    # Всегда сразу отвечаем 200 OK
    return "ok", 200


@app.route("/")
def index():
    return "Bot is running", 200


def setup_webhook():
    async def runner():
        # Сбрасываем старый вебхук (на всякий случай)
        await telegram_app.bot.delete_webhook()
        # Ставим новый вебхук НА URL ЭТОГО СЕРВИСА
        await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

    # ВАЖНО: используем отдельный временный loop, НЕ тот, что у бота
    asyncio.run(runner())


if __name__ == "__main__":
    # Настраиваем webhook в Telegram
    setup_webhook()

    # Запускаем event loop бота в отдельном потоке
    t = threading.Thread(target=start_bot_loop, daemon=True)
    t.start()

    # Запускаем Flask
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
