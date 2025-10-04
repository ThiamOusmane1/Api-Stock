# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import database
from models import users
from sqlalchemy import select
import schemas

# CHANGE this secret in production, keep safe (env var)
SECRET_KEY = "CHANGE_ME_SUPER_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    q = select(users).where(users.c.username == username)
    user = await database.fetch_one(q)
    if not user:
        raise credentials_exception
    return user

async def require_superadmin(user = Depends(get_current_user)):
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin requis")
    return user

async def require_admin_or_super(user = Depends(get_current_user)):
    # admin or superadmin allowed
    if user["role"] not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin requis")
    return user
