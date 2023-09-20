from enum import Enum
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
# from redis import Redis
from pydantic import BaseModel


from fastapi import APIRouter
from data.database import get_db_metadata
from jobs.send_email import sent_email

router = APIRouter()

# Path to get metadata
@router.get("/metadata", tags=["db metadata"])
async def metadata():
    '''Path to get details about the database schema'''
    Table = {}
    for table in get_db_metadata():
        table_info = {}  # Create a dictionary for table-specific metadata
        table_info['columns'] = {}  # Create a dictionary for column information

        # Populate the table-specific metadata
        table_info['name'] = table.name

        for column in table.c:
            column_info = {
                'type': str(column.type),
                'nullable': column.nullable,
                # 'default': column.default,
            }

            # Add column information to the table-specific metadata
            table_info['columns'][column.name] = column_info

        # Get primary keys for the table
        primary_keys = [key.name for key in table.primary_key]
        table_info['primary_keys'] = primary_keys

        # Get foreign keys for the table
        foreign_keys = []
        for column in table.columns:
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    foreign_keys.append({
                        'column': column.name,
                        'foreign_table': fk.column.table.name,
                        'foreign_column': fk.column.name
                    })
        table_info['foreign_keys'] = foreign_keys

        # Add table metadata to the 'Table' dictionary
        Table[table.name] = table_info

    return Table




# Path to email metadata
@router.get("/email_metadata/{to_email}", tags=["db metadata"])
async def email_metadata(to_email: str):
    '''Will sent the Metadata to the given email'''
    subject = "Database Metadata"
    content = str(get_db_metadata())
    send = sent_email(to_email=to_email, subject=subject, content=content)
    return send



class SupportedDatabases(str, Enum):
    mysql = "mysql"
    sqlite = "sqlite"
    postgres = "postgres"
    redis = "redis"
    mongodb = "mongodb"

class Connection(BaseModel):
    string: str

database_engines = {}
Session = sessionmaker()

metadata = MetaData()

# Path to crawl metadata of any database
@router.post("/any_db_metadata/{db}", tags=["db metadata"])
async def any_db_metadata(db: SupportedDatabases, connection_string: Connection):
    '''
    To connect with a db and get metadata
    "string": "mysql+mysqlconnector://rfamro:@mysql-rfam-public.ebi.ac.uk:4497/Rfam"
    "string": "postgresql://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs"
    '''
    source_db_url = connection_string.string
    try:
        if db not in SupportedDatabases:
            return {"error": "Unsupported database type"}
        if db in ["mysql", "sqlite", "postgres"]:
            engine = create_engine(source_db_url)
            Session.configure(bind=engine)
            session = Session()
            metadata = MetaData()
            metadata.reflect(bind=engine)
            return str(metadata.tables.values())
            # return [table.__dict__ for table in metadata.tables.values()]
            # return [table.tometadata() for table in metadata.tables.values()]  # Convert to list of dictionaries
        elif db == "redis":
            # redis = Redis.from_url(source_db_url)
            # redis_key = "your_redis_key"  # Replace with a suitable key
            # redis.hmset(redis_key, data.dict())
            return {"message": "Redis not implemented yet"}
        elif db == "mongodb":
            # mongo_client = MongoClient(source_db_url)
            # mongo_db = mongo_client["your_mongodb_database"]  # Replace with your actual database name
            # mongo_collection = mongo_db["your_mongodb_collection"]  # Replace with your actual collection name
            # mongo_collection.insert_one(data.dict())
            return {"message": "Mongodb not implemented yet"}
    except Exception as e:
        return {"error": str(e)}


