from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta
import logging

from price_watcher.Extract import extract, get_chat_ids, get_articles
from price_watcher.Transform import transform
from price_watcher.Load import load
from price_watcher.TGBot import show_changed_prices

logger = logging.getLogger(__name__)

with DAG(
    "price_sending",
    start_date=datetime(2025, 6, 27),
    schedule=timedelta(minutes=10),
    description="My pet project which get prices data from WB and send to Telegram.",
    tags=["PetProject", "ETL"],
    catchup=False,
) as dag:

    @task
    def extract_data():
        try:
            chatIds = get_chat_ids()
            articles = []

            for chatId in chatIds:
                articles_list_db = get_articles(chatId)
                for art in articles_list_db:
                    articles.append(art)

            # Удаляю дубли артикулов
            articles = list(set(articles))

            prices = extract(articles)
            logger.info("Extract succesfully!")

            return {
                "prices": prices,
                "chatIds": chatIds,
            }
        except Exception as e:
            logger.error(f"Extract error: {e}")
            raise

    @task
    def transform_data(ti):
        try:
            extract_result = ti.xcom_pull(task_ids="extract_data")
            if not extract_result:
                raise ValueError("No data received from extract task")

            prices = extract_result["prices"]
            csv_path = transform(prices)
            logger.info("Transform succesfully!")
            return csv_path
        except Exception as e:
            logger.error(f"Transform error: {e}")
            raise

    @task
    def load_data(ti):
        try:
            csv_path = ti.xcom_pull(task_ids="transform_data")
            load(csv_path)
            logger.info("Successfully loaded to DB!")
        except Exception as e:
            logger.error(f"Load error: {e}")
            raise

    @task
    def send_message(ti):
        try:
            extract_result = ti.xcom_pull(task_ids="extract_data")
            if not extract_result:
                raise ValueError("No data received from extract task")

            chatIds = extract_result["chatIds"]

            for chatId in chatIds:
                try:
                    show_changed_prices(chatId)
                    logger.info(f"Bot successfully!")
                except Exception as e:
                    logger.error(f"Bot error: {e}")
        except Exception as e:
            logger.error(f"Load error: {e}")
            raise

    extract_ = extract_data()
    transform_ = transform_data()
    load_ = load_data()
    send_ = send_message()

    extract_ >> transform_ >> load_ >> send_
