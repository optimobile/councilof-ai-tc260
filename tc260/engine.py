"""
TC260 Verification Engine
Council of AI - Safety Verification Platform

Orchestrates all TC260 risk category modules and generates comprehensive verification reports.
"""

import time
import uuid
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from tc260.schemas import (
    VerificationRequest,
    VerificationReport,
    RiskAssessment,
    VerificationStatus,
    TC260Config
)

from tc260.modules import (
    BiasDiscriminationModule,
    PrivacyViolationModule,
    MisinformationModule,
    HarmfulContentModule,
    IntellectualPropertyModule
)


class TC260Engine:
    """
    Main verification engine that coordinates all TC260 risk category modules.
    """
    
    # Map of category IDs to module classes
    MODULE_REGISTRY = {
        'TC260-01': BiasDiscriminationModule,
        'TC260-02': PrivacyViolationModule,
        'TC260-03': MisinformationModule,
        'TC260-04': HarmfulContentModule,
        'TC260-05': IntellectualPropertyModule,
    }
    
    def __init__(self, config: Optional[TC260Config] = None):
        """
        Initialize the TC260 verification engine.
        
        Args:
            config: TC260 configuration (uses defaults if None)
        """
        self.config = config or TC260Config()
        self.modules: Dict[str, Any] = {}
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize all enabled TC260 modules"""
        for category_id, module_class in self.MODULE_REGISTRY.items():
            if category_id in self.config.enabled_categories:
                self.modules[category_id] = module_class(
                    threshold=self.config.default_threshold
                )
    
    def verify(self, request: VerificationRequest) -> VerificationReport:
        """
        Verify AI-generated content against TC260 standards.
        
        Args:
            request: Verification request with content and parameters
            
        Returns:
            Complete verification report with risk assessments
        """
        start_time = time.time()
        request_id = f"ver_{uuid.uuid4().hex[:12]}"
        
        # Determine which categories to test
        categories_to_test = request.categories or list(self.modules.keys())
        categories_to_test = [c for c in categories_to_test if c in self.modules]
        
        # Run verification across all categories
        if self.config.parallel_processing:
            risk_assessments = self._verify_parallel(
                content=request.content,
                categories=categories_to_test,
                context=request.context
            )
        else:
            risk_assessments = self._verify_sequential(
                content=request.content,
                categories=categories_to_test,
                context=request.context
            )
        
        # Calculate overall metrics
        processing_time_ms = int((time.time() - start_time) * 1000)
        overall_score = self._calculate_overall_score(risk_assessments)
        overall_status = self._determine_overall_status(risk_assessments, request.threshold)
        
        categories_passed = sum(1 for r in risk_assessments if r.passed)
        categories_failed = sum(1 for r in risk_assessments if not r.passed and r.risk_score >= request.threshold)
        categories_warning = sum(1 for r in risk_assessments if not r.passed and r.risk_score < request.threshold)
        
        return VerificationReport(
            request_id=request_id,
            overall_score=overall_score,
            overall_status=overall_status,
            categories_tested=len(risk_assessments),
            categories_passed=categories_passed,
            categories_failed=categories_failed,
            categories_warning=categories_warning,
            risk_assessments=risk_assessments,
            processing_time_ms=processing_time_ms
        )
    
    def _verify_sequential(
        self, 
        content: str, 
        categories: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[RiskAssessment]:
        """Run verification sequentially across categories"""
        risk_assessments = []
        
        for category_id in categories:
            module = self.modules[category_id]
            assessment = module.analyze(content, context)
            risk_assessments.append(assessment)
        
        return risk_assessments
    
    def _verify_parallel(
        self, 
        content: str, 
        categories: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[RiskAssessment]:
        """Run verification in parallel across categories"""
        risk_assessments = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all verification tasks
            future_to_category = {
                executor.submit(self.modules[cat_id].analyze, content, context): cat_id
                for cat_id in categories
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_category):
                try:
                    assessment = future.result(timeout=self.config.timeout_seconds)
                    risk_assessments.append(assessment)
                except Exception as e:
                    category_id = future_to_category[future]
                    print(f"Error verifying {category_id}: {e}")
        
        # Sort by category ID for consistent ordering
        risk_assessments.sort(key=lambda x: x.category_id)
        
        return risk_assessments
    
    def _calculate_overall_score(self, assessments: List[RiskAssessment]) -> float:
        """Calculate weighted average risk score across all assessments"""
        if not assessments:
            return 0.0
        
        # Weight by confidence
        total_weighted_score = sum(a.risk_score * a.confidence for a in assessments)
        total_confidence = sum(a.confidence for a in assessments)
        
        return total_weighted_score / total_confidence if total_confidence > 0 else 0.0
    
    def _determine_overall_status(
        self, 
        assessments: List[RiskAssessment],
        threshold: float
    ) -> VerificationStatus:
        """Determine overall verification status"""
        if not assessments:
            return VerificationStatus.PASS
        
        # If any critical findings, fail
        critical_findings = [a for a in assessments if a.risk_score >= 80]
        if critical_findings:
            return VerificationStatus.FAIL
        
        # If any assessments exceed threshold, fail
        failed_assessments = [a for a in assessments if not a.passed]
        if failed_assessments:
            return VerificationStatus.FAIL
        
        # If any warnings (score > 50 but < threshold)
        warning_assessments = [a for a in assessments if 50 <= a.risk_score < threshold]
        if warning_assessments:
            return VerificationStatus.WARNING
        
        return VerificationStatus.PASS
    
    def get_module_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all loaded modules"""
        return {
            cat_id: {
                'category_id': module.category_id,
                'category_name': module.category_name,
                'threshold': module.threshold
            }
            for cat_id, module in self.modules.items()
        }
