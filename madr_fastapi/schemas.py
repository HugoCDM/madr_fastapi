from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UsersList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    token_type: str
    access_token: str


class BookSchema(BaseModel):
    year: int
    title: str
    novelist_id: int


class BookPublic(BaseModel):
    id: int
    year: int
    title: str
    novelist_id: int


class BookList(BaseModel):
    books: list[BookPublic]


class BookUpdate(BaseModel):
    title: str | None = None
    year: int | None = None
    novelist_id: int | None = None


class NovelistSchema(BaseModel):
    name: str


class NovelistPublic(NovelistSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


class NovelistList(BaseModel):
    novelists: list[NovelistPublic]


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=20)


class NovelistFilterPage(FilterPage):
    name: str | None = None


class BookFilterPage(FilterPage):
    title: str | None = None
    year: int | None = None
