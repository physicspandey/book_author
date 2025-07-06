from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from app.db.dependencies import get_db
from app.schemas.schemas import AuthorCreate, Author, Book, BookCreate
from app.utils.utils import get_books

book_router = APIRouter(prefix="", tags=["Books API"])


@book_router.post("/books/", response_model=Book)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return await create_book(db, book)


@book_router.get("/books/", response_model=list[Book])
async def list_books(db: Session = Depends(get_db)):
    return await get_books(db)
