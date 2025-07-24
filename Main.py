from Extract import extract, get_articles, get_chat_ids
from Transform import transform
from Load import load_price_data
from TGBot import show_prices


# chatIds = get_chat_ids()
# articles = []
#
# for chatId in chatIds:
#    articles_list_db = get_articles(chatId)
#    for art in articles_list_db:
#        articles.append(art)
#
## Удаляю дубли артикулов
# articles = list(set(articles))
#
# prices = extract(articles)
# csv_path = transform(prices)
# load_price_data(csv_path)
# for chatId in chatIds:
chatIds = [111111111, 222222222, 633386807]
for chatId in chatIds:
    try:
        show_prices(chatId)
    except Exception as e:
        print(f"Bot error: {e}")
