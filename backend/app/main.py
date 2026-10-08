""" Import FastAPI's main application class"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


def ensure_sqlite_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as connection:
        hosted_zone_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(hosted_zones)")
        }

        if "type" not in hosted_zone_columns:
            connection.exec_driver_sql(
                "ALTER TABLE hosted_zones "
                "ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'Public'"
            )

        if "description" not in hosted_zone_columns:
            connection.exec_driver_sql(
                "ALTER TABLE hosted_zones ADD COLUMN description TEXT"
            )

        dns_record_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(dns_records)")
        }

        if "routing_policy" not in dns_record_columns:
            connection.exec_driver_sql(
                "ALTER TABLE dns_records "
                "ADD COLUMN routing_policy VARCHAR(50) "
                "NOT NULL DEFAULT 'Simple routing'"
            )


ensure_sqlite_schema()


""" 
    Create the FastAPI application.
    'app' is the main object to which we attach our API routes.
"""
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://aws-route-53-clone-ten.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(
    hosted_zones.router,
    prefix="/api/v1"
)

app.include_router(
    dns_records.router,
    prefix="/api/v1"
)

app.include_router(
    auth.router,
    prefix="/api/v1"
)
