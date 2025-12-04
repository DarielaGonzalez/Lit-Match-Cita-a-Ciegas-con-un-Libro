from fastapi import FastAPI, HTTPException, Depends, Form
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from db import init_db, get_session
from models import User, Book, Author, Subscription, Feedback
from sqlmodel import select
from recommend import embed_texts, rank_books_by_embedding, get_model
from typing import List
import json

SECRET_KEY = "dev-secret-change-me"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Lit-Match Prototype")


class RegisterIn(BaseModel):
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class QuestionIn(BaseModel):
    answers: List[str]


@app.on_event("startup")
def on_startup():
    init_db()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain, hashed) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


@app.post('/api/register')
def register(inp: RegisterIn):
    with get_session() as sess:
        existing = sess.exec(select(User).where(User.email == inp.email)).first()
        if existing:
            raise HTTPException(400, "Email already registered")
        user = User(email=inp.email, hashed_password=hash_password(inp.password))
        sess.add(user)
        sess.commit()
        sess.refresh(user)
        token = create_token({"user_id": user.id})
        return {"token": token, "user": {"id": user.id, "email": user.email}}


@app.post('/api/login')
def login(inp: LoginIn):
    with get_session() as sess:
        user = sess.exec(select(User).where(User.email == inp.email)).first()
        if not user or not verify_password(inp.password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")
        token = create_token({"user_id": user.id})
        return {"token": token, "user": {"id": user.id, "email": user.email}}


def get_user_from_token(token: str):
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get('user_id')
    with get_session() as sess:
        user = sess.get(User, user_id)
        return user


@app.post('/api/questionnaire')
def questionnaire(data: QuestionIn, token: str = Form(...)):
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    # For prototyping: embed the concatenated answers as user 'profile'
    text = " ".join(data.answers)
    model = get_model()
    emb = model.encode([text], convert_to_numpy=True)[0].tolist()
    # Save to subscription as naive storage or attach to user -- here we just return
    return {"embedding": emb}


@app.post('/api/author/book')
def author_register_book(title: str = Form(...), description: str = Form(...), token: str = Form(...)):
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    with get_session() as sess:
        # Ensure author entry
        author = sess.exec(select(Author).where(Author.user_id == user.id)).first()
        if not author:
            author = Author(user_id=user.id, display_name=user.email)
            sess.add(author); sess.commit(); sess.refresh(author)
        book = Book(author_id=author.id, title=title, description=description)
        # compute embedding for description
        emb = embed_texts([description])[0]
        book.embedding = emb
        sess.add(book); sess.commit(); sess.refresh(book)
        return {"book": {"id": book.id, "title": book.title}}


@app.get('/api/books')
def list_books():
    with get_session() as sess:
        books = sess.exec(select(Book)).all()
        out = []
        for b in books:
            out.append({"id": b.id, "title": b.title, "description": b.description, "embedding": b.embedding})
        return {"books": out}


class RecommendIn(BaseModel):
    user_embedding: List[float]


@app.post('/api/recommend')
def recommend(inp: RecommendIn):
    with get_session() as sess:
        db_books = sess.exec(select(Book)).all()
        books = []
        for b in db_books:
            books.append({"id": b.id, "title": b.title, "description": b.description, "embedding": b.embedding})
        recs = rank_books_by_embedding(inp.user_embedding, books, top_k=10)
        return {"results": recs}


@app.post('/api/feedback')
def feedback(user_id: int = Form(...), book_id: int = Form(...), rating: int = Form(None), comments: str = Form(None)):
    with get_session() as sess:
        fb = Feedback(user_id=user_id, book_id=book_id, rating=rating, comments=comments)
        sess.add(fb); sess.commit(); sess.refresh(fb)
        return {"ok": True}


@app.post('/api/subscribe')
def subscribe(user_id: int = Form(...)):
    # Stub: in production integrate Stripe or similar
    with get_session() as sess:
        sub = Subscription(user_id=user_id, active=True)
        sess.add(sub); sess.commit(); sess.refresh(sub)
        return {"subscription_id": sub.id, "active": sub.active}
