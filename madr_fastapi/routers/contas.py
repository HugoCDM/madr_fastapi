from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import User
from madr_fastapi.schemas import Message, UserPublic, UserSchema
from madr_fastapi.security import get_current_user, get_password_hash

router = APIRouter(prefix='/conta', tags=['contas'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_account(session: Session, user: UserSchema):

    user_db = await session.scalar(
        select(User).where(
            (user.email.lower() == User.email)
            | (user.username.lower() == User.username)
        )
    )

    if user_db:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exist',
        )

    user_db = User(
        username=user.username.lower(),
        email=user.email.lower(),
        password=get_password_hash(user.password),
    )

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    return user_db


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int, user: UserSchema, session: Session, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You are not allowed to change this user',
        )

    try:
        current_user.username = user.username.strip().lower()
        current_user.email = user.email.strip().lower()
        current_user.password = get_password_hash(user.password)
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_user(
    user_id: int, session: Session, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You are not allowed to delete this user',
        )
    await session.delete(current_user)
    await session.commit()
    return {'message': 'Account deleted successfully'}
