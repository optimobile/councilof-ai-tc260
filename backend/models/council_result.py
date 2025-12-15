"""
Council result model for storing individual AI council test results.
TC260 Compliance: Detailed tracking of each safety test.
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import uuid


class CouncilResult(Base):
    """Individual AI council test result model."""
    
    __tablename__ = "council_results"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to verification
    verification_id = Column(String(50), ForeignKey("verifications.id"), nullable=False, index=True)
    
    # Council Information
    council_name = Column(String(255), nullable=False)
    risk_category = Column(String(255), nullable=False, index=True)
    
    # Results
    vote = Column(String(50), nullable=False)  # PASS, WARNING, FAIL
    score = Column(Integer)  # 0-100
    test_count = Column(Integer)
    
    # Detailed Findings (JSON array)
    findings = Column(JSONB)
    
    # Summary
    summary = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    verification = relationship("Verification", back_populates="council_results")
    
    def __repr__(self):
        return f"<CouncilResult(council={self.council_name}, vote={self.vote}, score={self.score})>"
