from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import VARBINARY
from app.db.database import Base
from app.Encryption.encryption import EncryptedMixin

author_book_association = Table(
    "author_book_association",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True)
)


class Author(Base, EncryptedMixin):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARBINARY(100), unique=True, index=True)
    mobile = Column(VARBINARY(100), unique=True, index=True)

    books = relationship(
        "Book",
        secondary="author_book_association",
        back_populates="authors"
    )

    __encrypted_fields__ = {"name": str, "mobile": str}
    __searchable_fields__ = []


class Book(Base, EncryptedMixin):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(VARBINARY(200), index=True)
    publisher_name = Column(VARBINARY(200), nullable=True)
    price = Column(Integer, nullable=True)

    authors = relationship(
        "Author",
        secondary="author_book_association",
        back_populates="books"
    )

    __encrypted_fields__ = {"title": str, "publisher_name": str}
    __searchable_fields__ = []

