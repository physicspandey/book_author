from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import VARBINARY
from app.db.database import Base
from app.Encryption.encryption import EncryptedMixin

"""
Relationship Type: One-to-Many

One author ➝ can write many books

Each book ➝ is written by only one author

# Creating an author and books
author = Author(name="George Orwell")
book1 = Book(title="1984", author=author)
book2 = Book(title="Animal Farm", author=author)

# Add to session
session.add(author)
session.commit()

# Access relationships
print(author.books)  # [book1, book2]
print(book1.author.name)  # George Orwell

"""


class Author(Base, EncryptedMixin):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARBINARY(100), unique=True, index=True)
    mobile = Column(VARBINARY(100), unique=True, index=True)
    books = relationship("Book", back_populates="author")

    __encrypted_fields__ = {"name": str, "mobile": str}
    __searchable_fields__ = []


class Book(Base, EncryptedMixin):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(VARBINARY(200), index=True)
    publisher_name = Column(VARBINARY(200), nullable=True)
    price = Column(Integer, nullable=True)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")

    __encrypted_fields__ = {"title": str, "publisher_name": str}
    __searchable_fields__ = []
