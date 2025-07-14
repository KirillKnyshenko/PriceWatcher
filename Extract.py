from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from concurrent.futures import ThreadPoolExecutor


def extract(articles: list) -> dict:
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_price, articles))

    return {"article": articles, "price": results}


def fetch_price(article):
    url = f"https://www.wildberries.ru/catalog/{article}/detail.aspx"

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(60)

    html_content = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html_content, "html.parser")

    # Получаю span с ценой
    priceRaw = soup.select_one(".price-block__wallet-price")

    if priceRaw is None:
        print(f"[WARNING] Red price not found for article {article}")
        priceRaw = soup.select_one(".price-block__final-price")
        if priceRaw is None:
            return None
        else:
            print(f"[INFO] Price found for article {article}")

    price_text = priceRaw.get_text(strip=True)
    cleaned_price = price_text.replace("\xa0", "").replace("₽", "").replace(" ", "")

    try:
        price = float(cleaned_price)
    except ValueError as e:
        print(f"[ERROR] Couldn't convert price for article {article}: {cleaned_price}")
        return None

    print(f"[INFO] Price for {article}: {price}")
    return price
