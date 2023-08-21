from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from data.database import get_db
from data.model import User
from auth.functions import (hash_password, 
                            authenticate_user, 
                            create_access_token, 
                            get_current_active_user, 
                            Token
                            )
from auth.authentication import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
import zxcvbn



router = APIRouter()

# Path to add a new user
@router.post("/user/register", tags=["users"])
def register_user(username:str, password:str, db: Session = Depends(get_db)):
    '''Path to create a authorised user'''
    # Check password strength
    password_strength = zxcvbn.zxcvbn(password)
    score = password_strength['score']
    suggestions = password_strength['feedback']['suggestions']
    if score < 3:
        raise HTTPException(
            status_code=400,
            detail="Score: "+str(score)+" Weak password. Consider choosing a stronger password. "+", ".join(suggestions),
            headers={"Passord-Suggestions": ", ".join(suggestions)}
        )
    
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "Message": "User registered successfully",
        "User": new_user,
        "Suggestions": suggestions
    }

# Path to get current user
@router.get("/users/me", tags=["users"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    '''Path to get current active user'''
    return current_user


@router.post("/token", response_model=Token, tags=["users"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    '''Path to get Auth Token'''
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

