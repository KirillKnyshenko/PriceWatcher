import pandas as pd
from sqlalchemy import create_engine, delete, select, MetaData
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta


def load_price_data(csv_path: str):
    try:
        load_dotenv()

        df = pd.read_csv(csv_path)

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

        PRICE_TABLE = "wb_price_history"

        metadata = MetaData()
        metadata.reflect(bind=engine)
        price_table = metadata.tables[PRICE_TABLE]

        with engine.connect() as conn:
            # Удаление дубля для аирфлоу
            stmt = delete(price_table).where(
                price_table.c.operationDate == "25-06-2025"
            )
            conn.execute(stmt)
        df.to_sql(name=PRICE_TABLE, con=engine, if_exists="append", index=False)

        print("Successfully loaded to DB!")
    except Exception as e:
        print(f"Load error: {e}")
        raise


def load_client_data(chat_id: str, username):
    try:
        load_dotenv()

        print(f"DB_HOST={os.getenv('DB_HOST')}")
        print(f"DB_USER={os.getenv('DB_USER')}")

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

        print("Successfully loaded to DB!")
    except Exception as e:
        print(f"Load error: {e}")
        raise
