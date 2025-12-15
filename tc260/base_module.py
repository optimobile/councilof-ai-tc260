"""
Base Module for TC260 Risk Categories
Council of AI - Safety Verification Platform

All TC260 risk category modules inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import re

# Import schemas (will be in same directory when deployed)

from tc260.schemas import RiskAssessment, RiskFinding, RiskLevel


class TC260BaseModule(ABC):
    """
    Abstract base class for all TC260 risk category modules.
    
    Each module must implement:
    - analyze(): Main analysis logic
    - _calculate_risk_score(): Risk scoring algorithm
    - _generate_recommendations(): Remediation suggestions
    """
    
    def __init__(self, category_id: str, category_name: str, threshold: float = 70.0):
        """
        Initialize the base module.
        
        Args:
            category_id: TC260 category identifier (e.g., "TC260-01")
            category_name: Human-readable name (e.g., "Bias and Discrimination")
            threshold: Risk score threshold above which assessment fails
        """
        self.category_id = category_id
        self.category_name = category_name
        self.threshold = threshold
        self.findings: List[RiskFinding] = []
        
    @abstractmethod
    def analyze(self, content: str, context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """
        Analyze content for risks in this category.
        
        Args:
            content: AI-generated content to analyze
            context: Optional additional context
            
        Returns:
            RiskAssessment with findings and recommendations
        """
        pass
    
    @abstractmethod
    def _calculate_risk_score(self, content: str, findings: List[RiskFinding]) -> float:
        """
        Calculate numerical risk score (0-100).
        
        Args:
            content: Content being analyzed
            findings: List of risk findings
            
        Returns:
            Risk score from 0 (safe) to 100 (critical)
        """
        pass
    
    @abstractmethod
    def _generate_recommendations(self, findings: List[RiskFinding]) -> List[str]:
        """
        Generate actionable recommendations based on findings.
        
        Args:
            findings: List of risk findings
            
        Returns:
            List of recommendation strings
        """
        pass
    
    def _determine_severity(self, risk_score: float) -> RiskLevel:
        """
        Map risk score to severity level.
        
        Args:
            risk_score: Numerical risk score (0-100)
            
        Returns:
            RiskLevel enum value
        """
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _create_assessment(
        self, 
        content: str, 
        findings: List[RiskFinding],
        processing_time_ms: int,
        confidence: float = 0.85,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """
        Create a complete RiskAssessment object.
        
        Args:
            content: Content that was analyzed
            findings: List of risk findings
            processing_time_ms: Time taken to process
            confidence: Model confidence (0-1)
            metadata: Additional metadata
            
        Returns:
            Complete RiskAssessment object
        """
        risk_score = self._calculate_risk_score(content, findings)
        severity = self._determine_severity(risk_score)
        recommendations = self._generate_recommendations(findings)
        passed = risk_score < self.threshold
        
        return RiskAssessment(
            category_id=self.category_id,
            category_name=self.category_name,
            risk_score=risk_score,
            severity=severity,
            passed=passed,
            findings=findings,
            recommendations=recommendations,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
    
    def _add_finding(
        self, 
        description: str, 
        severity: RiskLevel,
        location: Optional[str] = None,
        evidence: Optional[str] = None,
        confidence: float = 0.85
    ):
        """
        Add a risk finding to the current analysis.
        
        Args:
            description: Description of the finding
            severity: Severity level
            location: Where in the content this was found
            evidence: Supporting evidence
            confidence: Confidence in this finding (0-1)
        """
        finding = RiskFinding(
            description=description,
            severity=severity,
            location=location,
            evidence=evidence,
            confidence=confidence
        )
        self.findings.append(finding)
    
    def _reset_findings(self):
        """Clear all findings (called at start of each analysis)"""
        self.findings = []
    
    # Utility methods for common pattern matching
    
    def _contains_pattern(self, content: str, pattern: str, case_sensitive: bool = False) -> bool:
        """Check if content contains a regex pattern"""
        flags = 0 if case_sensitive else re.IGNORECASE
        return bool(re.search(pattern, content, flags))
    
    def _extract_matches(self, content: str, pattern: str, case_sensitive: bool = False) -> List[str]:
        """Extract all matches of a regex pattern"""
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.findall(pattern, content, flags)
    
    def _count_occurrences(self, content: str, pattern: str, case_sensitive: bool = False) -> int:
        """Count occurrences of a pattern"""
        return len(self._extract_matches(content, pattern, case_sensitive))
