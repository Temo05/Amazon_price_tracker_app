import requests, smtplib, os, json
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


path = find_dotenv()
load_dotenv(path)
header = os.getenv("HEADER")

def convert_usd_to_gel(usd_amount):
    api_key = os.getenv("CONVERT_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url).json()
    price = usd_amount * response["conversion_rates"]["GEL"]
    return round(price, 2)

#
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="users_for_amazon_tracking_project"
# )
#
# cursor = mydb.cursor()
#
# cursor.execute("""
# SELECT users.email, products.amazon_link, products.target_price
# FROM users
# JOIN products ON users.id = products.user_id
# """)
#
# rows = cursor.fetchall()

# for email, link, desired_price in rows:

DB_LINK=os.getenv("DB_LINK")
DB_KEY = os.getenv("DB_KEY")

HEADERS = {
    "apikey": DB_KEY,
    "Authorization": f"Bearer {DB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

users_list = requests.get(f"{DB_LINK}/rest/v1/users", headers=HEADERS).json()
product_list = requests.get(f"{DB_LINK}/rest/v1/products", headers=HEADERS).json()

for user in users_list:
    for product in product_list:
        if product["user_id"] == user["id"]:

            # res = requests.get(product["amazon_link"], headers=AMAZON_HEADERS, timeout=15).text
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(product["amazon_link"])

            try:
                button = driver.find_element(By.XPATH, "//button[@alt='Continue shopping']")
            except:
                price_whole = driver.find_element(By.CLASS_NAME, "a-price-whole").text.replace(",", "")
                price_fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text
                price = float((".").join([price_whole, price_fraction]))
            else:
                button.click()
                driver.implicitly_wait(2)
                price_whole = driver.find_element(By.CLASS_NAME, "a-price-whole").text.replace(",", "")
                price_fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text
                price = float((".").join([price_whole, price_fraction]))

            price_symbol = driver.find_element(By.CLASS_NAME, "a-price-symbol").text
            if price_symbol == "$":
                price = convert_usd_to_gel(price)
            product_title = driver.find_element(By.ID, "productTitle").text

            if price < product["target_price"]:
                with smtplib.SMTP(os.getenv("SMTP_ADDRESS"), 587) as connection:
                    connection.starttls()
                    connection.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
                    connection.sendmail(
                        from_addr=os.getenv('EMAIL'),
                        to_addrs=user["email"],
                        msg = f"Subject: Amazon Price Alert !!\n\n{product_title} is on sale for GEL{price}.\n {product['amazon_link']}".encode('utf-8')
                    )
            driver.close()

# cursor.close()
# mydb.close()

