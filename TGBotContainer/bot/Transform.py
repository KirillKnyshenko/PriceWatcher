import pandas as pd
from datetime import datetime, timedelta
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


def transform(prices_dict: dict) -> str:
    try:
        df = pd.DataFrame(prices_dict)

        df["dateUpdate"] = datetime.now()

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "prices.csv")
        df.to_csv(temp_path, index=False)

        return temp_path
    except Exception as e:
        logger.error(f"Transform error: {e}")
        raise
