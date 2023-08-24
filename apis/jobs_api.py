from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
import logging
from data.database import get_db
from jobs.tasks import candidate_csv

router = APIRouter()


# Path to start candidate.csv download
@router.get("/jobs/candidates/", tags=["jobs"])
async def create_csv(db: Session = Depends(get_db)):
    candidate_csv(db)

