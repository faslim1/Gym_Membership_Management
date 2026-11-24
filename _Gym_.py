import sqlite3
from datetime import date



conn = sqlite3.connect("Gymm.db")

cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")





cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS plans(
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT UNIQUE NOT NULL,
    fee REAL NOT NULL,
    duration INTEGER NOT NULL
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS diet_plans(
    diet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER UNIQUE NOT NULL,
    diet_name TEXT NOT NULL,
    breakfast TEXT,
    lunch TEXT,
    snack TEXT,
    dinner TEXT,

    FOREIGN KEY(plan_id)
    REFERENCES plans(plan_id)
    ON DELETE CASCADE
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS members(
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    plan_id INTEGER NOT NULL,
    join_date TEXT NOT NULL,

    FOREIGN KEY(user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    FOREIGN KEY(plan_id)
    REFERENCES plans(plan_id)
)
""")

conn.commit()

def register():

    print("\n--- USER REGISTRATION ---")

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if username == "" or password == "":
        print("Username and password cannot be empty.")
        return

    try:

        cursor.execute("""
        INSERT INTO users(username, password, role)
        VALUES (?, ?, ?)
        """, (username, password, "User"))

        conn.commit()

        print("Registration successful.")

    except sqlite3.IntegrityError:
        print("Username already exists.")

    except sqlite3.Error as e:
        print("Database error:", e)

def login():

    print("\n--- LOGIN ---")

    username = input("Username: ").strip()
    password = input("Password: ").strip()

    cursor.execute("""
    SELECT user_id, username, role
    FROM users
    WHERE username = ?
    AND password = ?
    """, (username, password))

    user = cursor.fetchone()

    if user:

        print("\nLogin successful.")

        user_id = user[0]
        role = user[2]

        if role == "Admin":
            admin_menu()

        else:
            user_menu(user_id)

    else:
        print("Invalid username or password.")

def add_plan():

    print("\n--- ADD MEMBERSHIP PLAN ---")

    plan_name = input("Plan name: ").strip()

    if plan_name == "":
        print("Plan name cannot be empty.")
        return

    try:

        fee = float(input("Fee: "))
        duration = int(input("Duration in days: "))

        if fee <= 0 or duration <= 0:
            print("Fee and duration must be greater than zero.")
            return

        cursor.execute("""
        INSERT INTO plans(plan_name, fee, duration)
        VALUES (?, ?, ?)
        """, (plan_name, fee, duration))

        conn.commit()

        print("Membership plan added successfully.")

    except ValueError:
        print("Please enter valid numbers.")

    except sqlite3.IntegrityError:
        print("Plan name already exists.")

def view_plans():

    cursor.execute("""
    SELECT plan_id, plan_name, fee, duration
    FROM plans
    """)

    plans = cursor.fetchall()

    if not plans:
        print("No membership plans available.")
        return

    print("\n--- MEMBERSHIP PLANS ---")

    for plan in plans:

        print("-----------------------------")
        print("Plan ID:", plan[0])
        print("Plan:", plan[1])
        print("Fee:", plan[2])
        print("Duration:", plan[3], "days")

def edit_plan():

    view_plans()

    try:

        plan_id = int(input("\nEnter Plan ID to edit: "))

        cursor.execute("""
        SELECT *
        FROM plans
        WHERE plan_id = ?
        """, (plan_id,))

        plan = cursor.fetchone()

        if plan is None:
            print("Invalid Plan ID.")
            return

        new_name = input("New plan name: ").strip()
        new_fee = float(input("New fee: "))
        new_duration = int(input("New duration: "))

        cursor.execute("""
        UPDATE plans
        SET plan_name = ?,
            fee = ?,
            duration = ?
        WHERE plan_id = ?
        """, (
            new_name,
            new_fee,
            new_duration,
            plan_id
        ))

        conn.commit()

        print("Plan updated successfully.")

    except ValueError:
        print("Invalid input.")

def delete_plan():

    view_plans()

    try:

        plan_id = int(input("Enter Plan ID to delete: "))

        cursor.execute("""
        DELETE FROM plans
        WHERE plan_id = ?
        """, (plan_id,))

        if cursor.rowcount == 0:
            print("Plan not found.")

        else:
            conn.commit()
            print("Plan deleted.")

    except ValueError:
        print("Invalid Plan ID.")

def add_diet():

    view_plans()

    try:

        plan_id = int(input("\nEnter Plan ID: "))

        cursor.execute("""
        SELECT *
        FROM plans
        WHERE plan_id = ?
        """, (plan_id,))

        if cursor.fetchone() is None:
            print("Invalid Plan ID.")
            return

        diet_name = input("Diet name: ")
        breakfast = input("Breakfast: ")
        lunch = input("Lunch: ")
        snack = input("Snack: ")
        dinner = input("Dinner: ")

        cursor.execute("""
        INSERT INTO diet_plans(
            plan_id,
            diet_name,
            breakfast,
            lunch,
            snack,
            dinner
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            plan_id,
            diet_name,
            breakfast,
            lunch,
            snack,
            dinner
        ))

        conn.commit()

        print("Diet plan added successfully.")

    except ValueError:
        print("Invalid Plan ID.")

    except sqlite3.IntegrityError:
        print("This membership plan already has a diet.")

def view_diets():

    cursor.execute("""
    SELECT
        p.plan_id,
        p.plan_name,
        d.diet_name,
        d.breakfast,
        d.lunch,
        d.snack,
        d.dinner

    FROM plans p

    LEFT JOIN diet_plans d
    ON p.plan_id = d.plan_id
    """)

    diets = cursor.fetchall()

    print("\n--- DIET PLANS ---")

    for diet in diets:

        print("\n-------------------------")
        print("Plan ID:", diet[0])
        print("Membership:", diet[1])
        print("Diet:", diet[2])
        print("Breakfast:", diet[3])
        print("Lunch:", diet[4])
        print("Snack:", diet[5])
        print("Dinner:", diet[6])

def edit_diet():

    view_diets()

    try:

        plan_id = int(input("\nEnter Plan ID: "))

        cursor.execute("""
        SELECT *
        FROM diet_plans
        WHERE plan_id = ?
        """, (plan_id,))

        if cursor.fetchone() is None:
            print("Diet plan not found.")
            return

        diet_name = input("New diet name: ")
        breakfast = input("New breakfast: ")
        lunch = input("New lunch: ")
        snack = input("New snack: ")
        dinner = input("New dinner: ")

        cursor.execute("""
        UPDATE diet_plans

        SET diet_name = ?,
            breakfast = ?,
            lunch = ?,
            snack = ?,
            dinner = ?

        WHERE plan_id = ?
        """, (
            diet_name,
            breakfast,
            lunch,
            snack,
            dinner,
            plan_id
        ))

        conn.commit()

        print("Diet updated successfully.")

    except ValueError:
        print("Invalid Plan ID.")

def delete_diet():

    try:

        plan_id = int(input("Enter Plan ID: "))

        cursor.execute("""
        DELETE FROM diet_plans
        WHERE plan_id = ?
        """, (plan_id,))

        if cursor.rowcount == 0:
            print("Diet not found.")

        else:
            conn.commit()
            print("Diet deleted.")

    except ValueError:
        print("Invalid ID.")

def join_membership(user_id):

    view_plans()

    try:

        plan_id = int(input("\nChoose Plan ID: "))

        cursor.execute("""
        SELECT *
        FROM plans
        WHERE plan_id = ?
        """, (plan_id,))

        if cursor.fetchone() is None:
            print("Invalid Plan ID.")
            return

        cursor.execute("""
        SELECT *
        FROM members
        WHERE user_id = ?
        """, (user_id,))

        if cursor.fetchone():
            print("You already have a membership.")
            return

        join_date = date.today().isoformat()

        cursor.execute("""
        INSERT INTO members(
            user_id,
            plan_id,
            join_date
        )
        VALUES (?, ?, ?)
        """, (
            user_id,
            plan_id,
            join_date
        ))

        conn.commit()

        print("Membership joined successfully.")

    except ValueError:
        print("Invalid Plan ID.")

def view_my_membership(user_id):

    cursor.execute("""
    SELECT
        p.plan_name,
        p.fee,
        p.duration,
        m.join_date

    FROM members m

    JOIN plans p
    ON m.plan_id = p.plan_id

    WHERE m.user_id = ?
    """, (user_id,))

    membership = cursor.fetchone()

    if membership:

        print("\n--- MY MEMBERSHIP ---")
        print("Plan:", membership[0])
        print("Fee:", membership[1])
        print("Duration:", membership[2], "days")
        print("Join Date:", membership[3])

    else:
        print("You do not have a membership.")

def view_my_diet(user_id):

    cursor.execute("""
    SELECT
        p.plan_name,
        d.diet_name,
        d.breakfast,
        d.lunch,
        d.snack,
        d.dinner

    FROM members m

    JOIN plans p
    ON m.plan_id = p.plan_id

    JOIN diet_plans d
    ON p.plan_id = d.plan_id

    WHERE m.user_id = ?
    """, (user_id,))

    diet = cursor.fetchone()

    if diet:

        print("\n--- MY DIET PLAN ---")
        print("Membership:", diet[0])
        print("Diet:", diet[1])
        print("Breakfast:", diet[2])
        print("Lunch:", diet[3])
        print("Snack:", diet[4])
        print("Dinner:", diet[5])

    else:
        print("No diet plan available.")

def cancel_membership(user_id):

    cursor.execute("""
    DELETE FROM members
    WHERE user_id = ?
    """, (user_id,))

    if cursor.rowcount == 0:
        print("You do not have a membership.")

    else:
        conn.commit()
        print("Membership cancelled.")

def view_members():

    cursor.execute("""
    SELECT
        m.member_id,
        u.username,
        p.plan_name,
        p.fee,
        m.join_date

    FROM members m

    JOIN users u
    ON m.user_id = u.user_id

    JOIN plans p
    ON m.plan_id = p.plan_id
    """)

    members = cursor.fetchall()

    print("\n--- MEMBERS ---")

    for member in members:

        print("----------------------")
        print("Member ID:", member[0])
        print("Username:", member[1])
        print("Plan:", member[2])
        print("Fee:", member[3])
        print("Join Date:", member[4])

def update_member_plan():

    view_members()
    view_plans()

    try:

        member_id = int(input("Enter Member ID: "))
        new_plan_id = int(input("Enter New Plan ID: "))

        cursor.execute("""
        UPDATE members
        SET plan_id = ?
        WHERE member_id = ?
        """, (
            new_plan_id,
            member_id
        ))

        if cursor.rowcount == 0:
            print("Member not found.")

        else:
            conn.commit()
            print("Membership plan updated.")

    except ValueError:
        print("Invalid ID.")

def delete_member():

    view_members()

    try:

        member_id = int(input("Enter Member ID: "))

        cursor.execute("""
        DELETE FROM members
        WHERE member_id = ?
        """, (member_id,))

        if cursor.rowcount == 0:
            print("Member not found.")

        else:
            conn.commit()
            print("Member deleted.")

    except ValueError:
        print("Invalid Member ID.")

def admin_menu():

    while True:

        print("""
ADMIN MENU

1. Add Membership Plan
2. View Membership Plans
3. Edit Membership Plan
4. Delete Membership Plan

5. Add Diet Plan
6. View Diet Plans
7. Edit Diet Plan
8. Delete Diet Plan

9. View Members
10. Update Member Plan
11. Delete Member

12. Logout
""")

        choice = input("Enter choice: ")

        if choice == "1":
            add_plan()

        elif choice == "2":
            view_plans()

        elif choice == "3":
            edit_plan()

        elif choice == "4":
            delete_diet()

        elif choice == "5":
            add_diet()

        elif choice == "6":
            view_my_diet()

        elif choice == "8":
            delete_diet()

        elif choice == "9":
            view_members()

        elif choice == "10":
            update_member_plan()

        elif choice == "11":
            delete_member()

        elif choice == "12":
            print("Logged out.")
            break

        else:
            print("Invalid choice.")

def user_menu(user_id):

    while True:

        print("""
========== MEMBER MENU ==========

1. View Membership Plans
2. View Diet Plans
3. Join Membership
4. View My Membership
5. View My Diet Plan
6. Cancel Membership
7. Logout
""")

        choice = input("Enter choice: ")

        if choice == "1":
            view_plans()

        elif choice == "2":
            view_diets()

        elif choice == "3":
            join_membership(user_id)

        elif choice == "4":
            view_my_membership(user_id)

        elif choice == "5":
            view_my_diet(user_id)

        elif choice == "6":
            cancel_membership(user_id)

        elif choice == "7":
            print("Logged out.")
            break

        else:
            print("Invalid choice.")

def create_admin():

    try:

        cursor.execute("""
        INSERT INTO users(username, password, role)
        VALUES (?, ?, ?)
        """, (
            "admin",
            "admin123",
            "Admin"
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

def main():

    create_admin()

    while True:

        print("""


1. Register
2. Login
3. Exit
""")

        choice = input("Enter choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            login()

        elif choice == "3":
            print("Thank you.")
            break

        else:
            print("Invalid choice.")


main()

conn.close()