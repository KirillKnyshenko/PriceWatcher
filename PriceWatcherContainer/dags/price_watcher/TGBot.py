from dotenv import load_dotenv
import os
from telegram import Bot
import asyncio

from price_watcher.Load import load_client_data, load_articles_data
from price_watcher.Extract import get_articles, get_prices_db


load_dotenv()
token = os.getenv("BOT_API_TOKEN")


def show_changed_prices(chat_id_arg: int):
    bot = Bot(token=token)

    price_list = get_prices_db(chat_id_arg, True)
    old_price_list = get_prices_db(chat_id_arg, False)

    text_lines = []
    for row in price_list:
        for old_row in old_price_list:
            if old_row[0] == row[0] and old_row[1] != row[1]:
                text_lines.append(
                    f"Артикул: {row[0]}, Цена: {row[1]}, Предыдущая цена: {old_row[1]}"
                )

    final_text = "\n".join(text_lines)

    if final_text:
        asyncio.run(
            bot.send_message(
                chat_id=chat_id_arg, text="Изменения в цене:\n\n" + final_text
            )
        )
