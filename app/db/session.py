from typing import Annotated
from fastapi import Depends
from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db.database import engine

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]