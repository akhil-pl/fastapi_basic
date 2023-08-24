from jobs.workers import celery
from data.database import get_db
from data.model import Candidate, Employee, Department
from sqlalchemy.orm import Session
from fastapi import Depends


import csv
import os
current_dir = os.path.abspath(os.path.dirname(__file__))

@celery.task()
def candidate_csv(db: Session = Depends(get_db)):
    header = ['ID', 'Name', 'DOB', 'Sex', 'Skills']
    data = []
    candidates = db.query(Candidate).all()
    for c in candidates:
        id = c.id
        name = c.name
        dob = c.dob
        sex = c.sex
        skills = c.skills
        data.append([id, name, dob, sex, skills])
    file_name = "candidate.csv"
    dirname = os.path.join(current_dir, "../files")
    if os.path.exists(dirname):
        with open(os.path.join(dirname, file_name), 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
    
