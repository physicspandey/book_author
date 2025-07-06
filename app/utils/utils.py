from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.schemas.schemas import AuthorCreate, BookCreate
from app.models.models import Author, Book


async def create_author(db: AsyncSession, author: AuthorCreate):
    db_author = Author(name=author.name, mobile=author.mobile)
    db.add(db_author)
    await db.commit()
    await db.refresh(db_author)
    print("hola")
    return db_author



async def get_author_by_id(db: AsyncSession, author_id: int):
    result = await db.execute(
        select(Author)
        .options(selectinload(Author.books))
        .filter(Author.id == author_id)
    )
    return result.scalar_one_or_none()


async def create_book(db: AsyncSession, book: BookCreate):
    db_book = Book(
        title=book.title,
        publisher_name=book.publisher_name,
        price=book.price,
        author_id=book.author_id
    )
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book


async def get_books(db: AsyncSession):
    result = await db.execute(select(Book))
    return result.scalars().all()


async def get_all_authors(db: AsyncSession):
    result = await db.execute(
        select(Author).options(selectinload(Author.books))
    )
    return result.scalars().all()
