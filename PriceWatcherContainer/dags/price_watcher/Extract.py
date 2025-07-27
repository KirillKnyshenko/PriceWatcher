from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from playwright.sync_api import sync_playwright

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, select, func, MetaData


def extract(articles: list) -> dict:
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_price, articles))

    return {"article": articles, "price": results}


def fetch_price(article):
    url = f"https://www.wildberries.ru/catalog/{article}/detail.aspx"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=15000)
            page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                }
            )
            page.wait_for_selector(
                ".price-block__wallet-price, .price-block__final-price", timeout=20000
            )
        except Exception as e:
            print(f"[ERROR] Timeout or load issue for article {article}: {e}")
            browser.close()
            return None

        html_content = page.content()
        browser.close()

    soup = BeautifulSoup(html_content, "html.parser")

    priceRaw = soup.select_one(".price-block__wallet-price") or soup.select_one(
        ".price-block__final-price"
    )
    if not priceRaw:
        print(f"[WARNING] Price not found for article {article}")
        return None

    price_text = priceRaw.get_text(strip=True)
    cleaned_price = price_text.replace("\xa0", "").replace("₽", "").replace(" ", "")

    try:
        price = float(cleaned_price)
    except ValueError:
        print(f"[ERROR] Failed to convert price for {article}: {cleaned_price}")
        return None

    print(f"[INFO] Price for {article}: {price}")
    return price


def get_articles(chat_id: str) -> list:
    try:
        load_dotenv("../")

        print(f"DB_HOST={os.getenv('DB_HOST')}")
        print(f"DB_USER={os.getenv('DB_USER')}")

        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        db = os.environ["DB_NAME"]

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        )

        ARTICLES_TABLE = "articles"

        metadata = MetaData()
        metadata.reflect(bind=engine)
        articles_table = metadata.tables[ARTICLES_TABLE]

        with engine.connect() as conn:
            stmt = select(articles_table).where((articles_table.c.chatId == chat_id))

            conn.execute(stmt)
            result = conn.execute(stmt)

            articles_list = [row[0] for row in result.fetchall()]
        return articles_list
    except Exception as e:
        print(f"Get from DB error: {e}")
        raise


def get_prices_db(chat_id: str) -> list:
    try:
        load_dotenv()

        print(f"DB_HOST={os.getenv('DB_HOST')}")
        print(f"DB_USER={os.getenv('DB_USER')}")

        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        db = os.environ["DB_NAME"]

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        )

        ARTICLES_TABLE = "articles"
        PRICE_TABLE = "wb_price_history"

        metadata = MetaData()
        metadata.reflect(bind=engine)
        articles_table = metadata.tables[ARTICLES_TABLE]
        price_table = metadata.tables[PRICE_TABLE]
        with engine.connect() as conn:
            stmt = select(articles_table).where((articles_table.c.chatId == chat_id))

            result = conn.execute(stmt)

            articles_list = [row[0] for row in result.fetchall()]

            stmt = select(price_table.c.article, price_table.c.price).where(
                (price_table.c.article.in_(articles_list))
            )

            result = conn.execute(stmt)
            price_list = [row for row in result.fetchall()]
        return price_list
    except Exception as e:
        print(f"Get from DB error: {e}")
        raise


def get_prices_db(chat_id: str, date: datetime) -> list:
    try:
        load_dotenv()

        print(f"DB_HOST={os.getenv('DB_HOST')}")
        print(f"DB_USER={os.getenv('DB_USER')}")

        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        db = os.environ["DB_NAME"]

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        )

        ARTICLES_TABLE = "articles"
        PRICE_TABLE = "wb_price_history"

        metadata = MetaData()
        metadata.reflect(bind=engine)
        articles_table = metadata.tables[ARTICLES_TABLE]
        price_table = metadata.tables[PRICE_TABLE]
        with engine.connect() as conn:
            stmt = select(articles_table).where((articles_table.c.chatId == chat_id))

            result = conn.execute(stmt)

            articles_list = [row[0] for row in result.fetchall()]

            stmt = select(price_table.c.article, price_table.c.price).where(
                (price_table.c.article.in_(articles_list)),
                (func.date(price_table.c.dateUpdate) == date),
            )

            result = conn.execute(stmt)
            price_list = [row for row in result.fetchall()]
        return price_list
    except Exception as e:
        print(f"Get from DB error: {e}")
        raise


def get_chat_ids() -> list:
    try:
        load_dotenv()

        print(f"DB_HOST={os.getenv('DB_HOST')}")
        print(f"DB_USER={os.getenv('DB_USER')}")

        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        db = os.environ["DB_NAME"]

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        )

        ARTICLES_TABLE = "articles"

        metadata = MetaData()
        metadata.reflect(bind=engine)
        articles_table = metadata.tables[ARTICLES_TABLE]

        with engine.connect() as conn:
            stmt = select(articles_table.c.chatId).distinct(articles_table.c.chatId)

            conn.execute(stmt)
            result = conn.execute(stmt)

            chatids_list = [row[0] for row in result.fetchall()]
        return chatids_list
    except Exception as e:
        print(f"Get from DB error: {e}")
        raise
