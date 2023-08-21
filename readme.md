# Getting started with FastAPI
This is a sample app to get familier with FastAPI.

## Steps to follow
### You should have python3, MySQL and redis installed in your system
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
pip install zxcvbn-python
pip install redis
```
Or run the following code, it will recursively install all the requirements
``` bash
pip install -r requirements.txt
```

After that create ```.env``` file inside auth folder and save the following values there
```.env
SECRET_KEY = $$Your_SeCRet_kEY$$
ALGORITHM = <Your hashing algorithn>
ACCESS_TOKEN_EXPIRE_MINUTES = time in intiger
```

Now run this code to start the server
``` bash
uvicorn main:app --reload
```
Now run this code to start the redis server for caching
``` bash
redis-server
```
