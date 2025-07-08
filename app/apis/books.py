from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.models import Book, Author
from app.schemas.schemas import BookCreate, BookOut, BookUpdate
from app.db.dependencies import get_db

book_router = APIRouter(prefix="", tags=["Books API"])


@book_router.post("/", response_model=BookOut)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Author).where(Author.id.in_(book.author_ids)))
    authors = result.scalars().all()
    if len(authors) != len(book.author_ids):
        raise HTTPException(status_code=400, detail="One or more author IDs are invalid")

    db_book = Book(
        title=book.title,
        publisher_name=book.publisher_name,
        price=book.price,
        authors=authors
    )
    db.add(db_book)
    await db.commit()

    # Re-fetch with authors eagerly loaded
    result = await db.execute(
        select(Book).options(selectinload(Book.authors)).where(Book.id == db_book.id)
    )
    book_with_authors = result.scalar_one()
    return book_with_authors


@book_router.get("/", response_model=list[BookOut])
async def get_all_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).options(selectinload(Book.authors)))
    return result.scalars().all()


@book_router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Book).options(selectinload(Book.authors)).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@book_router.put("/{book_id}", response_model=BookOut)
async def update_book(book_id: int, book_update: BookUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).options(selectinload(Book.authors)).where(Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_update.title is not None:
        db_book.title = book_update.title
    if book_update.publisher_name is not None:
        db_book.publisher_name = book_update.publisher_name
    if book_update.price is not None:
        db_book.price = book_update.price

    if book_update.author_ids is not None:
        # Fetch authors for new IDs
        result = await db.execute(select(Author).where(Author.id.in_(book_update.author_ids)))
        authors = result.scalars().all()
        if len(authors) != len(book_update.author_ids):
            raise HTTPException(status_code=400, detail="One or more author IDs are invalid")
        db_book.authors = authors

    await db.commit()
    await db.refresh(db_book)
    return db_book


@book_router.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.delete(book)
    await db.commit()
    return {"detail": "Book deleted successfully"}
