from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session, selectinload
from data.database import get_db
from data.model import Employee, Candidate, Department, User
from data.data_access import (employee_cache,
                              all_employees_cache,
                              invalidate_employee_cache,
                              invalidate_all_employees_cache)
from auth.functions import get_current_active_user
from datetime import datetime

router = APIRouter()

# Define today's date
current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# path to add a new employee,  implemented SCD type 2 for getting the emjployee promotion history
@router.post("/employees/", tags=["employees"])
async def create_employee(
    cid: int = Query(..., description="Candidate ID"),
    designation: str = Query(..., description="Employee's designation"),
    did: int = Query(..., description="Department ID"),
    start: str = Query(current_date, description="Start date"),
    end: str = Query("9999-12-31", description="End date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    '''Add new employee'''
    # First Check if the candidate or department exists
    candidate = db.query(Candidate).filter(Candidate.id == cid).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    department = db.query(Department).filter(Department.id == did).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    

    # Check if the candidate already exists as an employee
    existing_employee = db.query(Employee).filter(Employee.cid == cid).filter(Employee.end == "9999-12-31").first()

    if existing_employee:
        # Update the end date of the existing entry
        existing_employee.end = datetime.now()
        db.commit()

    # Create a new employee entry
    new_employee = Employee(
        cid=cid,
        designation=designation,
        did=did,
        start=start,
        end=end
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    invalidate_all_employees_cache()
    return new_employee



# Path to get details of a employee
@router.get("/employees/{employee_id}", tags=["employees"])
@employee_cache(ttl=600)
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    '''Get details of a employee including personal details and department details'''
    employee = (
        db.query(Employee)
        .options(selectinload(Employee.candidate), selectinload(Employee.department))
        .filter(Employee.id == employee_id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee_data = {
        "id": employee.id,
        "designation": employee.designation,
        "start": employee.start,
        "end": employee.end,
        "candidate": {
            "id": employee.candidate.id,
            "name": employee.candidate.name,
            "dob": employee.candidate.dob,
            "sex": employee.candidate.sex,
            "skills": employee.candidate.skills,
        },
        "department": employee.department.as_dict(),
    }
    return employee_data




# Path to get all employees
@router.get("/employees/", tags=["employees"])
@all_employees_cache() # Cached without time limit
async def get_all_employees(db: Session = Depends(get_db)):
    '''Get list of all employee'''
    employees = db.query(Employee).all()
    return employees




# Path to edit an employee
@router.put("/employees/{employee_id}", tags=["employees"])
async def update_employee(
    employees_id: int = Path(..., description="Employee ID"),
    designation: str = Query(None, description="Employee's designation"),
    did: int = Query(None, description="Department ID"),
    start: str = Query(None, description="Start date"),
    end: str = Query(None, description="End date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    '''To update an existing employee'''
    employee = db.query(Employee).filter(Employee.id == employees_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if designation is not None:
        employee.designation = designation
    if did is not None:
        employee.did = did
    if start is not None:
        employee.start = start
    if end is not None:
        employee.end = end

    db.commit()
    db.refresh(employee)
    invalidate_all_employees_cache()
    invalidate_employee_cache(employees_id)
    return employee




# Path to delete a user
@router.delete("/employees/{employee_id}", tags=["employees"])
async def delete_employee(
        employee_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    '''To delete an existing employee'''
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()
    invalidate_all_employees_cache()
    invalidate_employee_cache(employee_id)
    return {"message": "Employee deleted"}