from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from data.database import get_db
from data.model import Candidate, User
from data.data_access import (candidate_cache, 
                              all_candidates_cache, 
                              invalidate_candidate_cache, 
                              invalidate_all_candidates_cache)
from auth.functions import get_current_active_user

router = APIRouter()

# Path to create a new candidate
@router.post("/candidates/", tags=["candidates"])
async def create_candidate(
    name: str = Query(..., description="Candidate's name"),
    dob: str = Query(..., description="Date of birth"),
    skills: str = Query(..., description="Candidate's skills"),
    sex: str = Query(None, description="Candidate's sex"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Path to create a new candidate"""
    candidate_data = {
        "name": name,
        "dob": dob,
        "skills": skills,
        "sex": sex
    }
    candidate = Candidate(**candidate_data)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    invalidate_all_candidates_cache() # To delete cached all candidate
    return candidate




# Path to get a candidate details given id
@router.get("/candidates/{candidate_id}", tags=["candidates"])
@candidate_cache(ttl=600) #Cache for 10 minutes
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Path to get a candidate details given id"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate




# Path to get all candidates
@router.get("/candidates/", tags=["candidates"])
@all_candidates_cache()  # Cache for 10 minutes (adjust as needed)
async def get_all_candidates(pattern:str | None=None,
                             limit:int | None=None,
                              skip:int | None=None,
                              db: Session = Depends(get_db)):
    '''Path to get all candidates. Can match name with a pattern, limit the number of list or skip some initial results'''
    match = None
    if pattern:
        match = "%" + pattern + "%"  # Pattern wildcard match
        candidates = db.query(Candidate).filter(Candidate.name.like(match))
    else:
        candidates = db.query(Candidate)
    if skip is not None:
        candidates = candidates.offset(skip)
    if limit is not None:
        candidates = candidates.limit(limit)
    result = candidates.all()
    return result



# Path to get candidates with specific skills
@router.get("/candidates/with/{skill}", tags=["candidates"])
async def get_all_candidates(skill:str,
                             limit:int | None=None,
                              skip:int | None=None,
                              db: Session = Depends(get_db)):
    '''Path to get all candidates matching skills with a pattern, limit the number of list or skip some initial results'''
    match = "%" + skill + "%"  # Pattern wildcard match
    candidates = db.query(Candidate).filter(Candidate.skills.like(match))
    if skip is not None:
        candidates = candidates.offset(skip)
    if limit is not None:
        candidates = candidates.limit(limit)
    result = candidates.all()
    return result



# Path to edit an existing candidate
@router.put("/candidates/{candidate_id}", tags=["candidates"])
async def update_candidate(
    candidate_id: int = Path(..., description="Candidate ID"),
    name: str = Query(None, description="Candidate's name"),
    dob: str = Query(None, description="Date of birth"),
    skills: str = Query(None, description="Candidate's skills"),
    sex: str = Query(None, description="Candidate's sex"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    '''Edit details of an existing candidate. Only the parameters that changes needs to be added, rest will be the same'''
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if name is not None:
        candidate.name = name
    if dob is not None:
        candidate.dob = dob
    if skills is not None:
        candidate.skills = skills
    if sex is not None:
        candidate.sex = sex

    db.commit()
    db.refresh(candidate)
    invalidate_all_candidates_cache()
    invalidate_candidate_cache(candidate_id)
    return candidate




# Path to delete an user
@router.delete("/candidates/{candidate_id}", tags=["candidates"])
async def delete_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    '''Deleting an existing candidate'''
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()
    invalidate_all_candidates_cache()
    invalidate_candidate_cache(candidate_id)
    return {"message": "Candidate deleted"}