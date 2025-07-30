import pandas as pd
from sqlalchemy import create_engine, delete, MetaData
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def load(csv_path: str):
    try:
        load_dotenv()

        df = pd.read_csv(csv_path)

        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        db = os.environ["DB_NAME"]

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        )

        PRICE_TABLE = "wb_price_history"

        metadata = MetaData()
        metadata.reflect(bind=engine)

        df.to_sql(name=PRICE_TABLE, con=engine, if_exists="append", index=False)

        logger.info("Successfully loaded to DB!")
    except Exception as e:
        logger.error(f"Load error: {e}")
        raise


def load_client_data(chat_id: str, username):
    try:
        load_dotenv()

        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        db = os.environ["DB_NAME"]

        df = pd.DataFrame([{"username": username, "chatId": chat_id}])

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        )

        CLIENTS_TABLE = "clients"

        metadata = MetaData()
        metadata.reflect(bind=engine)
        clients_table = metadata.tables[CLIENTS_TABLE]

        with engine.connect() as conn:
            # Удаление дубля
            stmt = delete(clients_table).where(clients_table.c.chatId == chat_id)
            conn.execute(stmt)
            conn.commit()

        df.to_sql(name=CLIENTS_TABLE, con=engine, if_exists="append", index=False)

        logger.info("Successfully loaded to DB!")
    except Exception as e:
        logger.error(f"Load error: {e}")
        raise


def load_articles_data(chat_id: str, articles: list, articles_old: list):
    try:
        load_dotenv()

        # Удаляю дубли артикулов
        articles = list(set(articles))

        # Лист артикулов на удаление
        articles_delete = [art for art in articles_old if art not in articles]

        new_articles = [art for art in articles if art not in articles_old]

        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        db = os.environ["DB_NAME"]

        df = pd.DataFrame(
            [
                {"chatId": chat_id, "article": article, "dateUpdate": datetime.now()}
                for article in new_articles
            ]
        )

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        )

        ARTICLES_TABLE = "articles"

        metadata = MetaData()
        metadata.reflect(bind=engine)
        articles_table = metadata.tables[ARTICLES_TABLE]

        with engine.connect() as conn:
            # Удаление дубля
            stmt = delete(articles_table).where(
                (articles_table.c.chatId == chat_id)
                & (articles_table.c.article.in_(articles_delete))
            )

            conn.execute(stmt)
            conn.commit()

        df.to_sql(name=ARTICLES_TABLE, con=engine, if_exists="append", index=False)

        logger.info("Successfully loaded to DB!")
    except Exception as e:
        logger.error(f"Load error: {e}")
        raise
