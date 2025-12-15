"""
Blockchain log model for immutable verification records.
TC260 Compliance: Tamper-proof audit trail via ProofOf.AI blockchain.
"""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import uuid


class BlockchainLog(Base):
    """Blockchain verification log model for immutable audit trail."""
    
    __tablename__ = "blockchain_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to verification
    verification_id = Column(String(50), ForeignKey("verifications.id"), nullable=False, index=True)
    
    # Blockchain Information
    tx_hash = Column(String(255), unique=True, nullable=False, index=True, comment="Blockchain transaction hash")
    certificate_url = Column(Text, nullable=False, comment="ProofOf.AI certificate URL")
    report_hash = Column(String(255), nullable=False, comment="SHA-256 hash of verification report")
    
    # Timestamp
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    verification = relationship("Verification", back_populates="blockchain_logs")
    
    def __repr__(self):
        return f"<BlockchainLog(verification_id={self.verification_id}, tx_hash={self.tx_hash})>"
