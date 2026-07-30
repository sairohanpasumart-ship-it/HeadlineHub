import sqlite3

connection = sqlite3.connect('headlinelab.db')
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL,
        source TEXT NOT NULL,
        published TEXT,
        summary TEXT
    )
""")

connection.commit()
connection.close()

