import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Токен бота и URL калькулятора берём из переменных окружения на Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://bydfi-position-calc.onrender.com")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    open_btn = types.InlineKeyboardButton(
        text="ОТКРЫТЬ калькулятор",
        url=WEB_APP_URL,
    )
    keyboard.add(open_btn)

    await message.answer(
        "Привет! Нажми кнопку ниже, чтобы открыть калькулятор BYDFi:",
        reply_markup=keyboard
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)