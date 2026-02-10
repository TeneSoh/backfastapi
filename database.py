from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

sessionlocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

base = declarative_base()
