from pydantic import BaseModel
from typing import List, Optional


# ------------------ BOOK SCHEMAS ------------------

class BookBase(BaseModel):
    title: str
    publisher_name: Optional[str] = None
    price: Optional[int] = None


class BookCreate(BookBase):
    author_id: int


class Book(BookBase):
    id: int

    class Config:
        orm_mode = True


# ------------------ AUTHOR SCHEMAS ------------------

class AuthorBase(BaseModel):
    name: str
    mobile: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int
    # books: List[Book] = []

    class Config:
        orm_mode = True
