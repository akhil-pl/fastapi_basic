# Getting started with FastAPI
This is a sample app to get familier with FastAPI.

## Steps to follow
### You should have python3 and MySQL installed in your system
And create a database named 'employee_database'

- Setup and run virtual environment
``` bash
python3 -m venv .env
source .env/bin/activate
```
- Install requirements
``` bash
pip install fastapi
pip install 'uvicorn[standard]'
pip install mysql-connector-python
pip install SQLAlchemy
pip install "python-jose[cryptography]"
pip install "passlib[bcrypt]"
pip install python-multipart
```
Or run the following code, it will recursively install all the requirements
``` bash
pip install -r requirements.txt
```

Now run this code to start the server
``` bash
uvicorn main:app --reload
```
