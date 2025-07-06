from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.dependencies import get_db
from app.schemas.schemas import AuthorCreate, Author
from app.utils.utils import get_author_by_id, create_author, get_all_authors

author_router = APIRouter(prefix="/authors", tags=["Authors API"])


@author_router.post("/", response_model=Author)
async def create_authors(author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    return await create_author(db, author)


@author_router.get("/", response_model=List[Author])
async def list_authors(db: AsyncSession = Depends(get_db)):
    return await get_all_authors(db)


@author_router.get("/{author_id}", response_model=Author)
async def get_single_author(author_id: int, db: AsyncSession = Depends(get_db)):
    author = await get_author_by_id(db, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author
