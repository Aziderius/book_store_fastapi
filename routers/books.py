from fastapi import APIRouter, Depends, HTTPException, Path
from models import Genre, Books
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_genres(db: db_dependency):
    return db.query(Genre).all()


@router.get("/book/{book_id}", status_code=status.HTTP_200_OK)
async def read_book_by_id(db: db_dependency, book_id: int = Path(gt=0)):
    book_model = db.query(Books).filter(Books.id == book_id).first()
    if book_model is not None:
        return book_model
    raise HTTPException(status_code=404, detail='Book not found.')