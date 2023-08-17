from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from data.database import SessionLocal, get_db
from data.model import User

router = APIRouter()

# Path to add a new user
@router.post("/user/")
def register_user(username:str, password:str, db: Session = Depends(get_db)):
    user = create_user(username, password, db)
    return {"Message": "User registered susssfully", "User": user}
