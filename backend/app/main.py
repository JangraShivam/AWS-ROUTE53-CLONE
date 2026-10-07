""" Import FastAPI's main application class"""
from fastapi import FastAPI

""" Import the SQLAlchemy Base and database engine"""
from app.database import Base, engine

""" Import models so SQLAlchemy knows about our database tables """
from app import models

"""
    Import our API routers.

    Each router contains endpoints related to a particular
    part of our application.
"""
from app.routers import hosted_zones
from app.routers import dns_records
from app.routers import auth


"""
    Create all database tables that don't already exist.

    Base.metadata contains information about all SQLAlchemy
    models that inherit from Base.

    engine tells SQLAlchemy which database to create the
    tables in.
"""
Base.metadata.create_all(bind=engine)


""" 
    Create the FastAPI application.
    'app' is the main object to which we attach our API routes.
"""
app = FastAPI()


""" 
    A simple test endpoint.
    GET /
    When someone visits the root URL of our backend,
    this function will be executed.
"""
@app.get("/")
def home():
    return {"message": "Hello World"}



""" 
    Register the routers with our main FastAPI application.

    This makes all endpoints defined inside these routers
    available through 'app'.
"""
app.include_router(hosted_zones.router)
app.include_router(dns_records.router)
app.include_router(auth.router)