from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal


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


db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
async def get_the_user():
    return {'user': 'authenticated'}