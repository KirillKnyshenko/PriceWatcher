from Extract import extract, get_articles, get_chat_ids
from Transform import transform
from Load import load_price_data

chatIds = get_chat_ids()

for chatId in chatIds:
    articles = get_articles(chatId)
    prices = extract(articles)
    csv_path = transform(prices, chatId)
    load_price_data(csv_path)
