import requests, smtplib, os, json
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
import mysql.connector

path = find_dotenv()
load_dotenv(path)
header = os.getenv("HEADER")

json = json.loads(header)
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
            res = requests.get(product["amazon_link"], headers=json).text

            soup = BeautifulSoup(res, "html.parser")

            price = float(soup.find("span", class_="a-offscreen").text.split("GEL")[1].replace(",", "").strip())

            print(price)
            if price < product["target_price"]:
                with smtplib.SMTP(os.getenv("SMTP_ADDRESS"), 587) as connection:
                    connection.starttls()
                    connection.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
                    connection.sendmail(
                        from_addr=os.getenv('EMAIL'),
                        to_addrs=user["email"],
                        msg=f"Amazon Price Alert !!\n\n{soup.find("span", id="productTitle").text.strip()} is on sale for GEL{price}.\n {product["amazon_link"]}".encode(
                            "utf-8"),
                    )
# cursor.close()
# mydb.close()

