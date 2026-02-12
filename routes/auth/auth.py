import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta

from services.service import *
from models.models import User


route = APIRouter(prefix='/auth', tags=['auth'])

bcrypt_context = CryptContext(['argon2'], deprecated='auto')

class UserModel(BaseModel):
    nom:str
    prenom :str
    email :str
    phone :str
    pays :str
    password :str

class LoginModel(BaseModel):
    email:str
    password:str

secrete_key = secrets.token_urlsafe(64)

def authenticate(db:db_dependency , email:str, password:str):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="L'utilisateur n'existe pas")
    if not bcrypt_context.verify(password, str(user.password)):
        return False
    
    return user

def create_access_token(nom:str, id:int, expired_minute:int):
    paylod = {'sub':nom, "id":id, "scope":"access_token"}
    expired_time = datetime.now(timezone.utc) + timedelta(minutes=expired_minute)
    paylod.update({"exp":expired_time})

    access_token = jwt.encode(
        claims=paylod, key=secrete_key, algorithm='HS256'
    )

    return access_token


def create_refresh_token(nom:str, id:int, expired_date:int= 7):
    paylod = {'sub':nom, "id":id, "scope":"access_token"}
    expired_time = datetime.now(timezone.utc) + timedelta(days=expired_date)
    paylod.update({"exp":expired_time})

    access_token = jwt.encode(
        claims=paylod, key=secrete_key, algorithm='HS256'
    )

    return access_token


@route.post('/store-user', status_code=status.HTTP_201_CREATED)
async def storeUser(db:db_dependency, data:UserModel):
    user = User(
        nom = data.nom,
        prenom = data.prenom,
        email = data.email,
        phone = data.phone,
        pays = data.pays,
        password = bcrypt_context.hash(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@route.post('/login-user', status_code=status.HTTP_202_ACCEPTED)
async def login(db:db_dependency, data:LoginModel):
    user = authenticate(db, data.email, data.password)

    if isinstance(user, bool):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email ou mot de passe incorrect")
    
    access_token = create_access_token(str(user.nom), int(user.id), 30) # type: ignore
    refresh_token = create_refresh_token(user.nom, user.id, 7) # type: ignore

    return {
        'user':user,
        'access_token':access_token,
        'refresh_token':refresh_token
    }