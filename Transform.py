import pandas as pd
import xmltodict
from datetime import datetime, timedelta
import os
import tempfile


def transform(prices_dict: dict, chat_id: int) -> str:
    try:
        print(prices_dict, type(prices_dict))
        df = pd.DataFrame(prices_dict)

        df["dateUpdate"] = datetime.now()
        df["operationDate"] = datetime.now()
        df["chatId"] = chat_id

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "prices.csv")
        df.to_csv(temp_path, index=False)

        return temp_path
    except Exception as e:
        print(f"Transform error: {e}")
        raise
