from dotenv import load_dotenv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    Application,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from Load import load_client_data, load_articles_data
from Extract import get_articles

WAITING_FOR_GENERATE_LIST = 1
WAITING_FOR_ADD_LIST = 2

load_dotenv()
token = os.getenv("BOT_API_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Добрый день! В данном Боте Вы можете отслеживать цену на интересующие Вас товары WB."
    )
    chat_id = update.message.chat_id
    username = update.message.chat.username
    load_client_data(str(chat_id), username)
    await show_option_buttons(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("В разработке...")


async def show_option_buttons(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "Сгенерировать новый список артикулов", callback_data="button_1"
            )
        ],
        [
            InlineKeyboardButton(
                "Увидеть текущий список артикулов", callback_data="button_2"
            )
        ],
        [InlineKeyboardButton("Добавить артикулы к списку", callback_data="button_3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Выберите опцию:", reply_markup=reply_markup
        )


async def handle_generate_list(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Напишите список интересующих Вас артикулов в формате 1111111,22222222,333333333 и т. д. \n"
        "Не более 10 артикулов!"
    )
    return WAITING_FOR_GENERATE_LIST


async def handle_show_list(update, context):
    chat_id = update.callback_query.message.chat_id
    articles_list = get_articles(chat_id)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Текущий список Ваших артикулов: \n{', '.join(articles_list)}"
    )
    await show_option_buttons(update, context)


async def handle_add_articles(update, context):
    chat_id = update.callback_query.message.chat_id
    articles_list = get_articles(chat_id)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Вы хотите добавить новые артикулы. \n"
        + "ВНИМАНИЕ. Кол-во артикулов не должно превышать 10! \n\n"
        + f"Текущий список Ваших артикулов: \n{', '.join(articles_list)}\n\n"
        + "Можете скопировать список артикулов, заменив ненужные или вставив дополнительные в том же формате. "
        + "Вся информация об артикулах которые вы не укажите будет безвозратно удалена!"
    )
    return WAITING_FOR_ADD_LIST


async def receive_articles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    articles = parse_articles(text)

    if len(articles) > 10:
        await update.message.reply_text(
            f"Вы превысили максимально допустимое число артикулов для отслеживания!"
        )
        return ConversationHandler.END

    load_articles_data(str(chat_id), articles)

    await update.message.reply_text(
        f"✅ Новый список из {len(articles)} артикулов сохранён:\n{', '.join(articles)}"
    )
    await show_option_buttons(update, context)


def parse_articles(text):
    return [a.strip() for a in text.replace(",", " ").split() if a.strip().isdigit()]


async def receive_add_list(update, context):
    text = update.message.text
    chat_id = update.message.chat_id

    articles = parse_articles(text)

    load_articles_data(str(chat_id), articles)

    await update.message.reply_text(
        f"✅ Добавлено {len(articles)} артикулов к отслеживанию:\n{', '.join(articles)}"
    )
    await show_option_buttons(update, context)


def parse_articles(text):
    return [a.strip() for a in text.replace(",", " ").split() if a.strip().isdigit()]


conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handle_generate_list, pattern="^button_1$"),
        CallbackQueryHandler(handle_add_articles, pattern="^button_3$"),
    ],
    states={
        WAITING_FOR_GENERATE_LIST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_articles)
        ],
        WAITING_FOR_ADD_LIST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add_list)
        ],
    },
    fallbacks=[],
    per_chat=True,
)


def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(conv_handler)

    # Опции
    application.add_handler(
        CallbackQueryHandler(handle_show_list, pattern="^button_2$")
    )

    application.run_polling()


if __name__ == "__main__":
    main()
