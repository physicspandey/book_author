from fastapi import FastAPI, Depends, APIRouter
from app.db.database import Base, async_engine, sync_engine
from app.apis.authors import author_router
from app.apis.books import book_router

from app.Encryption.encryption import EncryptedMixin

EncryptedMixin.register_encryption_events()

Base.metadata.create_all(bind=sync_engine)

app = FastAPI(
    title="Book Author API",
    version="1.0.0"
)

router = APIRouter()

router.include_router(author_router, prefix="/authors")
router.include_router(book_router, prefix="/books")

app.include_router(router, prefix="/v1/api")


@app.get("/")
def check_health():
    return {"message": "Welcome to the Author-Book portal"}
