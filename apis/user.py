from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from data.database import get_db
from data.model import User
from auth.functions import hash_password, authenticate_user, create_access_token, get_current_user
# from auth.authentication import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()

# Path to get current user
@router.get("/users/me", tags=["users"])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user




# Path to add a new user
@router.post("/user/register", tags=["users"])
def register_user(username:str, password:str, db: Session = Depends(get_db)):
    '''Path to create a authorised user'''
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hash_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"Message": "User registered susssfully", "User": new_user}


# Path for Outh2autharisation
@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        # expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}