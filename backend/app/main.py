
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.api.v1.endpoints import auth, tickets, audit_logs, teams, dashboard
from contextlib import asynccontextmanager
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered IT Service Desk",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_PREFIX}/dashboard",
    tags=["Dashboard"]
)
app.include_router(
    teams.router,
    prefix=f"{settings.API_V1_PREFIX}/teams",
    tags=["Team Management"]
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
