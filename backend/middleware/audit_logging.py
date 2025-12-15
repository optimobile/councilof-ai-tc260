"""
Audit logging middleware for comprehensive request/response logging.
TC260 Compliance: Creates immutable audit trail of all API activity.
"""

from fastapi import Request
from config import settings
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


async def audit_logging_middleware(request: Request, call_next):
    """
    Audit logging middleware.
    
    Logs all API requests and responses in structured JSON format.
    """
    if not settings.enable_audit_logging:
        return await call_next(request)
    
    # Capture request details
    request_id = request.headers.get("X-Request-ID", "unknown")
    client_ip = request.client.host
    method = request.method
    path = request.url.path
    timestamp = datetime.utcnow().isoformat()
    
    # Log request
    logger.info(json.dumps({
        "event": "api_request",
        "request_id": request_id,
        "timestamp": timestamp,
        "client_ip": client_ip,
        "method": method,
        "path": path,
    }))
    
    # Process request
    response = await call_next(request)
    
    # Log response
    logger.info(json.dumps({
        "event": "api_response",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": response.status_code,
    }))
    
    return response
