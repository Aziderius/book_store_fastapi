from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import Genre, Books, Author
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func, select
from sqlalchemy import join
from starlette import status
from enum import Enum


router = APIRouter(
    prefix='/books',
    tags=['books']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_books(db: db_dependency):
    return db.query(Books).all()


@router.get("/genre/", status_code=status.HTTP_200_OK)
async def read_all_genres(db: db_dependency):
    return db.query(Genre).all()


@router.get("/author/", status_code=status.HTTP_200_OK)
async def read_all_authors(db: db_dependency):
    return db.query(Author).all()


@router.get("/find_author/", status_code=status.HTTP_200_OK)
async def find_author(db: db_dependency, book_author: str = Query(..., min_length=2)):

    author_exact = db.query(Author).filter(func.lower(Author.author_name) == func.lower(book_author)).first()
    if author_exact:
        return author_exact
    
    author_model = db.query(Author).filter(func.lower(Author.author_name).ilike(func.lower(f"%{book_author}%"))).limit(10).all()
    if author_model:
        return author_model
    
    raise HTTPException(status_code=404, detail='Book not found')


@router.get("/books_title/", status_code=status.HTTP_200_OK)
async def read_books_by_title(db:db_dependency, book_title: str = Query(..., min_length=2, max_length=100)):

    book_exact = db.query(Books).filter(func.lower(Books.title) == func.lower(book_title)).all()
    if book_exact:
        return book_exact
    
    book_model = db.query(Books).filter(func.lower(Books.title).ilike(func.lower(f"%{book_title}%"))).limit(50).all()
    if book_model:
        return book_model
    
    raise HTTPException(status_code=404, detail='Book not found')


@router.get("/books_author/", status_code=status.HTTP_200_OK)
async def read_books_by_author(db:db_dependency, author: str = Query(..., min_length=2)):

    author_model = select(Books, Author.author_name).select_from(join(Books, Author, Books.author_id == Author.id)).where(func.lower(Author.author_name) == func.lower(author))
    result = db.execute(author_model).fetchall()

    books = [row[0] for row in result]
    if books:
        return books

    raise HTTPException(status_code=404, detail=f'Books with genre "{author}" not found')


@router.get("/books_genres/", status_code=status.HTTP_200_OK)
async def read_books_by_genre(db:db_dependency, genre_name: str = Query(...)):
    # Realizar una join para obtener los libros y los nombres de géneros correspondientes
    genre_model = select(Books, Genre.genre_name).select_from(join(Books, Genre, Books.genre_id == Genre.id)).where(func.lower(Genre.genre_name) == func.lower(genre_name))
    result = db.execute(genre_model).fetchall()

    # Extraer los libros de la consulta
    books = [row[0] for row in result]
    if books:
        return books

    raise HTTPException(status_code=404, detail=f'Books with genre "{genre_name}" not found')


@router.get("/books_rating/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(db:db_dependency, rating: int = Query(gt=0, lt=6)):

    rating_model = db.query(Books).filter(Books.rating == rating).all()
    if rating_model is not None:
        return rating_model
    
    raise HTTPException(status_code=404, detail='Books not found.')


@router.get("/books_published_year/", status_code=status.HTTP_200_OK)
async def read_books_by_published_year(db:db_dependency, published_year: int = Query(title='Published year', gt=1000, lt=3000)):

    year_model = db.query(Books).filter(Books.published_date == published_year).all()
    if year_model is not None:
        return year_model
    
    raise HTTPException(status_code=404, detail='Books not found.')


@router.get("/books_pages_number", status_code=status.HTTP_200_OK)
async def read_books_by_number_of_pages(db: db_dependency,
                                        pages_number_min: int = Query(..., title='Pages number Minimum', gt=0),
                                        pages_number_max: int = Query(..., title='Pages number Maxmimum', gt=0)):
    pages_model = db.query(Books).filter(Books.page_number.between(pages_number_min, pages_number_max)).all()
    if pages_model is not None:
        return pages_model
    
    raise HTTPException(status_code=404, detail='Books not found.')


@router.get("/genre/pages_number", status_code=status.HTTP_200_OK)
async def read_books_by_genre_and_pages(db: db_dependency,
                                        genre_name : str = Query(...),
                                        pages_number_min: int = Query(..., title='Pages number Minimum', gt=0),
                                        pages_number_max: int = Query(..., title='Pages number Maxmimum', gt=0)):
    
    genre_pages_model = db.query(Books).join(Genre, Books.genre_id == Genre.id)\
    .filter(Genre.genre_name == genre_name, Books.page_number.between(pages_number_min, pages_number_max)).all()

    if genre_pages_model is not None:
        return genre_pages_model
    
    raise HTTPException(status_code=404, detail='Books not found.')


@router.get("/{book_id}", status_code=status.HTTP_200_OK)
async def read_book_by_id(db: db_dependency, book_id: int = Path(gt=0)):

    book_model = db.query(Books).filter(Books.id == book_id).first()
    if book_model is not None:
        return book_model
    
    raise HTTPException(status_code=404, detail='Book not found.')


@router.get("/author/{author_id}", status_code=status.HTTP_200_OK)
async def find_author_by_id(db: db_dependency, author_id: int = Path(gt=0)):

    author_model = db.query(Author).filter(Author.id == author_id).first()
    if author_model is not None:
        return author_model
    
    raise HTTPException(status_code=404, detail='Author not found.')


@router.get("/genre/{genre_id}", status_code=status.HTTP_200_OK)
async def find_genre_by_id(db: db_dependency, genre_id: int = Path(gt=0)):

    genre_model = db.query(Genre).filter(Genre.id == genre_id).first()
    if genre_model is not None:
        return genre_model
    
    raise HTTPException(status_code=404, detail='genre not found.')
