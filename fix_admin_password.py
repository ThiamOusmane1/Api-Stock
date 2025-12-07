# fix_admin_password.py
from database import SessionLocal
from models import User
from auth import get_password_hash

def fix_admin_password():
    """Corriger le mot de passe du superadmin"""
    
    db = SessionLocal()
    
    try:
        # Récupérer le superadmin
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("❌ Aucun utilisateur 'admin' trouvé !")
            print("🔧 Créez-le d'abord avec create_superadmin.py")
            return
        
        # Afficher l'état actuel
        print(f"📋 Utilisateur trouvé :")
        print(f"   ID: {admin.id}")
        print(f"   Username: {admin.username}")
        print(f"   Role: {admin.role}")
        print(f"   Password hash actuel: {admin.password_hash[:50]}...")
        
        # Mettre à jour le mot de passe
        new_password = "oussou"  # ⬅️ Changez ici si vous voulez un autre mot de passe
        admin.password_hash = get_password_hash(new_password)
        
        db.commit()
        
        print(f"\n✅ Mot de passe mis à jour avec succès !")
        print(f"   Username: admin")
        print(f"   Nouveau password: {new_password}")
        print(f"   Password hash: {admin.password_hash[:50]}...")
        print(f"\n🔑 Vous pouvez maintenant vous connecter avec :")
        print(f"   Username: admin")
        print(f"   Password: {new_password}")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_password()