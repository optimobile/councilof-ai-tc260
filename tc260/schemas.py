"""
TC260 Pydantic Schemas for Risk Assessment
Council of AI - Safety Verification Platform
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class VerificationStatus(str, Enum):
    """Overall verification status"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


class RiskFinding(BaseModel):
    """Individual risk finding within a category"""
    description: str
    severity: RiskLevel
    location: Optional[str] = None  # Where in the input this was found
    evidence: Optional[str] = None  # Supporting evidence
    confidence: float = Field(ge=0.0, le=1.0)


class RiskAssessment(BaseModel):
    """Risk assessment result for a single TC260 category"""
    category_id: str = Field(..., description="TC260 category identifier (e.g., TC260-01)")
    category_name: str = Field(..., description="Human-readable category name")
    risk_score: float = Field(ge=0.0, le=100.0, description="Risk score from 0 (safe) to 100 (critical)")
    severity: RiskLevel
    passed: bool = Field(..., description="True if risk is within acceptable threshold")
    findings: List[RiskFinding] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence in this assessment")
    processing_time_ms: int = Field(ge=0, description="Time taken to process this category")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VerificationRequest(BaseModel):
    """Request to verify AI output against TC260 standards"""
    content: str = Field(..., description="AI-generated content to verify")
    categories: Optional[List[str]] = Field(
        default=None, 
        description="Specific TC260 categories to test (None = all)"
    )
    threshold: float = Field(
        default=70.0, 
        ge=0.0, 
        le=100.0,
        description="Risk score threshold (scores above this fail)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for verification"
    )


class VerificationReport(BaseModel):
    """Complete verification report across all tested categories"""
    request_id: str
    overall_score: float = Field(ge=0.0, le=100.0, description="Weighted average risk score")
    overall_status: VerificationStatus
    categories_tested: int
    categories_passed: int
    categories_failed: int
    categories_warning: int
    risk_assessments: List[RiskAssessment]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "ver_abc123",
                "overall_score": 35.5,
                "overall_status": "PASS",
                "categories_tested": 5,
                "categories_passed": 4,
                "categories_failed": 1,
                "categories_warning": 0,
                "risk_assessments": [],
                "timestamp": "2025-12-14T17:30:00Z",
                "processing_time_ms": 1250
            }
        }


class TC260Config(BaseModel):
    """Configuration for TC260 verification engine"""
    enabled_categories: List[str] = Field(
        default_factory=lambda: [f"TC260-{i:02d}" for i in range(1, 33)]
    )
    default_threshold: float = 70.0
    parallel_processing: bool = True
    max_workers: int = 8
    timeout_seconds: int = 30
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
