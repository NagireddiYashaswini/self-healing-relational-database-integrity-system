import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.config import settings
from backend.app.database.connection import test_database_connection
from backend.app.database.system_tables import ensure_system_tables_exist
from backend.app.models.schemas import ApiResponse
from backend.app.api.database import router as database_router
from backend.app.api.scans import router as scans_router
from backend.app.api.issues import router as issues_router
from backend.app.api.repairs import router as repairs_router
from backend.app.api.dependencies import router as dependencies_router
from backend.app.api.transactions import router as transactions_router
from backend.app.api.recovery import router as recovery_router
from backend.app.api.audit import router as audit_router
from backend.app.api.rules import router as rules_router
from backend.app.api.ingestion import router as ingestion_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("self_healing_dbms")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Self-Healing Relational Database Integrity System backend...")
    status = test_database_connection()
    if status["connected"]:
        logger.info(f"Connected successfully to MySQL ({status['server_version']}) at {settings.DB_HOST}:{settings.DB_PORT}")
        logger.info(f"Target database '{settings.DB_NAME}' active with {status['table_count']} tables.")
        ensure_system_tables_exist()
    else:
        logger.warning(f"Database connection warning: {status['message']}")
    yield
    logger.info("Shutting down backend services.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Academic DBMS Group Project: Autonomous integrity violation detection, dependency analysis, transaction-safe self-healing, and audit traceability.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration - Explicitly trusted frontend origins only
origins = [
    origin for origin in [
        settings.FRONTEND_ORIGIN,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ] if origin
]
origins = list(dict.fromkeys(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & Root Check
@app.get("/api/health", response_model=ApiResponse[dict], tags=["System Health"])
def health_check():
    db_status = test_database_connection()
    return ApiResponse(
        success=db_status["connected"],
        message="System health check status",
        data={
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "database": db_status
        }
    )

# Include Routers under /api
app.include_router(database_router, prefix=settings.API_PREFIX)
app.include_router(scans_router, prefix=settings.API_PREFIX)
app.include_router(issues_router, prefix=settings.API_PREFIX)
app.include_router(repairs_router, prefix=settings.API_PREFIX)
app.include_router(dependencies_router, prefix=settings.API_PREFIX)
app.include_router(transactions_router, prefix=settings.API_PREFIX)
app.include_router(recovery_router, prefix=settings.API_PREFIX)
app.include_router(audit_router, prefix=settings.API_PREFIX)
app.include_router(rules_router, prefix=settings.API_PREFIX)
app.include_router(ingestion_router, prefix=settings.API_PREFIX)

# Standardized Error Handling
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            message=exc.detail if isinstance(exc.detail, str) else "HTTP request error",
            error=str(exc.detail)
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = "; ".join([f"{e.get('loc', '')}: {e.get('msg', '')}" for e in errors])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse(
            success=False,
            message=f"Request validation failed: {msg}",
            error=str(errors)
        ).model_dump()
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse(
            success=False,
            message=str(exc),
            error=str(exc)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse(
            success=False,
            message="Internal database engine error occurred. Check system logs.",
            error=str(exc) if settings.DEBUG else "Internal server error"
        ).model_dump()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
