"""
TC260 Verification Engine - ALL 32 MODULES
Council of AI - EU260 Safety Verification Platform

Orchestrates all 32 TC260 risk category modules for comprehensive AI safety verification.
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

# Import all 32 modules
from tc260.modules.tc260_01_bias import BiasDiscriminationModule
from tc260.modules.tc260_02_privacy import PrivacyViolationModule
from tc260.modules.tc260_03_misinfo import MisinformationModule
from tc260.modules.tc260_04_harmful import HarmfulContentModule
from tc260.modules.tc260_05_ip import IntellectualPropertyModule
from tc260.modules.tc260_06_manipulation_and_deception import ManipulationDeceptionModule
from tc260.modules.tc260_07_autonomous_weapons import AutonomousWeaponsModule
from tc260.modules.tc260_08_economic_disruption import EconomicDisruptionModule
from tc260.modules.tc260_09_social_engineering import SocialEngineeringModule
from tc260.modules.tc260_10_deepfakes_and_synthetic_media import DeepfakesSyntheticMediaModule
from tc260.modules.tc260_11_environmental_impact import EnvironmentalImpactModule
from tc260.modules.tc260_12_labor_displacement import LaborDisplacementModule
from tc260.modules.tc260_13_surveillance_and_tracking import SurveillanceTrackingModule
from tc260.modules.tc260_14_algorithmic_bias import AlgorithmicBiasModule
from tc260.modules.tc260_15_data_poisoning import DataPoisoningModule
from tc260.modules.tc260_16_model_theft import ModelTheftModule
from tc260.modules.tc260_17_adversarial_attacks import AdversarialAttacksModule
from tc260.modules.tc260_18_prompt_injection import PromptInjectionModule
from tc260.modules.tc260_19_output_manipulation import OutputManipulationModule
from tc260.modules.tc260_20_hallucination import HallucinationModule
from tc260.modules.tc260_21_toxicity import ToxicityModule
from tc260.modules.tc260_22_child_safety import ChildSafetyModule
from tc260.modules.tc260_23_self_harm import SelfHarmModule
from tc260.modules.tc260_24_substance_abuse import SubstanceAbuseModule
from tc260.modules.tc260_25_gambling import GamblingModule
from tc260.modules.tc260_26_financial_fraud import FinancialFraudModule
from tc260.modules.tc260_27_medical_misinformation import MedicalMisinformationModule
from tc260.modules.tc260_28_legal_compliance import LegalComplianceModule
from tc260.modules.tc260_29_ethical_violations import EthicalViolationsModule
from tc260.modules.tc260_30_transparency import TransparencyModule
from tc260.modules.tc260_31_accountability import AccountabilityModule
from tc260.modules.tc260_32_human_oversight import HumanOversightModule


class TC260Engine:
    """
    Complete TC260/EU260 verification engine with all 32 risk category modules.
    """
    
    # Registry of all 32 modules
    MODULE_REGISTRY = {
        'TC260-01': BiasDiscriminationModule,
        'TC260-02': PrivacyViolationModule,
        'TC260-03': MisinformationModule,
        'TC260-04': HarmfulContentModule,
        'TC260-05': IntellectualPropertyModule,
        'TC260-06': ManipulationDeceptionModule,
        'TC260-07': AutonomousWeaponsModule,
        'TC260-08': EconomicDisruptionModule,
        'TC260-09': SocialEngineeringModule,
        'TC260-10': DeepfakesSyntheticMediaModule,
        'TC260-11': EnvironmentalImpactModule,
        'TC260-12': LaborDisplacementModule,
        'TC260-13': SurveillanceTrackingModule,
        'TC260-14': AlgorithmicBiasModule,
        'TC260-15': DataPoisoningModule,
        'TC260-16': ModelTheftModule,
        'TC260-17': AdversarialAttacksModule,
        'TC260-18': PromptInjectionModule,
        'TC260-19': OutputManipulationModule,
        'TC260-20': HallucinationModule,
        'TC260-21': ToxicityModule,
        'TC260-22': ChildSafetyModule,
        'TC260-23': SelfHarmModule,
        'TC260-24': SubstanceAbuseModule,
        'TC260-25': GamblingModule,
        'TC260-26': FinancialFraudModule,
        'TC260-27': MedicalMisinformationModule,
        'TC260-28': LegalComplianceModule,
        'TC260-29': EthicalViolationsModule,
        'TC260-30': TransparencyModule,
        'TC260-31': AccountabilityModule,
        'TC260-32': HumanOversightModule,
    }
    
    def __init__(self, config: Optional[TC260Config] = None):
        """Initialize TC260 engine with all 32 modules"""
        self.config = config or TC260Config()
        self.modules: Dict[str, Any] = {}
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Load all enabled modules"""
        for category_id in self.config.enabled_categories:
            if category_id in self.MODULE_REGISTRY:
                module_class = self.MODULE_REGISTRY[category_id]
                self.modules[category_id] = module_class(self.config.default_threshold)
    
    def verify(self, request: VerificationRequest) -> VerificationReport:
        """
        Perform comprehensive TC260/EU260 verification.
        
        Args:
            request: Verification request with content and options
            
        Returns:
            Complete verification report with all risk assessments
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Determine which categories to test
        categories_to_test = request.categories or list(self.modules.keys())
        
        # Run verification (parallel or sequential)
        if self.config.parallel_processing:
            assessments = self._verify_parallel(request.content, categories_to_test, request.context)
        else:
            assessments = self._verify_sequential(request.content, categories_to_test, request.context)
        
        # Calculate overall metrics
        overall_score = sum(a.risk_score for a in assessments) / len(assessments) if assessments else 0.0
        
        categories_passed = sum(1 for a in assessments if a.passed)
        categories_failed = sum(1 for a in assessments if not a.passed and a.risk_score >= request.threshold)
        categories_warning = sum(1 for a in assessments if not a.passed and a.risk_score < request.threshold)
        
        # Determine overall status
        if categories_failed > 0:
            overall_status = VerificationStatus.FAIL
        elif categories_warning > 0:
            overall_status = VerificationStatus.WARNING
        else:
            overall_status = VerificationStatus.PASS
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return VerificationReport(
            request_id=request_id,
            overall_score=overall_score,
            overall_status=overall_status,
            categories_tested=len(assessments),
            categories_passed=categories_passed,
            categories_failed=categories_failed,
            categories_warning=categories_warning,
            risk_assessments=assessments,
            processing_time_ms=processing_time_ms
        )
    
    def _verify_parallel(self, content: str, categories: List[str], context: Optional[Dict[str, Any]]) -> List[RiskAssessment]:
        """Run verification in parallel using thread pool"""
        assessments = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_category = {
                executor.submit(self.modules[cat].analyze, content, context): cat
                for cat in categories if cat in self.modules
            }
            
            for future in as_completed(future_to_category):
                try:
                    assessment = future.result(timeout=self.config.timeout_seconds)
                    assessments.append(assessment)
                except Exception as e:
                    category = future_to_category[future]
                    print(f"Error in {category}: {e}")
        
        return sorted(assessments, key=lambda x: x.category_id)
    
    def _verify_sequential(self, content: str, categories: List[str], context: Optional[Dict[str, Any]]) -> List[RiskAssessment]:
        """Run verification sequentially"""
        assessments = []
        
        for category in categories:
            if category in self.modules:
                try:
                    assessment = self.modules[category].analyze(content, context)
                    assessments.append(assessment)
                except Exception as e:
                    print(f"Error in {category}: {e}")
        
        return assessments
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get information about loaded modules"""
        return {
            "total_modules": len(self.MODULE_REGISTRY),
            "loaded_modules": len(self.modules),
            "enabled_categories": self.config.enabled_categories,
            "modules": {
                cat_id: {
                    "name": module.category_name,
                    "threshold": module.threshold
                }
                for cat_id, module in self.modules.items()
            }
        }
