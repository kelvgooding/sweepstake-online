# Modules

from bs4 import BeautifulSoup
import requests
import csv
import sqlite3

connection = sqlite3.connect("../static/db/SS_DB_PROD.db", check_same_thread=False)
c = connection.cursor()

# Variables

url = "https://www.grandnational.org.uk/grand-national-runners.php"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

c.execute("delete from gn_horses;")
connection.commit()

for i in soup.find_all("div", class_="the_banners_banners"):
    number = i.find("div", class_="the_banners_banners__favourite--number")
    horses = i.find("h3")
    odds = i.find("span", class_="the_banners_banners--odds")
    c.execute('INSERT INTO gn_horses values (?, ?, ?, ?, ?)', (f"H{number.text.strip()[1:]}", f"{number.text.strip().replace('#', '')}", f"{horses.text.strip()}", f"{odds.text.strip()}", "TBC"))
    connection.commit()