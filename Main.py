from Extract import extract, get_articles, get_chat_ids
from Transform import transform
from Load import load_price_data

chatIds = get_chat_ids()
articles = []
print(chatIds)
for chatId in chatIds:
    articles_list_db = get_articles(chatId)
    for art in articles_list_db:
        articles.append(art)

# Удаляю дубли артикулов
print(articles)
articles = list(set(articles))
print(articles)

prices = extract(articles)
csv_path = transform(prices)
load_price_data(csv_path)
