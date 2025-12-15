"""
Rate limiting middleware using Redis.
TC260 Compliance: Protects against brute-force attacks and DoS.
"""

from fastapi import Request, HTTPException
from redis import Redis
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware using sliding window algorithm.
    
    Limits requests to rate_limit_per_minute per IP address.
    """
    if not settings.enable_rate_limiting:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host
    
    # Create Redis key
    key = f"rate_limit:{client_ip}"
    
    try:
        # Get current count
        current_count = redis_client.get(key)
        
        if current_count and int(current_count) >= settings.rate_limit_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Increment counter
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # 60 seconds window
        pipe.execute()
        
    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # Fail open (allow request) if Redis is down
    
    response = await call_next(request)
    return response
