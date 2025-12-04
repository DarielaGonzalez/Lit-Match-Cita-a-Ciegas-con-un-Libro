from typing import Optional, List
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    hashed_password: str
    is_author: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    display_name: str

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(index=True)
    title: str
    description: str
    raw_text: Optional[str] = None
    embedding: Optional[List[float]] = Field(default=None, sa_column=Field(..., nullable=True))

class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    active: bool = True
    started_at: datetime = Field(default_factory=datetime.utcnow)

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    book_id: int = Field(index=True)
    rating: Optional[int] = None
    comments: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
