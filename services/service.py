from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, Path

from database import engine
from database import sessionlocal
from models.models import base

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally :
        db.close()

base.metadata.create_all(bind=engine)
db_dependency = Annotated[Session, Depends(get_db)] 
