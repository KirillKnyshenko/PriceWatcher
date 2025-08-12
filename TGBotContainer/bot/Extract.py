from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright

from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, select, func, MetaData
import logging

logger = logging.getLogger(__name__)


def get_engine():
    load_dotenv()
    return create_engine(
        f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
    )


engine = get_engine()
metadata = MetaData()
metadata.reflect(bind=engine)

ARTICLES_TABLE_NAME = "articles"
PRICE_TABLE_NAME = "wb_price_history"

articles_table = metadata.tables[ARTICLES_TABLE_NAME]
price_table = metadata.tables[PRICE_TABLE_NAME]


def get_articles_list(chat_id, conn, articles_table):
    stmt = select(articles_table).where(articles_table.c.chatId == chat_id)
    result = conn.execute(stmt)
    return [row[0] for row in result.fetchall()]


def extract(articles: list) -> dict:
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_price, articles))

    return {"article": articles, "price": results}


def fetch_price(article):
    url = f"https://www.wildberries.ru/catalog/{article}/detail.aspx"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                }
            )
            page.goto(url, timeout=15000)
            page.wait_for_selector(
                ".price-block__wallet-price, .price-block__final-price", timeout=20000
            )
            html_content = page.content()
        except Exception as e:
            logger.error(f"[ERROR] Timeout or load issue for article {article}: {e}")

            return None
        finally:
            browser.close()

    soup = BeautifulSoup(html_content, "html.parser")

    priceRaw = soup.select_one(".price-block__wallet-price") or soup.select_one(
        ".price-block__final-price"
    )
    if not priceRaw:
        logger.warning(f"[WARNING] Price not found for article {article}")
        return None

    price_text = priceRaw.get_text(strip=True)
    cleaned_price = price_text.replace("\xa0", "").replace("₽", "").replace(" ", "")

    try:
        price = float(cleaned_price)
    except ValueError:
        logger.error(f"[ERROR] Failed to convert price for {article}: {cleaned_price}")
        return None

    logger.info(f"[INFO] Price for {article}: {price}")
    return price


def get_articles(chat_id: str) -> list:
    try:
        with engine.connect() as conn:
            articles_list = get_articles_list(chat_id, conn, articles_table)
        return articles_list
    except Exception as e:
        logger.error(f"Get from DB error: {e}")
        raise


def get_prices_db(chat_id: str, isMax: bool = True) -> list:
    try:
        with engine.connect() as conn:
            articles_list = get_articles_list(chat_id, conn, articles_table)

            if isMax:
                subquery = (
                    select(func.max(price_table.c.dateUpdate)).where(
                        price_table.c.article.in_(articles_list)
                    )
                ).scalar_subquery()

                stmt = select(price_table.c.article, price_table.c.price).where(
                    price_table.c.article.in_(articles_list),
                    price_table.c.dateUpdate == subquery,
                )
            else:
                subquery = (
                    select(price_table.c.dateUpdate.label("dateUpdate"))
                    .where(price_table.c.article.in_(articles_list))
                    .distinct()
                    .order_by(price_table.c.dateUpdate.desc())
                    .limit(2)
                ).subquery()

                second_last_date = conn.execute(
                    select(subquery.c.dateUpdate).offset(1)
                ).scalar()

                stmt = select(price_table.c.article, price_table.c.price).where(
                    price_table.c.article.in_(articles_list),
                    price_table.c.dateUpdate == second_last_date,
                )

            result = conn.execute(stmt)
            price_list = [row for row in result.fetchall()]
        return price_list
    except Exception as e:
        logger.error(f"Get from DB error: {e}")
        raise


def get_price_history_db(chat_id: str) -> list:
    try:
        with engine.connect() as conn:
            articles_list = get_articles_list(chat_id, conn, articles_table)

            if not articles_list:
                return []

            stmt = select(
                price_table.c.article, price_table.c.price, price_table.c.dateUpdate
            ).where(price_table.c.article.in_(articles_list))

            result = conn.execute(stmt)
            price_list = [
                {"article": row[0], "price": row[1], "date": row[2]}
                for row in result.fetchall()
            ]

        return price_list

    except Exception as e:
        logger.error(f"Get from DB error: {e}")
        return []


def get_chat_ids() -> list:
    try:
        with engine.connect() as conn:
            stmt = select(articles_table.c.chatId).distinct(articles_table.c.chatId)

            result = conn.execute(stmt)

            chatids_list = [row[0] for row in result.fetchall()]
        return chatids_list
    except Exception as e:
        logger.error(f"Get from DB error: {e}")
        raise
