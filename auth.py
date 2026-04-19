# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, RoleEnum, CompanyStatusEnum
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_SUPER_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"🔑 Token créé: {token[:50]}...")  # ✅ DEBUG
    return token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"🔍 Décodage du token: {token[:50]}...")  # ✅ DEBUG
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f"✅ Token décodé, username: {username}")  # ✅ DEBUG


        if username is None:
            print("❌ Token décodé mais username manquant")  # ✅ DEBUG
            raise credentials_exception
    except JWTError as e:
        print(f"❌ Erreur JWT: {e}")  # ✅ DEBUG
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print("❌ Utilisateur non trouvé dans la DB")  # ✅ DEBUG
        raise credentials_exception
    
    print(f"✅ Utilisateur trouvé: {user.username}")  # ✅ DEBUG

    # 🚫 BLOCAGE ENTREPRISE
    if user.company:
        if user.company.status != CompanyStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail="Entreprise suspendue ou résiliée"
            )
        
    return user

def require_superadmin(user: User = Depends(get_current_user)):
    if user.role != RoleEnum.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Superadmin requis")
    return user

def require_admin_or_super(user: User = Depends(get_current_user)):
    if user.role not in (RoleEnum.ADMIN, RoleEnum.SUPERADMIN):
        raise HTTPException(status_code=403, detail="Admin requis")
    return user

# Fonction utilitaire pour authentifier un utilisateur
def authenticate_user(db: Session, username: str, password: str):
    print(f"🔐 Authentification de l'utilisateur: {username}")  # ✅ DEBUG
    user = db.query(User).filter(User.username == username).first()


    if not user:
        print(f"❌ Utilisateur '{username}' introuvable")  # ✅ DEBUG    
        return None
    

    if not verify_password(password, user.password_hash):
        print(f"❌ Mot de passe incorrect pour l'utilisateur '{username}'")  # ✅ DEBUG
        return None
    
    print(f"✅ Utilisateur '{username}' authentifié avec succès")  # ✅ DEBUG
    return user