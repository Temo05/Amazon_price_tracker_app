import requests, smtplib, os, json
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
import mysql.connector

path = find_dotenv()
load_dotenv(path)
header = os.getenv("HEADER")

AMAZON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def convert_usd_to_gel(usd_amount):
    url = "https://api.exchangerate.host/convert"
    params = {
        "from": "USD",
        "to": "GEL",
        "amount": usd_amount
    }
    response = requests.get(url, params=params).json()
    return response.get("result", usd_amount)

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

            res = requests.get(product["amazon_link"], headers=AMAZON_HEADERS, timeout=15).text

            soup = BeautifulSoup(res, "html.parser")


            try:
                price = float(soup.find("span", class_="a-offscreen").text.split("GEL")[1].replace(",", "").strip())
            except:
                price = float(soup.find("span", class_="a-offscreen").text.split("USD")[1].replace(",", "").strip())
                price = convert_usd_to_gel(price)

            print(price)
            # if price < product["target_price"]:
            #     with smtplib.SMTP(os.getenv("SMTP_ADDRESS"), 587) as connection:
            #         connection.starttls()
            #         connection.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
            #         connection.sendmail(
            #             from_addr=os.getenv('EMAIL'),
            #             to_addrs=user["email"],
            #             msg = f"Subject:Amazon Price Alert !!\n\n{soup.find('span', id='productTitle').text.strip()} is on sale for GEL{price}.\n {product['amazon_link']}".encode('utf-8')
            #         )
# cursor.close()
# mydb.close()

