from fastapi import FastAPI, Depends
# from fastapi.middleware.cors import CORSMiddleware
from data.database import engine
from data.model import Base
from apis import candidate, circuitbreaker, employee, department, user, jobs_api
from meta.metadata import description, tags_metadata, contact
from fastapi.security import OAuth2PasswordBearer
from log.logs import configure_logging, error_middleware



app = FastAPI(
    title="Database API",
    description=description,
    summary="EMPLOYEE DATABASE",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact=contact,
    openapi_tags=tags_metadata,
)

# Configure logging
configure_logging()

# Apply the error middleware globally, Not working
app.middleware("http")(error_middleware)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Create the database tables if they don't already exist
Base.metadata.create_all(bind=engine, checkfirst=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
def show_root():
    return {"Hello": "Go to 'url/docs' to view API end points"}

# Different API paths
app.include_router(user.router)
app.include_router(candidate.router)
app.include_router(employee.router)
app.include_router(department.router)
app.include_router(jobs_api.router)
app.include_router(circuitbreaker.router)