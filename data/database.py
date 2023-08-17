from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Create an MySQL database engine
connection_string = "mysql+mysqlconnector://user:@localhost:3306/employee_database"
engine = create_engine(connection_string, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Function to be used in ascess db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()