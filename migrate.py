# migrate.py
import sqlite3

def migrate():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entreprises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT UNIQUE NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        entreprise_id INTEGER,
        FOREIGN KEY (entreprise_id) REFERENCES entreprises(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entreprise_id INTEGER,
        nom TEXT NOT NULL,
        description TEXT,
        quantite INTEGER NOT NULL DEFAULT 0,
        longueur FLOAT,
        largeur FLOAT,
        hauteur FLOAT,
        poids FLOAT,
        FOREIGN KEY (entreprise_id) REFERENCES entreprises(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS retraits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entreprise_id INTEGER,
        article_id INTEGER,
        quantite INTEGER NOT NULL,
        poids_total FLOAT NOT NULL,
        date TEXT,
        user_id INTEGER,
        FOREIGN KEY (entreprise_id) REFERENCES entreprises(id),
        FOREIGN KEY (article_id) REFERENCES articles(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()
    print("✅ Migration terminée avec succès")

if __name__ == "__main__":
    migrate()
    