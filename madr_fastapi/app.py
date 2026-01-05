import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from madr_fastapi.routers import auth, contas, livros, romancistas
from madr_fastapi.schemas import Message

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
app.include_router(auth.router)
app.include_router(contas.router)
app.include_router(livros.router)
app.include_router(romancistas.router)

app.add_middleware(CORSMiddleware, allow_origins=['localhost:5432'])


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def main():
    return {'message': 'Seja bem-vindo(a) ao Meu Acervo Digital de Romances'}
