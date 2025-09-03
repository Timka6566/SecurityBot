import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters


from handlers.generation import generate_easy, generate_medium, generate_strong
from handlers.checking import check_password_strength
from handlers.advice import ADVICE_TEXTS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔐 Сгенерировать пароль",
                              callback_data='main_generate')],
        [InlineKeyboardButton("💪 Проверить надежность пароля",
                              callback_data='main_check')],
        [InlineKeyboardButton("🎓 Советы по безопасности",
                              callback_data='main_advice')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_generation_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Простой", callback_data='gen_easy'),
            InlineKeyboardButton("Средний", callback_data='gen_medium'),
            InlineKeyboardButton("Надежный", callback_data='gen_strong'),
        ],
        [InlineKeyboardButton("⬅️ Назад в главное меню",
                              callback_data='back_to_main')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_advice_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔐 Что такое 2FA?", callback_data='advice_2fa')],
        [InlineKeyboardButton("🎣 Что такое фишинг?",
                              callback_data='advice_phishing')],
        [InlineKeyboardButton("⬅️ Назад в главное меню",
                              callback_data='back_to_main')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад в главное меню",
                              callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    start_text = (
        f"Привет, {user.mention_html()}!\n\n"
        "Я твой личный помощник по кибербезопасности."
        " Выбери, что ты хочешь сделать:"
    )
    await update.message.reply_html(start_text, reply_markup=get_main_menu_keyboard())


async def main_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'back_to_main':
        await query.edit_message_text(
            text='Выбери, что ты хочешь сделать:',
            reply_markup=get_main_menu_keyboard()
        )
    elif data == 'main_generate':
        await query.edit_message_text(
            text='Выбери сложность пароля:',
            reply_markup=get_generation_menu_keyboard()
        )
    elif data == 'main_advice':
        await query.edit_message_text(
            text='Выбери тему, о которой хотите узнать:',
            reply_markup=get_advice_menu_keyboard()
        )
    elif data == 'main_check':
        await query.edit_message_text(
            text=(
                "Чтобы проверить надежность пароля, просто отправь его мне следующим сообщением.\n\n"
                "⚠️ *Внимание:* Отправленные пароли нигде не сохраняются."
            ),
            reply_markup=get_back_to_main_keyboard()
        )
    elif data in ['gen_easy', 'gen_medium', 'gen_strong']:
        if data == 'gen_easy':
            password = generate_easy()
            level = 'простого'
        elif data == 'gen_medium':
            password = generate_medium()
            level = 'среднего'
        else:
            password = generate_strong()
            level = 'надежного'

        await query.edit_message_text(
            text=f"Твой новый пароль {level} уровня сложности:\n\n`{password}`\n\nНажми на пароль, чтобы скопировать его.",
            parse_mode='Markdown',
            reply_markup=get_generation_menu_keyboard()
        )
    elif data in ADVICE_TEXTS:
        await query.edit_message_text(
            text=ADVICE_TEXTS[data],
            parse_mode='Markdown',
            reply_markup=get_advice_menu_keyboard()
        )


async def handle_password_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    password = update.message.text

    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")

    strength_feedback = await check_password_strength(password)

    await update.message.reply_text(
        strength_feedback,
        reply_markup=get_back_to_main_keyboard(),
        parse_mode='Markdown'
    )


def main() -> None:
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("Не найден токен! Убедитесь, что он задан в переменных окружения как TOKEN=...")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CallbackQueryHandler(main_button_callback))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_password_check))

    application.run_polling()


if __name__ == "__main__":
    main()
