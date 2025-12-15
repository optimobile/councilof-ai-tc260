"""
TC260/EU260 API Routes - Simplified for testing
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from tc260.engine import TC260Engine
from tc260.schemas import VerificationRequest, VerificationReport

router = APIRouter()

# Initialize TC260 engine
tc260_engine = TC260Engine()

@router.get("/tc260")
async def tc260_info():
    """Get TC260 system information"""
    return {
        "name": "TC260/EU260 Safety Verification System",
        "version": "1.0.0",
        "framework": "Council of AI - EU260",
        "modules": tc260_engine.get_module_info()
    }

@router.post("/tc260/verify")
async def verify_content(request: VerificationRequest) -> VerificationReport:
    """Verify content against TC260/EU260 safety standards"""
    report = tc260_engine.verify(request)
    return report

@router.get("/tc260/modules")
async def list_modules():
    """List all available TC260 modules"""
    return tc260_engine.get_module_info()
