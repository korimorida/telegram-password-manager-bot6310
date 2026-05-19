import asyncio
import string
import secrets

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message, BotCommand,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command

from database import save_password, get_passwords, delete_password

# Токен от BotFather
TOKEN = "вставить"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Генерация пароля
def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# Клавиатура команд
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔐 Сгенерировать пароль")],
        [KeyboardButton(text="📄 Мои пароли")],
    ],
    resize_keyboard=True
)


# inline-кнопки
def get_length_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="8", callback_data="length_8"),
                InlineKeyboardButton(text="12", callback_data="length_12"),
                InlineKeyboardButton(text="16", callback_data="length_16"),
            ]
        ]
    )


# Команды в меню Telegram
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="gen", description="Сгенерировать пароль"),
        BotCommand(command="list", description="Мои пароли"),
    ]
    await bot.set_my_commands(commands)


# /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🔐 Бот для паролей\n\nВыбери действие 👇",
        reply_markup=keyboard
    )


# генерация (команда и кнопка)
@dp.message(Command("gen"))
@dp.message(lambda message: message.text == "🔐 Сгенерировать пароль")
async def gen_handler(message: Message):
    await message.answer(
        "Выбери длину пароля:",
        reply_markup=get_length_keyboard()
    )


# выбор длины пароля
@dp.callback_query(lambda c: c.data.startswith("length_"))
async def length_callback(callback: CallbackQuery):
    length = int(callback.data.split("_")[1])
    password = generate_password(length)
    save_password(callback.from_user.id, password)

    await callback.message.edit_text(
        f"Пароль создан ✅\n\n`{password}`",
        parse_mode="Markdown"
    )


# список паролей с нумерацией и кнопками удаления
@dp.message(Command("list"))
@dp.message(lambda message: message.text == "📄 Мои пароли")
async def list_handler(message: Message):
    passwords = get_passwords(message.from_user.id)

    if not passwords:
        await message.answer("У тебя нет паролей")
        return

    buttons = []
    text = "Твои пароли:\n\n"

    for i, (pid, pwd) in enumerate(passwords, start=1):
        text += f"{i}. `{pwd}`\n"
        # кнопка удаления
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {i}",
                callback_data=f"delete_{pid}"
            )
        ])

    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard_inline)


# запрос на удаление пароля
@dp.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_request(callback: CallbackQuery):
    password_id = int(callback.data.split("_")[1])

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{password_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
            ]
        ]
    )

    await callback.message.edit_text(
        "Удалить пароль?",
        reply_markup=confirm_keyboard
    )


# подтверждение удаления
@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_delete(callback: CallbackQuery):
    password_id = int(callback.data.split("_")[1])
    delete_password(password_id)

    await callback.message.edit_text("Пароль удалён ✅")


# отмена удаления
@dp.callback_query(lambda c: c.data == "cancel")
async def cancel(callback: CallbackQuery):
    await callback.message.edit_text("Удаление отменено ✅")


# запуск бота
async def main():
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())