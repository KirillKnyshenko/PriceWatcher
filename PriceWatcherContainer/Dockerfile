FROM apache/airflow:2.8.1

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER root
RUN apt-get update && apt-get install -y wget gnupg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libxshmfence1 libxss1 libxtst6 libgtk-3-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
RUN playwright install
