from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import schemas, utils
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def check_health():
    return {"message": "Welcome to the Author-Book portal"}

@app.post("/authors/", response_model=schemas.Author)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    return utils.create_author(db, author)

@app.get("/authors/", response_model=list[schemas.Author])
def list_authors(db: Session = Depends(get_db)):
    return utils.get_authors(db)

@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return utils.create_book(db, book)

@app.get("/books/", response_model=list[schemas.Book])
def list_books(db: Session = Depends(get_db)):
    return utils.get_books(db)
