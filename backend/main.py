"""
Main FastAPI application entry point.
Configures middleware, routes, and application lifecycle.
TC260 Security Enhanced.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from middleware.rate_limiting import rate_limit_middleware
from middleware.audit_logging import audit_logging_middleware
from config import settings
import logging

# Configure structured JSON logging
logging.basicConfig(
    level=logging.INFO if settings.environment == "production" else logging.DEBUG,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
)

# Add CORS middleware (Strict by default)
if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    logger.info("CORS middleware enabled")

# Add trusted host middleware (Security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.environment == "development" else [
        "councilof.ai",
        "www.councilof.ai",
        "api.councilof.ai",
        "*.railway.app",
    ]
)
logger.info("Trusted host middleware enabled")

# Add security middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(audit_logging_middleware)
logger.info("Security middleware enabled (rate limiting, audit logging)")


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"TC260 Security: Enabled")
    logger.info(f"Rate limiting: {settings.enable_rate_limiting}")
    logger.info(f"Audit logging: {settings.enable_audit_logging}")
    logger.info(f"Blockchain logging: {settings.enable_blockchain_logging}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "environment": settings.environment,
        "security": "TC260 Compliant",
        "docs": "/docs" if settings.environment != "production" else "disabled",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.api_version,
        "security": "TC260 Compliant",
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"message": "pong"}


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 error handler."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 error handler."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
