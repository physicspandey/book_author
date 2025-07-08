from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.future import select

from app.models.models import Author
from app.schemas.schemas import AuthorCreate, AuthorOut, AuthorUpdate
from app.db.dependencies import get_db

author_router = APIRouter(prefix="/authors", tags=["Authors API"])


@author_router.post("/create", response_model=AuthorOut)
async def create_author(author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    db_author = Author(name=author.name, mobile=author.mobile)
    db.add(db_author)
    await db.commit()
    await db.refresh(db_author)
    return db_author


@author_router.get("/fetch_all", response_model=List[AuthorOut])
async def get_all_authors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author))
    return result.scalars().all()


@author_router.get("/fetch/{author_id}", response_model=AuthorOut)
async def get_author(author_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@author_router.put("/update/{author_id}", response_model=AuthorOut)
async def update_author(author_id: int, updated: AuthorUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    if updated.name is not None:
        author.name = updated.name
    if updated.mobile is not None:
        author.mobile = updated.mobile

    await db.commit()
    await db.refresh(author)
    return author


@author_router.delete("/delete/{author_id}")
async def delete_author(author_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    await db.delete(author)
    await db.commit()
    return {"detail": "Author deleted successfully"}
