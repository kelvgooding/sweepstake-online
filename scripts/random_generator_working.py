"""
Author: Kelvin Gooding
Created: DD/MM/YYYY
Version: 1.000
"""

# Modules

# Classes / Methods

# Variables

# Script

import random
import sqlite3

connection = sqlite3.connect("../static/db/SS_DB_PROD.db", check_same_thread=False)
c = connection.cursor()

c.execute("SELECT full_name FROM DFDIAN UNION ALL SELECT full_name FROM DFDIAN;")
participants_list = c.fetchall()

c.execute("SELECT h_code FROM gn_horses;")
horses_list = c.fetchall()

### Fixed List

#participants_list = ["Player A", "Player B", "Player C", "Player D", "Player E", "Player F", "Player G", "Player H", "Player I", "Player J"]
#horses_list = ["Player A", "Player B", "Player C", "Player D", "Player E"]



while True:

    # every horses in list, number of horses

    pairings = random.sample(horses_list, k=len(horses_list))

    if not any(a == b for a, b in zip(horses_list, pairings)):
        break

for a, b in zip(participants_list, pairings):
    print(f'{a} x {b}')