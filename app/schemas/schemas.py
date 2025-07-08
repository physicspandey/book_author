from pydantic import BaseModel
from typing import List, Optional


class AuthorBase(BaseModel):
    name: str
    mobile: str


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = None
    mobile: str | None = None


class AuthorOut(AuthorBase):
    id: int

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    title: str
    publisher_name: Optional[str] = None
    price: Optional[int] = None


class BookCreate(BookBase):
    author_ids: List[int]


class BookUpdate(BaseModel):
    title: Optional[str] = None
    publisher_name: Optional[str] = None
    price: Optional[int] = None
    author_ids: Optional[List[int]] = None


class AuthorOut(BaseModel):
    id: int
    name: str
    mobile: str

    class Config:
        orm_mode = True


class BookOut(BookBase):
    id: int
    authors: List[AuthorOut]

    class Config:
        orm_mode = True
