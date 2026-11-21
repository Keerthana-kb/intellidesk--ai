
from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.api.v1.endpoints import auth, tickets, audit_logs


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered IT Service Desk",
    version=settings.APP_VERSION
)


# Register Authentication APIs
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)


# Register Ticket Management APIs
app.include_router(
    tickets.router,
    prefix=f"{settings.API_V1_PREFIX}/tickets",
    tags=["Tickets"]
)

# Register Audit Logs APIs
app.include_router(
    audit_logs.router,
    prefix=f"{settings.API_V1_PREFIX}/audit-logs",
    tags=["Audit Logs"]
)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to IntelliDesk AI",
        "status": "Application running successfully"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Database connection check
@app.get("/db-check")
def database_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database()")
            )

            database_name = result.scalar_one()

        return {
            "status": "connected",
            "database": database_name
        }

    except Exception:
        return {
            "status": "error",
            "message": "Database connection failed"
        }
