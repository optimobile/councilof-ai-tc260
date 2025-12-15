"""
TC260 API Routes for FastAPI
Council of AI - Safety Verification Platform
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from tc260.engine import TC260Engine
from tc260.schemas import VerificationRequest, VerificationReport, TC260Config
from database import get_db
import models
import auth

# Initialize router
router = APIRouter(prefix="/api/v1/tc260", tags=["TC260 Verification"])

# Initialize TC260 engine (singleton)
tc260_engine = TC260Engine()


@router.get("/")
async def tc260_info():
    """Get TC260 system information"""
    module_info = tc260_engine.get_module_info()
    
    return {
        "name": "TC260 AI Safety Verification System",
        "version": "0.1.0",
        "status": "operational",
        "modules_loaded": len(module_info),
        "modules": module_info,
        "config": {
            "parallel_processing": tc260_engine.config.parallel_processing,
            "max_workers": tc260_engine.config.max_workers,
            "default_threshold": tc260_engine.config.default_threshold
        }
    }


@router.post("/verify", response_model=VerificationReport)
async def verify_content(
    request: VerificationRequest,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Verify AI-generated content against TC260 safety standards
    
    **Requires authentication**
    
    - **content**: The AI-generated content to verify
    - **categories**: Optional list of specific TC260 categories to test
    - **threshold**: Risk score threshold (default: 70.0)
    - **context**: Optional additional context
    
    Returns a comprehensive verification report with risk assessments.
    """
    try:
        report = tc260_engine.verify(request)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/verify/public", response_model=VerificationReport)
async def verify_content_public(request: VerificationRequest):
    """
    Public endpoint for TC260 verification (no authentication required)
    
    **Rate limited** - For testing purposes only
    
    - **content**: The AI-generated content to verify
    - **categories**: Optional list of specific TC260 categories to test
    - **threshold**: Risk score threshold (default: 70.0)
    
    Returns a comprehensive verification report.
    """
    try:
        report = tc260_engine.verify(request)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/categories")
async def list_categories():
    """List all available TC260 risk categories"""
    module_info = tc260_engine.get_module_info()
    
    categories = [
        {
            "id": info["category_id"],
            "name": info["category_name"],
            "threshold": info["threshold"],
            "enabled": True
        }
        for cat_id, info in module_info.items()
    ]
    
    return {
        "total": len(categories),
        "categories": categories
    }


@router.get("/categories/{category_id}")
async def get_category_info(category_id: str):
    """Get detailed information about a specific TC260 category"""
    module_info = tc260_engine.get_module_info()
    
    if category_id not in module_info:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    
    info = module_info[category_id]
    
    # Get module instance for additional details
    module = tc260_engine.modules.get(category_id)
    
    return {
        "category_id": info["category_id"],
        "category_name": info["category_name"],
        "threshold": info["threshold"],
        "description": f"Detects risks related to {info['category_name'].lower()}",
        "enabled": True,
        "module_class": module.__class__.__name__ if module else None
    }


@router.post("/verify/batch", response_model=List[VerificationReport])
async def verify_batch(
    requests: List[VerificationRequest],
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Verify multiple pieces of content in batch
    
    **Requires authentication**
    
    Maximum 10 items per batch.
    """
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 items per batch")
    
    try:
        reports = [tc260_engine.verify(req) for req in requests]
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch verification failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for TC260 system"""
    try:
        # Test verification with simple content
        test_request = VerificationRequest(content="Test content")
        report = tc260_engine.verify(test_request)
        
        return {
            "status": "healthy",
            "modules_operational": len(tc260_engine.modules),
            "last_test_time_ms": report.processing_time_ms
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
