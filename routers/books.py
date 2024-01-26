from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import Genre, Books, Author
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
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


@router.get("/books/title", status_code=status.HTTP_200_OK)
async def read_book_by_title(db:db_dependency, book_title: str = Query(..., min_length=2, max_length=100)):

    book_exact = db.query(Books).filter(func.lower(Books.title) == func.lower(book_title)).all()
    if book_exact:
        return book_exact
    
    book_model = db.query(Books).filter(func.lower(Books.title).ilike(func.lower(f"%{book_title}%"))).limit(50).all()
    if book_model:
        return book_model
    
    raise HTTPException(status_code=404, detail='Book not found')


@router.get("/books/author", status_code=status.HTTP_200_OK)
async def read_book_by_author(db: db_dependency, book_author: str = Query(..., min_length=2)):

    author_exact = db.query(Author).filter(func.lower(Author.author_name) == func.lower(book_author)).first()
    if author_exact:
        return author_exact
    
    author_model = db.query(Author).filter(func.lower(Author.author_name).ilike(func.lower(f"%{book_author}%"))).limit(10).all()
    if author_model:
        return author_model
    
    raise HTTPException(status_code=404, detail='Book not found')