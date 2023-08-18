from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from data.database import SessionLocal, get_db
from data.model import Department
from pydantic import BaseModel

router = APIRouter()

class DepartmentCreate(BaseModel):
    name: str

# Path to add new department
@router.post("/departments/", tags=["departments"])
def create_department(department_data: DepartmentCreate, db: Session = Depends(get_db)):
    '''Path to add a new department'''
    department = Department(**department_data.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


# Path to get department name with Id
@router.get("/departments/{department_id}", tags=["departments"])
async def get_department(department_id: int, db: Session = Depends(get_db)):
    '''Get department using id'''
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


# Path to get all departments list
@router.get("/departments/", tags=["departments"])
async def get_all_departments(limit:int | None = None, db: Session = Depends(get_db)):
    '''Path to get all the departments'''
    if limit == None:
        departments = db.query(Department).all()
    else:
        departments = db.query(Department).limit(limit).all()
    return departments


# Path to delete a department
@router.delete("/departments/{department_id}", tags=["departments"])
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    '''Path to delete a department. This will inturn delete all the employee associated with that department'''
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    db.delete(department)
    db.commit()
    return {"message": "Department deleted"}