import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer

from services.service import *
from models.models import User


route = APIRouter(prefix='/auth', tags=['auth'])

bcrypt_context = CryptContext(['argon2'], deprecated='auto')

oauth_bearer = OAuth2PasswordBearer('auth/login') 

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

class RefreshTokenModel(BaseModel):
    refresh_token:str

secrete_key = secrets.token_urlsafe(64)

def authenticate(db:db_dependency , email:str, password:str):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="L'utilisateur n'existe pas")
    if not bcrypt_context.verify(password, str(user.password)):
        return False
    
    return user

def create_access_token(nom:str, id:int, expired_minute:int=30):
    payload = {'sub':nom, "id":id, "scope":"access_token"}
    expired_time = datetime.now(timezone.utc) + timedelta(minutes=expired_minute)
    payload.update({"exp":expired_time})

    access_token = jwt.encode(
        claims=payload, key=secrete_key, algorithm='HS256'
    )

    return access_token



def create_refresh_token(nom:str, id:int, expired_date:int= 7):
    payload = {'sub':nom, "id":id, "scope":"refresh_token"}
    expired_time = datetime.now(timezone.utc) + timedelta(days=expired_date)
    payload.update({"exp":expired_time})

    refresh_token = jwt.encode(
        claims=payload, key=secrete_key, algorithm='HS256'
    )

    return refresh_token

@route.post('/get-token', status_code=status.HTTP_200_OK)
async def get_token(db:db_dependency, data: RefreshTokenModel):
    try:
        payload = jwt.decode(
            token = data.refresh_token,
            key = secrete_key,
            algorithms = 'HS256',
        )
        if payload['scope'] == 'refresh_token':
            nom = payload['sub']
            id = payload['id']
            user = db.query(User).filter(User.id == id).first()
            if not user :
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='l\'utilisateur n\'existe pas')
            access_token = create_access_token(nom, id)

            return {
                'nom':nom,
                "access_token":access_token
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Database error")
    

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

def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(
            token = token,
            key = secrete_key,
            algorithms = 'HS256',
        )

        if not payload['scope'] == 'access_token':
            raise HTTPException(status_code=401, detail='wrong access token')
        
        nom = payload['sub']
        id = payload['id']
 
        if not nom and not id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='wrong user')
        
        return {
            'nom': nom,
            'id': id
        }

    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token a expirer')
    except JWTError as jwterror:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token invalide')
    