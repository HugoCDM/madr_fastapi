from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import User
from madr_fastapi.schemas import Token
from madr_fastapi.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])
Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
async def login(session: Session, form_data: OAuth2Form):
    user = await session.scalar(
        select(User).where(form_data.username == User.email)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='User or credentials invalid',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='User or credentials invalid',
        )

    token = create_access_token(data={'sub': user.email})

    return {'access_token': token, 'token_type': 'bearer'}


# @router.post('/refresh_token', response_model=Token)
# async def refresh_access_token(
#     session: Session,
#     current_user:
# ):
#     pass
