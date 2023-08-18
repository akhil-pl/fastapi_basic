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
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()

# Path to add a new user
@router.post("/user/register", tags=["users"])
def register_user(username:str, password:str, db: Session = Depends(get_db)):
    '''Path to create a authorised user'''
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"Message": "User registered susssfully", "User": new_user}

# Path to get current user
@router.get("/users/me", tags=["users"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
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

        
    # Your token generation logic here
    # Continue with token generation logic
    # user_dict = fake_users_db.get(form_data.username)
    # candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    # if not user_dict:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    # user = UserInDB(**user_dict)
    # hashed_password = fake_hash_password(form_data.password)
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    # return {"access_token": user.username, "token_type": "bearer"}






# Path for Outh2autharisation
# @router.post("/token")
# def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
    
#     # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username},
#         # expires_delta=access_token_expires
#     )
    
#     return {"access_token": access_token, "token_type": "bearer"}