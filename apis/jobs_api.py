from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
import logging
from data.database import get_db
from data.model import Candidate
from data.data_access import flush_all
from jobs.tasks import candidate_csv

router = APIRouter()


# Path to clear all caching
@router.get("/clear-cache/", tags=["jobs"])
async def clear_cache():
    '''Path to clear all cached data'''
    result = flush_all()
    return {"Message" : result}


# Path to start candidate.csv download
@router.get("/jobs/candidates/", tags=["jobs"])
async def create_csv(db: Session = Depends(get_db)):
    '''Trying to implement celery jobs, not working properly'''
    candidate_csv(db)

