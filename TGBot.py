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

load_dotenv()
token = os.getenv("BOT_API_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("state", None)
    await update.message.reply_text(
        "Добрый день! В данном Боте Вы можете отслеживать цену на интересующие Вас товары WB."
    )
    chat_id = update.message.chat_id
    username = update.message.chat.username
    load_client_data(str(chat_id), username)
    await show_option_buttons(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("state", None)
    await update.message.reply_text("В разработке...")


async def show_option_buttons(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.user_data.pop("state", None)
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
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Выберите опцию:", reply_markup=reply_markup
        )


async def handle_generate_list(update, context):
    context.user_data["state"] = "awaiting_articles"
    chat_id = update.callback_query.message.chat_id
    articles_list = get_articles(chat_id)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Добавление артикулов\n\n"
        "Вам необходимо далее ввести список артикулов в формате 1111111,22222222,333333333\n"
        "Количество артикулов не более 10"
        "\n\n‼️ВНИМАНИЕ‼️\n\n"
        f"Текущий список Ваших артикулов: \n{', '.join(articles_list)}\n\n"
        "Если в указаном списке ниже не будет какого-то из вышеперечисленных артикулов (т.е. тех что Вы уже отислеживаете), то они будут безвозратно удалены.\n"
        "В случае если Вы передумали и хотите вернутся назад, то введите (или нажмите справа) команду /start"
    )
    return WAITING_FOR_GENERATE_LIST


async def handle_show_list(update, context):
    context.user_data.pop("state", None)
    chat_id = update.callback_query.message.chat_id
    articles_list = get_articles(chat_id)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Текущий список Ваших артикулов ({len(articles_list)} шт.): \n{', '.join(articles_list)}"
    )
    await show_option_buttons(update, context)


async def receive_articles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "awaiting_articles":
        await update.message.reply_text(
            "Сначала нажмите кнопку 'Сгенерировать новый список артикулов'."
        )
        return ConversationHandler.END

    text = update.message.text
    chat_id = update.message.chat_id

    articles = parse_articles(text)

    if len(articles) > 10:
        await update.message.reply_text(
            f"Вы превысили максимально допустимое число артикулов для отслеживания!"
        )
        return ConversationHandler.END

    old_articles_list = get_articles(chat_id)
    load_articles_data(str(chat_id), articles, old_articles_list)
    articles_list = get_articles(chat_id)

    await update.message.reply_text(
        f"✅ Новый список из {len(articles_list)} артикулов сохранён:\n{', '.join(articles_list)}"
    )

    context.user_data.pop("state", None)
    await show_option_buttons(update, context)
    return ConversationHandler.END


def parse_articles(text):
    return [a.strip() for a in text.replace(",", " ").split() if a.strip().isdigit()]


conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handle_generate_list, pattern="^button_1$"),
    ],
    states={
        WAITING_FOR_GENERATE_LIST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_articles)
        ]
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
