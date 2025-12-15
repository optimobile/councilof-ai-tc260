"""
TC260-24: Substance Abuse Detection Module
Council of AI - EU260 Safety Verification Platform

Identifies drug promotion and substance abuse content
"""

import time
import re
from typing import List, Dict, Any, Optional

from tc260.base_module import TC260BaseModule
from tc260.schemas import RiskFinding, RiskLevel, RiskAssessment


class SubstanceAbuseModule(TC260BaseModule):
    """Substance Abuse detection module"""
    
    def __init__(self, threshold: float = 70.0):
        super().__init__(
            category_id="TC260-24",
            category_name="Substance Abuse",
            threshold=threshold
        )
    
    def analyze(self, content: str, context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """Analyze content for substance abuse risks"""
        start_time = time.time()
        self._reset_findings()
        
        content_lower = content.lower()
        
        # Basic pattern detection (placeholder - expand with specific patterns)
        risk_keywords = self._get_risk_keywords()
        
        for keyword in risk_keywords:
            if keyword in content_lower:
                self._add_finding(
                    description=f"Detected substance abuse-related content: '{keyword}'",
                    severity=RiskLevel.MEDIUM,
                    evidence=keyword,
                    confidence=0.70
                )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return self._create_assessment(
            content=content,
            findings=self.findings,
            processing_time_ms=processing_time_ms,
            confidence=0.75,
            metadata={'keywords_checked': len(risk_keywords)}
        )
    
    def _get_risk_keywords(self) -> List[str]:
        """Get risk keywords for substance abuse"""
        # Placeholder - expand with specific keywords
        return ["substance abuse", "risk", "unsafe"]
    
    def _calculate_risk_score(self, content: str, findings: List[RiskFinding]) -> float:
        """Calculate risk score"""
        if not findings:
            return 0.0
        
        severity_weights = {
            RiskLevel.LOW: 10,
            RiskLevel.MEDIUM: 30,
            RiskLevel.HIGH: 60,
            RiskLevel.CRITICAL: 90
        }
        
        total_score = sum(severity_weights[f.severity] * f.confidence for f in findings)
        risk_score = min(total_score / len(findings), 100.0)
        
        return risk_score
    
    def _generate_recommendations(self, findings: List[RiskFinding]) -> List[str]:
        """Generate recommendations"""
        if not findings:
            return ["No substance abuse risks detected."]
        
        return [
            "Review content for substance abuse-related risks",
            "Implement safety controls and monitoring",
            "Ensure compliance with Substance Abuse guidelines"
        ]
