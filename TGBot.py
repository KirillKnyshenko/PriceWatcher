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
from Load import load_client_data

WAITING_FOR_ARTICLES = 1

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
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)


async def handle_generate_list(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Напишите список интересующих Вас артикулов в формате 1111111,22222222,333333333 и т. д."
    )


async def handle_show_list(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Текущий список артикулов:")


async def handle_add_articles(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Добавляем артикулы к списку...")


async def receive_articles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    articles = [
        a.strip() for a in text.replace(",", " ").split() if a.strip().isdigit()
    ]

    if not articles:
        await update.message.reply_text(
            "Не удалось распознать ни одного артикула. Попробуйте ещё раз."
        )
        return WAITING_FOR_ARTICLES

    # 💾 Тут можно сохранить артикулы в БД
    await update.message.reply_text(
        f"Получено {len(articles)} артикулов. Теперь они отслеживаются:\n\n{', '.join(articles)}"
    )
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_generate_list, pattern="^button_1$")],
    states={
        WAITING_FOR_ARTICLES: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_articles)
        ]
    },
    fallbacks=[],
)


def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Опции

    application.add_handler(
        CallbackQueryHandler(handle_show_list, pattern="^button_2$")
    )
    application.add_handler(
        CallbackQueryHandler(handle_add_articles, pattern="^button_3$")
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
