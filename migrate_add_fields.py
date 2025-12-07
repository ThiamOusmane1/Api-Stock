# migrate_add_fields.py
"""
Script pour ajouter les nouveaux champs à la table users
Exécuter : python migrate_add_fields.py
"""
from sqlalchemy import text
from database import engine, SessionLocal
from models import Base

def migrate():
    """Ajouter les nouveaux champs à la table users"""
    db = SessionLocal()
    
    try:
        print("🔄 Migration en cours...")
        
        # Ajouter les colonnes si elles n'existent pas
        with engine.connect() as conn:
            # first_login
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN first_login BOOLEAN DEFAULT TRUE
                """))
                conn.commit()
                print("✅ Colonne 'first_login' ajoutée")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("ℹ️ Colonne 'first_login' existe déjà")
                else:
                    print(f"⚠️ Erreur first_login: {e}")
            
            # password_reset_required
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN password_reset_required BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("✅ Colonne 'password_reset_required' ajoutée")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("ℹ️ Colonne 'password_reset_required' existe déjà")
                else:
                    print(f"⚠️ Erreur password_reset_required: {e}")
            
            # email
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email VARCHAR
                """))
                conn.commit()
                print("✅ Colonne 'email' ajoutée")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("ℹ️ Colonne 'email' existe déjà")
                else:
                    print(f"⚠️ Erreur email: {e}")
            
            # created_at
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """))
                conn.commit()
                print("✅ Colonne 'created_at' ajoutée")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("ℹ️ Colonne 'created_at' existe déjà")
                else:
                    print(f"⚠️ Erreur created_at: {e}")
        
        # Mettre first_login = False pour les utilisateurs existants (déjà connectés)
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE users 
                SET first_login = FALSE 
                WHERE first_login IS NULL
            """))
            conn.commit()
            print("✅ Utilisateurs existants mis à jour (first_login = False)")
        
        print("\n🎉 Migration terminée avec succès !")
        print("\nℹ️ Notes :")
        print("- Les utilisateurs existants ont first_login=False (déjà connectés)")
        print("- Les nouveaux utilisateurs créés auront first_login=True")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()