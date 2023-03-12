#!/usr/bin/env python3

# Modules

import sqlite3

connection = sqlite3.connect("../static/db/SS_DB_PROD.db", check_same_thread=False)
c = connection.cursor()

# creation of list named tables

tables = []

# append all database tables to tables list, excluding cltm_horses, ss_group, ss_group_hosts

for i in c.execute("SELECT name FROM sqlite_master where name <> 'cltm_horses' and name <> 'ss_group' and name <> 'ss_group_hosts';"):
    tables.append(i[0])

# delete all database tables in tables list

for i in tables:
    c.execute(f"DROP TABLE {i}")

# delete all rows in ss_group_hosts

c.execute("DELETE FROM ss_group_hosts;")

# delete all rows in ss_group

c.execute("DELETE FROM ss_group;")
connection.commit()