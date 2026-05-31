import sqlite3

DB_PATH = "app.db"  # adapte si le nom est différent

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ajouter la colonne is_active si elle n'existe pas
try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
    print("✅ Colonne is_active ajoutée avec succès")
except sqlite3.OperationalError as e:
    print("⚠️", e)

conn.commit()
conn.close()
