"""
Script de migration pour ajouter la colonne sub_role à la table users
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL non définie dans .env")

engine = create_engine(DATABASE_URL)

def run_migration():
    with engine.connect() as conn:

        # 1 — Vérifier si la colonne existe déjà
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='sub_role'
        """))
        if result.fetchone():
            print("✅ La colonne sub_role existe déjà — migration ignorée")
            return

        print("🔧 Ajout des valeurs manquantes au type ENUM...")

        # 2 — Ajouter les valeurs manquantes au type ENUM existant
        valeurs = ['commercial', 'magasinier', 'chef_chantier', 'gestionnaire_stock', 'aucun']
        for valeur in valeurs:
            try:
                conn.execute(text(f"ALTER TYPE subroleenum ADD VALUE IF NOT EXISTS '{valeur}'"))
                conn.commit()
                print(f"   ✅ Valeur '{valeur}' ajoutée")
            except Exception as e:
                conn.rollback()
                print(f"   ℹ️ '{valeur}' : {e}")

        # 3 — Ajouter la colonne avec la valeur par défaut
        print("🔧 Ajout de la colonne sub_role...")
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS sub_role subroleenum 
                NOT NULL DEFAULT 'aucun'
            """))
            conn.commit()
            print("✅ Colonne sub_role ajoutée avec succès !")
        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur ajout colonne : {e}")
            raise

if __name__ == "__main__":
    print("🚀 Migration sub_role")
    print("=" * 50)
    run_migration()
    print("=" * 50)
    print("✅ Migration terminée !")
