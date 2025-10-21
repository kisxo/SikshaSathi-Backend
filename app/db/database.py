from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
engine = create_engine(DATABASE_URL, echo=True)

# Base MetaData class, all ORM Table classes derives from this Base class.
# All derived class Metadata/Schema is attached to this class for Table creation.
class Base(DeclarativeBase):
    pass

# Function to create database tables
# Should only be called once during server start up
def create_db_and_tables():
    Base.metadata.create_all(engine)