import sqlite3
from crypto_utils import encrypt_password, decrypt_password

# подключение к базе (создаст файл если нет)
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

# создаём таблицу
cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    password TEXT
)
""")

conn.commit()

# сохранить пароль (с шифрованием)
def save_password(user_id, password):
    encrypted = encrypt_password(password)
    cursor.execute(
        "INSERT INTO passwords (user_id, password) VALUES (?, ?)",
        (user_id, encrypted)
    )
    conn.commit()

# получить пароли пользователя (с расшифровкой)
def get_passwords(user_id):
    cursor.execute(
        "SELECT id, password FROM passwords WHERE user_id = ?",
        (user_id,)
    )
    rows = cursor.fetchall()
    return [(pid, decrypt_password(pwd)) for pid, pwd in rows]

# удалить пароль
def delete_password(password_id):
    cursor.execute(
        "DELETE FROM passwords WHERE id = ?",
        (password_id,)
    )
    conn.commit()