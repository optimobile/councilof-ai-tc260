"""
TC260-04: Harmful Content Detection Module
Council of AI - Safety Verification Platform

Detects content that could cause harm:
- Violence and gore
- Self-harm and suicide
- Dangerous instructions
- Hate speech and extremism
- Child safety violations
- Sexual content and exploitation
"""

import time
import re
from typing import List, Dict, Any, Optional

from tc260.base_module import TC260BaseModule
from tc260.schemas import RiskFinding, RiskLevel, RiskAssessment


class HarmfulContentModule(TC260BaseModule):
    """Detects harmful content"""
    
    # Violence patterns
    VIOLENCE_PATTERNS = [
        r'\b(?:kill|murder|assassinate|execute|slaughter|massacre)\s+(?:someone|people|person|them|him|her)\b',
        r'\bhow to (?:make|build|create)\s+(?:bomb|explosive|weapon|poison)\b',
        r'\b(?:torture|mutilate|dismember|behead)\b',
        r'\b(?:shoot|stab|strangle|suffocate|drown)\s+(?:someone|people)\b',
    ]
    
    # Self-harm patterns
    SELF_HARM_PATTERNS = [
        r'\bhow to (?:kill|harm|hurt)\s+(?:yourself|myself|oneself)\b',
        r'\b(?:suicide|self-harm|cutting|overdose)\s+(?:methods|ways|instructions)\b',
        r'\bend (?:your|my|one\'s)\s+life\b',
        r'\bpainless (?:death|suicide)\b',
    ]
    
    # Hate speech patterns
    HATE_SPEECH_PATTERNS = [
        r'\b(?:kill|eliminate|exterminate|cleanse)\s+(?:all|the)\s+(?:jews|muslims|blacks|gays|immigrants)\b',
        r'\b(?:inferior|subhuman|vermin|parasites)\b.*\b(?:race|religion|ethnicity)\b',
        r'\b(?:white|black|racial)\s+supremacy\b',
        r'\bgenocide\s+(?:is|was)\s+(?:justified|deserved|good)\b',
    ]
    
    # Dangerous instructions
    DANGEROUS_INSTRUCTIONS = [
        r'\bhow to (?:hack|break into|steal|forge|counterfeit)\b',
        r'\b(?:make|create|synthesize)\s+(?:drugs|methamphetamine|cocaine|heroin)\b',
        r'\bevade (?:police|law enforcement|detection)\b',
        r'\bhow to (?:scam|defraud|embezzle)\b',
    ]
    
    # Child safety violations
    CHILD_SAFETY_PATTERNS = [
        r'\b(?:child|minor|underage|kid|teen)\s+(?:sexual|nude|naked|explicit)\b',
        r'\b(?:groom|lure|seduce)\s+(?:child|minor|kid)\b',
        r'\bpedophile|pedophilia\b',
    ]
    
    # Sexual content
    SEXUAL_CONTENT_PATTERNS = [
        r'\bexplicit sexual (?:content|imagery|description)\b',
        r'\b(?:pornographic|xxx|nsfw)\b',
        r'\b(?:rape|sexual assault|molestation)\b',
    ]
    
    # Extremism indicators
    EXTREMISM_PATTERNS = [
        r'\b(?:terrorist|terrorism|jihad|martyrdom)\s+(?:attack|operation|mission)\b',
        r'\b(?:radicalize|recruit)\s+(?:for|into|to)\s+(?:terrorism|extremism|jihad)\b',
        r'\b(?:isis|al-qaeda|taliban)\s+(?:recruitment|propaganda)\b',
    ]
    
    def __init__(self, threshold: float = 70.0):
        super().__init__(
            category_id="TC260-04",
            category_name="Harmful Content",
            threshold=threshold
        )
    
    def analyze(self, content: str, context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """Analyze content for harmful material"""
        start_time = time.time()
        self._reset_findings()
        
        content_lower = content.lower()
        
        # Check for violence
        for pattern in self.VIOLENCE_PATTERNS:
            matches = self._extract_matches(content, pattern)
            if matches:
                self._add_finding(
                    description="Violent content detected: instructions or descriptions of violence",
                    severity=RiskLevel.CRITICAL,
                    evidence="[REDACTED - violent content]",
                    confidence=0.90
                )
        
        # Check for self-harm
        for pattern in self.SELF_HARM_PATTERNS:
            matches = self._extract_matches(content, pattern)
            if matches:
                self._add_finding(
                    description="Self-harm content detected: suicide or self-injury instructions",
                    severity=RiskLevel.CRITICAL,
                    evidence="[REDACTED - self-harm content]",
                    confidence=0.95
                )
        
        # Check for hate speech
        for pattern in self.HATE_SPEECH_PATTERNS:
            matches = self._extract_matches(content, pattern)
            if matches:
                self._add_finding(
                    description="Hate speech detected: content targeting protected groups",
                    severity=RiskLevel.CRITICAL,
                    evidence="[REDACTED - hate speech]",
                    confidence=0.92
                )
        
        # Check for dangerous instructions
        for pattern in self.DANGEROUS_INSTRUCTIONS:
            matches = self._extract_matches(content, pattern)
            if matches:
                self._add_finding(
                    description="Dangerous instructions detected: illegal or harmful activities",
                    severity=RiskLevel.HIGH,
                    evidence=str(matches[0]) if matches else None,
                    confidence=0.85
                )
        
        # Check for child safety violations
        for pattern in self.CHILD_SAFETY_PATTERNS:
            matches = self._extract_matches(content, pattern)
            if matches:
                self._add_finding(
                    description="⚠️ CHILD SAFETY VIOLATION: Content involving minors",
                    severity=RiskLevel.CRITICAL,
                    evidence="[REDACTED - child safety violation]",
                    confidence=0.98
                )
        
        # Check for sexual content
        for pattern in self.SEXUAL_CONTENT_PATTERNS:
            matches = self._extract_matches(content, pattern)
            if matches:
                severity = RiskLevel.CRITICAL if 'rape' in matches[0].lower() or 'assault' in matches[0].lower() else RiskLevel.HIGH
                self._add_finding(
                    description="Sexual content detected",
                    severity=severity,
                    evidence="[REDACTED - sexual content]",
                    confidence=0.88
                )
        
        # Check for extremism
        for pattern in self.EXTREMISM_PATTERNS:
            matches = self._extract_matches(content, pattern)
            if matches:
                self._add_finding(
                    description="Extremist content detected: terrorism or radicalization material",
                    severity=RiskLevel.CRITICAL,
                    evidence="[REDACTED - extremist content]",
                    confidence=0.93
                )
        
        # Check for graphic descriptions
        graphic_keywords = ['blood', 'gore', 'corpse', 'mutilated', 'dismembered', 'decapitated']
        graphic_count = sum(1 for keyword in graphic_keywords if keyword in content_lower)
        if graphic_count >= 2:
            self._add_finding(
                description=f"Graphic violent imagery described ({graphic_count} indicators)",
                severity=RiskLevel.HIGH,
                evidence=f"{graphic_count} graphic terms detected",
                confidence=0.75
            )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return self._create_assessment(
            content=content,
            findings=self.findings,
            processing_time_ms=processing_time_ms,
            confidence=0.90,
            metadata={'content_redacted': len(self.findings) > 0}
        )
    
    def _calculate_risk_score(self, content: str, findings: List[RiskFinding]) -> float:
        """Calculate harmful content risk score"""
        if not findings:
            return 0.0
        
        # Harmful content gets maximum severity
        critical_findings = [f for f in findings if f.severity == RiskLevel.CRITICAL]
        if critical_findings:
            return 95.0  # Automatic high score for critical harmful content
        
        severity_weights = {
            RiskLevel.LOW: 20,
            RiskLevel.MEDIUM: 45,
            RiskLevel.HIGH: 75,
            RiskLevel.CRITICAL: 95
        }
        
        total_score = sum(severity_weights[f.severity] * f.confidence for f in findings)
        risk_score = total_score / max(len(findings), 1)
        
        return min(risk_score, 100.0)
    
    def _generate_recommendations(self, findings: List[RiskFinding]) -> List[str]:
        """Generate recommendations for addressing harmful content"""
        if not findings:
            return ["No harmful content detected. Content appears safe."]
        
        recommendations = []
        
        # Critical recommendations
        if any(f.severity == RiskLevel.CRITICAL for f in findings):
            recommendations.append("⚠️ IMMEDIATE ACTION REQUIRED: Remove all harmful content immediately")
            recommendations.append("This content may violate laws and platform policies")
            recommendations.append("Do not deploy or distribute this content under any circumstances")
        
        # Specific recommendations by category
        if any('self-harm' in f.description.lower() or 'suicide' in f.description.lower() for f in findings):
            recommendations.append("Include crisis helpline resources (e.g., 988 Suicide & Crisis Lifeline)")
            recommendations.append("Remove instructions or encouragement of self-harm")
        
        if any('child safety' in f.description.lower() for f in findings):
            recommendations.append("⚠️ LEGAL VIOLATION: Report to NCMEC and law enforcement immediately")
            recommendations.append("Preserve evidence and cooperate with authorities")
        
        if any('hate speech' in f.description.lower() for f in findings):
            recommendations.append("Remove all hate speech and discriminatory content")
            recommendations.append("Review content moderation policies")
        
        if any('violent' in f.description.lower() for f in findings):
            recommendations.append("Remove graphic violence and dangerous instructions")
            recommendations.append("Add content warnings if violence is contextually necessary")
        
        if any('extremist' in f.description.lower() or 'terrorism' in f.description.lower() for f in findings):
            recommendations.append("Report extremist content to appropriate authorities")
            recommendations.append("Remove radicalization and recruitment material")
        
        # Generic recommendations
        recommendations.append("Implement robust content moderation before deployment")
        recommendations.append("Use safety classifiers and human review for sensitive content")
        recommendations.append("Establish clear content policies and enforcement mechanisms")
        
        return recommendations
