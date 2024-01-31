from database import Base
from sqlalchemy import Column, Integer, Float, String, ForeignKey


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String, default='user')


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String, unique=True)


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True, index=True)
    genre_name = Column(String, unique=True)


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    author_id = Column(Integer, ForeignKey("author.id"))
    genre_id = Column(Integer, ForeignKey("genre.id"))
    published_date = Column(Integer)
    page_number = Column(Integer)
    price = Column(Float)
    rating = Column(Integer)
    synopsis = Column(String)

