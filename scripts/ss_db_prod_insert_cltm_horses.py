#!/usr/bin/env python3

# Modules

from bs4 import BeautifulSoup
import requests
import sqlite3

connection = sqlite3.connect("../static/db/SS_DB_PROD.db", check_same_thread=False)
c = connection.cursor()

# Variables

url = "https://www.horseracing.net/cheltenham/gold-cup"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

records = []

c.execute("delete from cltm_horses;")
connection.commit()

for i in soup.find_all("div", class_="row-runner"):
    number = i.find("div", class_="fs-num")
    horses = i.find("div", class_="fri-name")
    odds = i.find("div", class_="oi-odds")
    print(number.text)
    print(horses.text[:-3])
    print(odds.text)

    c.execute("INSERT INTO cltm_horses values (?, ?, ?, ?, ?)", (
        f"H{number.text.strip()}",
        f"{number.text.strip()}",
        f"{horses.text.strip().upper()[:-3]}",
        f"{odds.text.strip()}",
        "TBC"))
    connection.commit()
