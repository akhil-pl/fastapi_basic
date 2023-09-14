from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import logging

Base = declarative_base()

logger = logging.getLogger(__name__)

# Create an MySQL database engine
connection_string = "mysql+mysqlconnector://user:@localhost:3306/employee_database"
engine = create_engine(connection_string, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# Function to be used in ascess db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


metadata = MetaData()

metadata.reflect(bind=engine)

def get_db_metadata():
    return metadata.tables.values()

# # List all tables in the database
# for table in metadata.tables.values():
#     print(f"Table Name: {table.name}")
#     for column in table.c:
#         print(f"Column Name: {column.name}, Type: {column.type}")