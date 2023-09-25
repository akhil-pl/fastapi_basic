from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .authentication import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from data.model import User
from data.database import get_db

import pyotp
from jobs.send_email import sent_email

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email==email).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




# OTP functions
def send_otp(email:str, subject:str, db:Session, validity_period:int | None = None):
    # save it in cache instead of database
    totp_secret = pyotp.random_base32()
    user = db.query(User).filter(User.email==email).first()
    user.otp_key = totp_secret
    db.commit()
    db.refresh(user)
    if validity_period:
        totp = pyotp.TOTP(totp_secret, interval=validity_period)
    else:
        validity_period = 600
        totp = pyotp.TOTP(totp_secret, interval=validity_period)
    otp = totp.now()
    sent_email(to_email=email, subject=subject, content=otp)

def verify_otp(email:str, )

