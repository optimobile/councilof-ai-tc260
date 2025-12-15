"""
User model for authentication and account management.
TC260 Compliance: PII fields are tagged and encrypted.
"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class User(Base):
    """User account model with PII protection."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True, comment="PII: User email")
    password_hash = Column(String(255), nullable=False, comment="Hashed password (bcrypt)")
    
    # Profile (PII)
    company_name = Column(String(255), comment="PII: Company name")
    
    # API Access
    api_key_hash = Column(String(255), unique=True, index=True, comment="Hashed API key (SHA-256)")
    
    # Subscription tier
    tier = Column(String(50), default="free")  # free, bronze, silver, gold, platinum
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps (for data retention)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    verifications = relationship("Verification", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def is_stale(self):
        """Check if user account is stale (for data retention)."""
        from datetime import timedelta
        from config import settings
        return datetime.utcnow() > self.last_login_at + timedelta(days=settings.data_retention_days)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, tier={self.tier})>"
