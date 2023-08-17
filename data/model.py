from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))

class Person(Base):
    __abstract__ = True #Will not be added to table
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255))
    dob = Column(DateTime)
    sex = Column(String(255))


class Candidate(Person):
    __tablename__ = 'candidate'
    skills = Column(String(255))
    employee = relationship("Employee", backref="candidate", cascade="all, delete")# Cascading effect to delete all child relations
    
    
class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, autoincrement=True, primary_key=True)
    cid = Column(Integer, ForeignKey('candidate.id'))
    designation = Column(String(255))
    did = Column(Integer, ForeignKey('departments.id'))
    start = Column(DateTime)
    end = Column(DateTime)


class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255), unique=True)
    employees = relationship("Employee", backref="department", cascade="all, delete")
    # Function to return department object as a dictionary
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

