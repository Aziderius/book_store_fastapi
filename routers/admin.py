from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import Users, Own_library, Genre, Books, Author
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func, select
from sqlalchemy import join
from starlette import status
from .auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class NewBookRequest(BaseModel):
    title: str = Field(min_length=2)
    author_id: int = Field(gt=0)
    genre_id: int = Field(gt=0)
    published_date: int = Field(gt=0)
    page_number: int = Field(gt=0)
    price: float = Field(gt=0)
    rating: int = Field(gt=0, lt=6)
    synopsis: str = Field(min_length=2)


class NewAuthorRequest(BaseModel):
    author_name: str = Field(min_length=2)


class NewGenreRequest(BaseModel):
    genre_name: str = Field(min_length=2)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_users(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    return db.query(Users).all()


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404, detail='User not found')
    

@router.get("/libraries", status_code=status.HTTP_200_OK)
async def get_all_libraries(user:user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    return db.query(Own_library).all()


@router.get("/library/{library_id}", status_code=status.HTTP_200_OK)
async def get_library_by_owner_id(user: user_dependency, db: db_dependency, library_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    library_model = db.query(Own_library).filter(Own_library.owner_id == library_id).all()
    if library_model is not None:
        return library_model
    
    raise HTTPException(status_code=404, detail='User not found')


@router.post("/add_genre", status_code=status.HTTP_201_CREATED)
async def create_genre(user: user_dependency, db: db_dependency, genre_request: NewGenreRequest):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    genre_model = Author(**genre_request.model_dump())

    db.add(genre_model)
    db.commit()


@router.post("/add_author", status_code=status.HTTP_201_CREATED)
async def create_author(user: user_dependency, db: db_dependency, author_request: NewAuthorRequest):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    author_model = Author(**author_request.model_dump())

    db.add(author_model)
    db.commit()


@router.post("/add_book", status_code=status.HTTP_201_CREATED)
async def create_book(user: user_dependency, db: db_dependency, book_request: NewBookRequest):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    book_model = Books(**book_request.model_dump())

    db.add(book_model)
    db.commit()


@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_model = db.query(Users).filter(Users.id == user_id).first()
    user_library_model = db.query(Own_library).filter(Own_library.owner_id == user_id).all()

    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    for entry in user_library_model:
        db.delete(entry)

    db.delete(user_model)
    db.commit()


@router.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(user: user_dependency, db: db_dependency, book_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    book_model = db.query(Books).filter(Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404, detail='Book not found')
    
    db.query(Books).filter(Books.id == book_id).delete()
    db.commit()

