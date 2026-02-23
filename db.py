import sqlite3
import os

DB_PATH = './data/app.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS feature_flags (id INTEGER PRIMARY KEY, name TEXT, description TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS feature_flags_enabled_users (id INTEGER PRIMARY KEY, flag_id INTEGER, user_id INTEGER)")
    conn.commit()
    conn.close()

'''
Users
'''

def add_user(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


'''
Feature flags
'''
def get_all_feature_flags():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feature_flags")
    rows = cursor.fetchall()

    result = []

    for row in rows:
        cursor_result = conn.cursor()
        cursor_result.execute("SELECT user_id FROM feature_flags_enabled_users WHERE flag_id = " + str(row[0]))


        global_default_state = False
        enabled_users = []

        for user_row in cursor_result.fetchall():
            user_id = user_row[0]
            if user_id == -1:
                global_default_state = True
            else:
                enabled_users.append(int(user_id))

        result.append({
            "id": row[0],
            "name": row[1],
            "default_state": global_default_state,
            "enabled_users": enabled_users
        })

    conn.close()

    return result

def get_feature_flag_by_id(flag_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feature_flags WHERE id = ?", (flag_id,))
    row = cursor.fetchall()[0]

    result = None

    cursor_result = conn.cursor()
    cursor_result.execute("SELECT user_id FROM feature_flags_enabled_users WHERE flag_id = " + str(flag_id))

    global_default_state = False
    enabled_users = []

    for user_row in cursor_result.fetchall():
        user_id = user_row[0]
        if user_id == -1:
            global_default_state = True
        else:
            enabled_users.append(int(user_id))

    result = {
        "id": row[0],
        "name": row[1],
        "default_state": global_default_state,
        "enabled_users": enabled_users
    }

    conn.close()

    return result

def add_feature_flag(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feature_flags (name) VALUES (?) returning id", (name,))
    id = cursor.fetchall()[0][0]
    conn.commit()
    conn.close()

    return int(id)

def add_feature_flag_enabled_user(flag_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feature_flags_enabled_users (flag_id, user_id) VALUES (?, ?)", (flag_id, user_id))
    conn.commit()
    conn.close()

def delete_feature_flag_enabled_user(flag_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feature_flags_enabled_users WHERE flag_id = ? AND user_id = ?", (flag_id, user_id))
    conn.commit()
    conn.close()


'''
Miscellaneous
'''

def count_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
