"""
Verification model for AI system verification requests and results.
TC260 Compliance: Comprehensive audit trail and status tracking.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Verification(Base):
    """AI system verification model with full audit trail."""
    
    __tablename__ = "verifications"
    
    # Primary key
    id = Column(String(50), primary_key=True)  # e.g., "ver_abc123"
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # AI System Information
    ai_name = Column(String(255), nullable=False)
    ai_type = Column(String(100))  # text_generation, image_generation, etc.
    ai_endpoint = Column(Text, nullable=False)
    documentation_url = Column(Text)
    
    # Verification Configuration
    tier = Column(String(50), nullable=False)  # bronze, silver, gold, platinum
    
    # Status and Results
    status = Column(String(50), default="processing", nullable=False, index=True)  # processing, completed, failed
    verdict = Column(String(50))  # PASS, WARNING, FAIL
    safety_score = Column(Integer)  # 0-100
    
    # Output URLs
    report_url = Column(Text)
    certificate_url = Column(Text)
    badge_url = Column(Text)
    
    # Webhook
    webhook_url = Column(Text)
    
    # Metadata (flexible JSON field)
    metadata = Column(JSONB)
    
    # Timestamps (full audit trail)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="verifications")
    council_results = relationship("CouncilResult", back_populates="verification", cascade="all, delete-orphan")
    blockchain_logs = relationship("BlockchainLog", back_populates="verification", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Verification(id={self.id}, ai_name={self.ai_name}, status={self.status}, verdict={self.verdict})>"
