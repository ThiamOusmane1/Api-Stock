# create_superadmin.py
from database import SessionLocal, engine, Base
from models import User, RoleEnum
from auth import get_password_hash

def create_superadmin():
    """Créer un superadmin par défaut"""
    
    # Créer les tables si elles n'existent pas
    print("📦 Création des tables...")
    Base.metadata.create_all(bind=engine)
    
    # Créer une session
    db = SessionLocal()
    
    try:
        # Vérifier si le superadmin existe déjà
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("❌ Le superadmin 'admin' existe déjà !")
            print(f"   ID: {existing_admin.id}")
            print(f"   Username: {existing_admin.username}")
            print(f"   Role: {existing_admin.role}")
        else:
            # Créer le superadmin
            superadmin = User(
                username="admin",
                password_hash=get_password_hash("admin1"),
                role=RoleEnum.SUPERADMIN,
                company_id=None
            )
            db.add(superadmin)
            db.commit()
            db.refresh(superadmin)
            
            print("✅ Superadmin créé avec succès !")
            print(f"   ID: {superadmin.id}")
            print(f"   Username: admin")
            print(f"   Password: admin1")
            print(f"   Role: {superadmin.role}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_superadmin()