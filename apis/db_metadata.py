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
    '''Not yet configured for gmail'''
    subject = "Database Metadata"
    content = str(get_db_metadata())
    send = sent_email(to_email=to_email, subject=subject, content=content)
    return send
