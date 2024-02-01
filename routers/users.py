from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from .auth import get_current_user
from pydantic import BaseModel, Field
from models import Own_library, Books, Author
from starlette import status


router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UpdateBookRequest(BaseModel):
    personal_description: str | None = None
    personal_rating: int | None = None
    

class AddBookRequest(UpdateBookRequest):
    book_id: int = Field(gt=0)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/my_books/", status_code=status.HTTP_200_OK)
async def see_my_books(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    my_book_model = (
        db.query(Own_library, Books, Author)
        .join(Books, Own_library.book_id == Books.id)
        .join(Author, Books.author_id == Author.id)
        .filter(Own_library.owner_id == user.get('id'))
        .all()
    )

    results = []
    for own_library, book, author in my_book_model:
        results.append({
            "my_book_id": own_library.id,
            "book_id": book.id,
            "title": book.title,
            "author": author.author_name,
            "personal_description": own_library.personal_description,
            "personal_rating": own_library.personal_rating,
        })
        
    return results


@router.post("/add_book", status_code=status.HTTP_201_CREATED)
async def add_book_to_my_library(user: user_dependency, db: db_dependency, my_book_request: AddBookRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    my_book_model = Own_library(**my_book_request.model_dump(), owner_id=user.get('id'))

    db.add(my_book_model)
    db.commit()


@router.post("/my_books/{my_book_id}", status_code=status.HTTP_201_CREATED)
async def update_my_book(user: user_dependency,
                                      db: db_dependency,
                                      my_book_request: UpdateBookRequest,
                                      my_book_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    my_book_model = db.query(Own_library).filter(Own_library.id == my_book_id)\
    .filter(Own_library.owner_id == user.get('id')).first()

    if my_book_model is None:
        raise HTTPException(status_code=404, detail='Book not found')
    
    my_book_model.personal_description = my_book_request.personal_description
    my_book_model.personal_rating = my_book_request.personal_rating

    db.add(my_book_model)
    db.commit()


@router.delete("/my_books/{my_book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_book(user: user_dependency, db: db_dependency, my_book_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    my_book_model = db.query(Own_library).filter(Own_library.id == my_book_id)\
    .filter(Own_library.owner_id == user.get('id')).first()

    if my_book_model is None:
        raise HTTPException(status_code=404, detail='Book not found')
    db.query(Own_library).filter(Own_library.id == my_book_id).filter(Own_library.owner_id == user.get('id')).delete()

    db.commit()
