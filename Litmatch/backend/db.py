from sqlmodel import create_engine, SQLModel, Session
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "litmatch.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
