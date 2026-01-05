from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, cast, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import Book, User
from madr_fastapi.schemas import (
    BookFilterPage,
    BookList,
    BookPublic,
    BookSchema,
    BookUpdate,
    Message,
)
from madr_fastapi.security import get_current_user

router = APIRouter(
    prefix='/livro', tags=['livros'], dependencies=[Depends(get_current_user)]
)
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=BookPublic)
async def add_book(
    session: Session, current_user: CurrentUser, book_schema: BookSchema
):
    book = await session.scalar(
        select(Book).where(book_schema.title.strip().lower() == Book.title)
    )
    if book:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Book already created'
        )

    try:
        book = Book(
            title=book_schema.title.strip().lower(),
            year=book_schema.year,
            novelist_id=book_schema.novelist_id,
        )

        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Novelist id is invalid',
        )


@router.patch(
    '/{book_id}', response_model=BookPublic, status_code=HTTPStatus.OK
)
async def update_book(
    book_id: int, session: Session, current_user: CurrentUser, book: BookUpdate
):
    book_db = await session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book id was not found'
        )

    if book.title:
        book_db.title = book.title.strip().lower()

    if book.year:
        book_db.year = book.year

    if book.novelist_id:
        book_db.novelist_id = book.novelist_id

    # for key, value in book.model_dump(exclude_unset=True).items():
    #     setattr(book_db, key, value)

    session.add(book_db)
    await session.commit()
    await session.refresh(book_db)

    return book_db


@router.delete('/{book_id}', response_model=Message, status_code=HTTPStatus.OK)
async def delete_book(
    book_id: int, session: Session, current_user: CurrentUser
):
    book_db = await session.scalar(select(Book).where(book_id == Book.id))
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book id was not found'
        )

    await session.delete(book_db)
    await session.commit()

    return {'message': 'Book deleted successfully'}


@router.get('/{book_id}', status_code=HTTPStatus.OK, response_model=BookPublic)
async def get_book_by_id(
    book_id: int, session: Session, current_user: CurrentUser
):
    book_db = await session.scalar(select(Book).where(book_id == Book.id))
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book id was not found'
        )
    return book_db


@router.get('/', status_code=HTTPStatus.OK, response_model=BookList)
async def get_book_by_parameters(
    session: Session,
    current_user: CurrentUser,
    books_filter: Annotated[BookFilterPage, Query()],
):
    query = select(Book)

    if books_filter.title and books_filter.title.strip().lower():
        query = query.filter(
            Book.title.contains(books_filter.title.strip().lower())
        )

    if books_filter.year:
        query = query.filter(
            cast(Book.year, String).contains(books_filter.year)
        )

    books = await session.scalars(
        query.limit(books_filter.limit).offset(books_filter.offset)
    )

    return {'books': books.all()}
