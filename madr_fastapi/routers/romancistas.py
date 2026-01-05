from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import Novelist, User
from madr_fastapi.schemas import (
    Message,
    NovelistFilterPage,
    NovelistList,
    NovelistPublic,
    NovelistSchema,
)
from madr_fastapi.security import get_current_user

router = APIRouter(
    prefix='/romancista',
    tags=['romancistas'],
    dependencies=[Depends(get_current_user)],
)
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=NovelistPublic
)
async def create_novelist(
    session: Session,
    current_user: CurrentUser,
    novelist_schema: NovelistSchema,
):
    novelist_db = await session.scalar(
        select(Novelist).where(
            Novelist.name == novelist_schema.name.strip().lower()
        )
    )
    if novelist_db:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Novelist already exists'
        )

    novelist_db = Novelist(name=novelist_schema.name.strip().lower())
    session.add(novelist_db)
    await session.commit()
    await session.refresh(novelist_db)

    return novelist_db


@router.delete(
    '/{novelist_id}', status_code=HTTPStatus.OK, response_model=Message
)
async def delete_novelist(
    novelist_id: int,
    session: Session,
    current_user: CurrentUser,
):
    # deletar o romancista pelo id:
    novelist_db = await session.scalar(
        select(Novelist).where(novelist_id == Novelist.id)
    )
    if not novelist_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Novelist id not found'
        )

    await session.delete(novelist_db)
    await session.commit()

    return {'message': 'Novelist deleted in the MADR'}


@router.patch(
    '/{novelist_id}', status_code=HTTPStatus.OK, response_model=NovelistPublic
)
async def update_novelist(
    novelist_id: int,
    session: Session,
    current_user: CurrentUser,
    novelist: NovelistSchema,
):
    novelist_db = await session.scalar(
        select(Novelist).where(novelist_id == Novelist.id)
    )
    if not novelist_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Novelist id not found'
        )

    try:
        novelist_db.name = novelist.name.strip().lower()
        session.add(novelist_db)
        await session.commit()
        await session.refresh(novelist_db)

        return novelist_db

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Novelist already exists',
        )


@router.get(
    '/{novelist_id}', status_code=HTTPStatus.OK, response_model=NovelistPublic
)
async def get_novelist_by_id(
    novelist_id: int, session: Session, current_user: CurrentUser
):
    novelist_db = await session.scalar(
        select(Novelist).where(novelist_id == Novelist.id)
    )
    if not novelist_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Novelist id not found'
        )

    return novelist_db


@router.get('/', status_code=HTTPStatus.OK, response_model=NovelistList)
async def get_novelists_by_parameters(
    session: Session,
    novelist_filter: Annotated[NovelistFilterPage, Query()],
    current_user: CurrentUser,
):
    query = select(Novelist)
    if novelist_filter.name:
        query = query.filter(Novelist.name.contains(novelist_filter.name))

    novelists = await session.scalars(
        query.offset(novelist_filter.offset).limit(novelist_filter.limit)
    )

    return {'novelists': novelists.all()}
