import os
import asyncio
import threading
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")
# ДОЛЖЕН быть БЕЗ /webhook на конце, только https://...onrender.com
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL is not set")

app = Flask(__name__)

# Глобальное приложение и event loop для бота
telegram_app = Application.builder().token(BOT_TOKEN).build()
bot_loop = asyncio.new_event_loop()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("==> start handler called, update:", update)

    if update.message is None:
        print("==> update.message is None, return")
        return

    keyboard = [
        [InlineKeyboardButton("ОТКРЫТЬ калькулятор", url=WEB_APP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже, чтобы открыть калькулятор BYDFi:",
        reply_markup=reply_markup,
    )
    print("==> reply_text sent")


telegram_app.add_handler(CommandHandler("start", start))


def run_bot_loop():
    """Фоновый поток, в котором крутится event loop телеграм-приложения."""
    asyncio.set_event_loop(bot_loop)

    async def runner():
        try:
            print("==> initializing telegram_app")
            await telegram_app.initialize()
            print("==> starting telegram_app")
            await telegram_app.start()
            print("==> telegram_app started")
        except Exception as e:
            # Если что-то упадёт на старте, увидим это в логах
            print("ERROR in bot runner:", repr(e))

    # запускаем инициализацию и start
    bot_loop.run_until_complete(runner())
    # если всё ок, крутим loop бесконечно
    try:
        print("==> entering bot_loop.run_forever()")
        bot_loop.run_forever()
    except Exception as e:
        print("ERROR in bot_loop.run_forever:", repr(e))


@app.route("/webhook", methods=["POST"])
def webhook():
    # Telegram шлёт JSON
    data = request.get_json(force=True)

    # Десериализуем update
    update = Update.de_json(data, telegram_app.bot)

    # Если по какой-то причине loop уже закрыт — логируем и не падаем
    if bot_loop.is_closed():
        print("ERROR: bot_loop is closed, cannot process update")
        return "loop closed", 500

    # Отправляем обработку апдейта в уже работающий event loop
    try:
        asyncio.run_coroutine_threadsafe(
            telegram_app.process_update(update), bot_loop
        )
    except RuntimeError as e:
        # сюда попадём, если loop закрыт или ещё не запущен
        print("ERROR in run_coroutine_threadsafe:", repr(e))
        return "loop error", 500

    # Всегда сразу отвечаем 200 OK
    return "ok", 200


@app.route("/")
def index():
    return "Bot is running", 200


def setup_webhook():
    """Настройка вебхука в Telegram. Используем отдельный временный loop."""
    async def runner():
        print("==> deleting old webhook")
        await telegram_app.bot.delete_webhook()
        print("==> setting new webhook to", f"{WEBHOOK_URL}/webhook")
        await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        print("==> webhook set")

    # ВАЖНО: этот loop никак не связан с bot_loop, он временный и будет закрыт
    asyncio.run(runner())


if __name__ == "__main__":
    # 1. Настраиваем webhook в Telegram (отдельный временный loop)
    setup_webhook()

    # 2. Запускаем event loop бота в отдельном потоке
    t = threading.Thread(target=run_bot_loop, daemon=True)
    t.start()

    # 3. Запускаем Flask
    port = int(os.getenv("PORT", 10000))
    print(f"==> starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
