# database.py
from sqlalchemy import create_engine, MetaData
from databases import Database

DATABASE_URL = "sqlite:///./stock.db"

# async DB
database = Database(DATABASE_URL)

# SQLAlchemy engine + metadata
# check_same_thread False for SQLite + SQLAlchemy in multi threads
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata = MetaData()
