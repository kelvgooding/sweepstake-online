"""
Author: Kelvin Gooding
Created: 22/01/2022
Version: 1.000
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import random
import string
from datetime import datetime
import os

# flask variables

app = Flask(__name__)
app.secret_key = os.urandom(26)

# sqlite3 variables

connection = sqlite3.connect("static/db/SS_DB_PROD.db", check_same_thread=False)
c = connection.cursor()

### End User Views ###

@app.route("/", methods=["POST", "GET"])
def index():

    # an empty list array to store all group codes from ss_group table

    all_group_codes = []

    if request.method == "POST":

        # loop through groupid column in ss_group and add codes to all_group_codes list array

        for code in c.execute(f'select groupid from ss_group where groupid="{request.form.get("groupcode").upper()}";'):
            all_group_codes.append(code[0])

        # if the group code exists in the all_group_codes list, proceed

        if request.form.get('groupcode').upper() in all_group_codes:
            session['my_var'] = request.form.get('groupcode').upper()
            return redirect(url_for('group'))

        else:
            flash("INVALID GROUP CODE.")
            flash("PLEASE TRY AGAIN.")

    return render_template("index.html")

@app.route("/create_group", methods=["POST", "GET"])
def create_group():

    # create a 6 character group code

    new_group_code = ''.join(random.choices(string.ascii_uppercase, k=6))

    if request.method == "POST":

        # insert form data into ss_group table

        c.execute("INSERT INTO ss_group VALUES (?, ?, ?, ?, ?, NULL, CURRENT_TIMESTAMP)", (
            f'{request.form.get("num_of_part")}',
            f'{request.form.get("hostname")}',
            f'{request.form.get("email")}',
            f'{request.form.get("entry_price")}',
            f'{new_group_code}',))
        connection.commit()

        # insert form data into ss_group_hosts table

        c.execute("INSERT INTO ss_group_hosts VALUES (?, ?, CURRENT_TIMESTAMP)", (f'{request.form.get("hostname")}', f'{request.form.get("email")}',))
        connection.commit()

        # create table using the the randomly generated 6 character group code

        c.execute(f"CREATE TABLE {new_group_code} (status, full_name, admin, group_code, grp_rank)")
        connection.commit()

        # Insert create group row data into new group code

        c.execute(f"INSERT INTO {new_group_code} values ('Y', '{request.form.get('hostname')}', 'Y', '{new_group_code}', 'TBC')")
        connection.commit()

        # create table group code - XXXXXX_P

        c.execute(f"CREATE TABLE {new_group_code}_P (name, horse_name)")
        connection.commit()

        flash(f"YOUR GROUP CODE IS: {new_group_code.upper()}")
        flash(f"KEEP THIS CODE SAFE.")

    return render_template("create_group.html")

@app.route("/group", methods=["POST", "GET"])
def group():

    # store group code into session

    group_code = session.get('my_var', None)

    # show group host on webpage

    group_host_name = []

    for i in c.execute("select hostname from ss_group where groupid = (?);", (f"{session.get('my_var', None)}",)):
        group_host_name.append(i[0])

    # an empty array for the jackpot total

    jackpot = []

    for i in c.execute("select num_of_part * entry_price as jackpot from ss_group where groupid = (?);",(f"{session.get('my_var', None)}",)):
        jackpot.append(i[0])

    # prize money percentage calculation

    def percentage(percent, whole):
        return (percent * whole) / 100.0

    test = percentage(jackpot[0], 50)

    first = test
    second = percentage(test, 60)
    third = percentage(test, 40)

    # SQL count for participants

    p_count = []

    for i in c.execute("select num_of_part from ss_group where groupid = (?);", (f"{session.get('my_var', None)}",)):
        p_count.append(i[0])

    # price each participant must be using entry_price in the group code table

    PPE = []

    ppe_query = f"select entry_price from ss_group where groupid = '{session.get('my_var', None)}'"

    for i in c.execute(ppe_query):
        PPE.append(i[0])

    # number of horse picks per participant

    horse_picks = (int(40) / int(p_count[0]))

    # SQL to show count of rows in the group code table

    filled = []

    filled_query = f"select count(*) from '{session.get('my_var', None)}'"

    for i in c.execute(filled_query):
        print(filled)
        filled.append(str(i[0]))

    participants_query = f"SELECT '{session.get('my_var', None)}'.status, '{session.get('my_var', None)}'.full_name, gn_horses.h_num, gn_horses.h_name, gn_horses.h_odds, gn_horses.ranked FROM '{session.get('my_var', None)}' LEFT JOIN gn_horses ON '{session.get('my_var', None)}'.grp_rank = gn_horses.h_code;"

    c.execute(participants_query)
    participants = c.fetchall()

    #

    c.execute(f"SELECT status, full_name FROM '{session.get('my_var', None)}';")
    participants2 = c.fetchall()

    c.execute(f'SELECT * FROM gn_horses ORDER BY ranked ASC LIMIT 3;')
    all_horses = c.fetchall()


    if request.method == "POST":
        insertinto = f"INSERT INTO {session.get('my_var', None)} VALUES ('Y', '{request.form.get('join-group')}', 'N', '{session.get('my_var', None)}', 'TBC')"

        c.execute(insertinto)
        connection.commit()

        return redirect(url_for("group"))

    return render_template("group.html",
                           jackpot=jackpot,
                           group_code=group_code,
                           group_host_name=group_host_name,
                           filled=filled,
                           p_count=p_count,
                           participants=participants,
                           participants2=participants2,
                           first=first,
                           second=second,
                           third=third,
                           PPE=PPE,
                           hp=int(horse_picks),
                           all_horses=all_horses, )

@app.route("/group/picks", methods=["POST", "GET"])
def picks():

    groupcode = session.get('my_var2', None)

    # SQL001 - JOIN group code to gn_horses to generate new table.

    c.execute(f"SELECT '{session.get('my_var', None)}_P'.name, gn_horses.h_num, gn_horses.h_name, gn_horses.h_odds, gn_horses.ranked FROM '{session.get('my_var', None)}_P' LEFT JOIN gn_horses ON '{session.get('my_var', None)}_P'.horse_name = gn_horses.h_code;")
    participants = c.fetchall()

    return render_template("picks.html",
                           participants=participants,
                           groupcode=groupcode)

### Admin View ###

@app.route("/admin", methods=["POST", "GET"])
def admin():

    if request.method == "POST":
        c.execute(f"SELECT email, groupid FROM ss_group WHERE email=(?) and groupid=(?);",
                  (f"{request.form.get('admin-email').strip()}", f"{request.form.get('admin-group-id')}",))

        result = c.fetchone()

        if result != (f"{request.form.get('admin-email').strip()}", f"{request.form.get('admin-group-id')}"):
            flash("Login failed. Please try again.")
            return render_template("admin_login.html")

        else:
            session['my_var2'] = request.form.get('admin-group-id').upper()
            return redirect(url_for("admin_group"))

    return render_template("admin_login.html")

@app.route("/admin/group", methods=["POST", "GET"])
def admin_group():
    groupcode = session.get('my_var2', None)
    current_date = datetime.today().strftime("%d/%m/%Y")

    c.execute(f"SELECT status, full_name from '{groupcode}'")
    contacts = c.fetchall()

    c.execute(f'SELECT gen_flag FROM ss_group where groupid="{groupcode}"')
    gen_flag = c.fetchall()

    c.execute(f'select num_of_part from ss_group where groupid="{groupcode}";')
    max_participants = c.fetchall()

    c.execute(f'select entry_price from ss_group where groupid="{groupcode}";')
    entry_price = c.fetchall()

    if request.method == "POST" and request.form.get("updated"):
        print("Update button has been clicked.")
        for i in request.form.getlist('mycheckbox'):
            print(i)
            c.execute(f'UPDATE {groupcode} SET status="Y" WHERE status="N" and full_name=(?)', (i,))
            connection.commit()
        flash("UPDATE HAS BEEN MADE!")
        return redirect(url_for('admin_group'))

    if request.method == "POST" and request.form.get("remove"):
        print("Removed button has been clicked.")
        for i in request.form.getlist('mycheckbox2'):
            c.execute(f"DELETE FROM '{groupcode}' WHERE full_name=(?)", (i,))
            connection.commit()
        flash("REMOVAL HAS BEEN MADE!")
        return redirect(url_for('admin_group'))

    if request.method == "POST" and request.form.get("generate"):

        c.execute(f'SELECT num_of_part from ss_group where groupid="{groupcode}";')
        counted = c.fetchall()[-1][0]
        print(counted)
        print("----- PART CHECK -----")

        if counted == "40":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode};")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")

            c.execute(f"SELECT full_name FROM {groupcode};")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)


            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        if counted == "20":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode};")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")

            c.execute(f"SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode};")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)


            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        if counted == "10":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode};")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")

            c.execute(f"SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode};")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)

            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        if counted == "8":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode}")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")
            c.execute(f"SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode}")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)

            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        if counted == "5":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode}")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")

            c.execute(f"SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode}")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)

            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        if counted == "4":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode}")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")

            c.execute(f"SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode}")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)

            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        if counted == "2":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode}")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")

            c.execute(f"SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode}")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)

            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        if counted == "1":

            print("----- STEP 1 -----")
            # This step is determined by how many players there are. The unions must corrospond.
            generate_list = []
            c.execute(f"SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode} UNION ALL SELECT * FROM {groupcode}")
            for i in c.fetchall():
                generate_list.append(i)
            print(generate_list)

            print("----- STEP 2 -----")

            c.execute(f"SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode} UNION ALL SELECT full_name FROM {groupcode}")
            participants_list = c.fetchall()
            print(participants_list)

            c.execute("SELECT h_code FROM gn_horses;")
            horses_list = c.fetchall()
            print(horses_list)

            print("----- STEP 3 -----")

            while True:

                # every horses in list, number of horses

                pairings = random.sample(horses_list, k=len(horses_list))
                print("----- STEP 3A -----")
                print(pairings)

                if not any(a == b for a, b in zip(horses_list, pairings)):
                    break

            print("----- STEP 3B -----")
            for a, b, cate in zip(participants_list, pairings, generate_list):
                print(f'{a} x {b}')
                c.execute(f"INSERT INTO {groupcode}_P VALUES (?, ?)",
                          (f"{a[0]}", f"{b[0]}"))
                connection.commit()

        print("----- STEP 4 -----")

        c.execute(f'UPDATE ss_group SET gen_flag="Y" where groupid="{groupcode}";')
        connection.commit()
        return redirect(url_for('admin_group'))


    return render_template("admin_group.html",
                           contacts=contacts,
                           groupcode=groupcode,
                           gen_flag=gen_flag,
                           max_participants=max_participants,
                           entry_price=entry_price,
                           current_date=current_date)

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
