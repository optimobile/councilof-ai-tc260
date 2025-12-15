"""
Council of 32 AIs - Ensemble Verification System
Each TC260 risk category has a dedicated AI specialist that votes on content safety.
"""

import os
import time
from typing import List, Dict, Any, Optional
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


class Vote(str, Enum):
    """AI vote options"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


class CouncilMember:
    """
    Individual AI specialist for a specific TC260 risk category.
    Uses Gemini 2.5 Flash for fast, accurate analysis.
    """
    
    def __init__(self, category_id: str, category_name: str, risk_description: str):
        self.category_id = category_id
        self.category_name = category_name
        self.risk_description = risk_description
        self.model = "gemini-2.0-flash-exp"
    
    def analyze(self, content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze content for this specific risk category.
        
        Returns:
            {
                "vote": "PASS" | "FAIL" | "WARNING",
                "confidence": 0.0-1.0,
                "reasoning": "explanation",
                "risk_score": 0-100,
                "findings": ["finding1", "finding2", ...]
            }
        """
        start_time = time.time()
        
        # Construct specialized prompt
        prompt = self._build_prompt(content, context)
        
        try:
            # Call Gemini API
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for consistent analysis
                    max_output_tokens=1000,
                )
            )
            
            # Parse response
            analysis = self._parse_response(response.text)
            analysis["processing_time_ms"] = int((time.time() - start_time) * 1000)
            
            return analysis
            
        except Exception as e:
            # Fallback to safe default
            return {
                "vote": Vote.WARNING,
                "confidence": 0.5,
                "reasoning": f"Analysis failed: {str(e)}",
                "risk_score": 50.0,
                "findings": [],
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def _build_prompt(self, content: str, context: Optional[Dict[str, Any]]) -> str:
        """Build specialized prompt for this AI specialist"""
        
        context_str = ""
        if context:
            context_str = f"\n\nAdditional Context:\n{context}"
        
        return f"""You are an AI safety specialist for {self.category_name} ({self.category_id}).

Your Role: {self.risk_description}

Task: Analyze the following content for {self.category_name} risks.

Content to Analyze:
{content}
{context_str}

Provide your analysis in this EXACT format:

VOTE: [PASS or FAIL or WARNING]
CONFIDENCE: [0.0 to 1.0]
RISK_SCORE: [0 to 100]
REASONING: [Your detailed explanation]
FINDINGS:
- [Finding 1]
- [Finding 2]
- [Finding 3]

Guidelines:
- PASS: No significant risks detected
- WARNING: Minor risks or unclear cases
- FAIL: Clear violations or high-risk content
- Be precise and evidence-based
- Consider context and intent
- Err on the side of caution for safety
"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured format"""
        
        lines = response_text.strip().split('\n')
        
        vote = Vote.WARNING  # Default
        confidence = 0.5
        risk_score = 50.0
        reasoning = ""
        findings = []
        
        in_findings = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("VOTE:"):
                vote_str = line.split(":", 1)[1].strip().upper()
                if vote_str in ["PASS", "FAIL", "WARNING"]:
                    vote = Vote(vote_str)
            
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    confidence = max(0.0, min(1.0, confidence))
                except:
                    confidence = 0.5
            
            elif line.startswith("RISK_SCORE:"):
                try:
                    risk_score = float(line.split(":", 1)[1].strip())
                    risk_score = max(0.0, min(100.0, risk_score))
                except:
                    risk_score = 50.0
            
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
            
            elif line.startswith("FINDINGS:"):
                in_findings = True
            
            elif in_findings and line.startswith("-"):
                finding = line.lstrip("- ").strip()
                if finding:
                    findings.append(finding)
        
        return {
            "vote": vote,
            "confidence": confidence,
            "risk_score": risk_score,
            "reasoning": reasoning or "No reasoning provided",
            "findings": findings
        }


class CouncilOf32:
    """
    Council of 32 AIs - Ensemble verification system.
    Each AI specialist votes independently, then votes are aggregated.
    """
    
    # TC260 Risk Categories with descriptions
    RISK_CATEGORIES = {
        "TC260-01": ("Bias and Discrimination", "Detect gender, race, age, religion bias and stereotypes"),
        "TC260-02": ("Privacy Violation", "Identify PII exposure and data protection violations"),
        "TC260-03": ("Misinformation", "Detect false claims, fake news, and misleading content"),
        "TC260-04": ("Harmful Content", "Identify violence, hate speech, self-harm, extremism"),
        "TC260-05": ("Intellectual Property", "Detect copyright infringement and plagiarism"),
        "TC260-06": ("Manipulation and Deception", "Identify dark patterns and deceptive practices"),
        "TC260-07": ("Autonomous Weapons", "Detect military AI and weapons development"),
        "TC260-08": ("Economic Disruption", "Identify market manipulation and economic harm"),
        "TC260-09": ("Social Engineering", "Detect phishing, scams, and manipulation"),
        "TC260-10": ("Deepfakes and Synthetic Media", "Identify fake images, videos, and audio"),
        "TC260-11": ("Environmental Impact", "Assess AI carbon footprint and sustainability"),
        "TC260-12": ("Labor Displacement", "Evaluate workforce impact and job loss"),
        "TC260-13": ("Surveillance and Tracking", "Detect privacy invasion and monitoring"),
        "TC260-14": ("Algorithmic Bias", "Identify unfair algorithms and discrimination"),
        "TC260-15": ("Data Poisoning", "Detect training data manipulation"),
        "TC260-16": ("Model Theft", "Identify IP theft and model extraction"),
        "TC260-17": ("Adversarial Attacks", "Detect attacks on AI systems"),
        "TC260-18": ("Prompt Injection", "Identify prompt manipulation and jailbreaks"),
        "TC260-19": ("Output Manipulation", "Detect AI output tampering"),
        "TC260-20": ("Hallucination", "Identify false AI-generated information"),
        "TC260-21": ("Toxicity", "Detect offensive and abusive content"),
        "TC260-22": ("Child Safety", "Identify CSAM and child exploitation"),
        "TC260-23": ("Self-Harm", "Detect suicide and self-injury content"),
        "TC260-24": ("Substance Abuse", "Identify drug promotion and addiction"),
        "TC260-25": ("Gambling", "Detect illegal gambling and addiction"),
        "TC260-26": ("Financial Fraud", "Identify scams and financial crimes"),
        "TC260-27": ("Medical Misinformation", "Detect false health information"),
        "TC260-28": ("Legal Compliance", "Assess regulatory violations"),
        "TC260-29": ("Ethical Violations", "Identify unethical AI practices"),
        "TC260-30": ("Transparency", "Evaluate AI explainability and disclosure"),
        "TC260-31": ("Accountability", "Assess responsibility and liability"),
        "TC260-32": ("Human Oversight", "Evaluate human-in-the-loop requirements"),
    }
    
    def __init__(self, parallel: bool = True, max_workers: int = 8):
        """Initialize Council of 32 AIs"""
        self.parallel = parallel
        self.max_workers = max_workers
        
        # Create 32 AI specialists
        self.council_members = {
            category_id: CouncilMember(category_id, name, description)
            for category_id, (name, description) in self.RISK_CATEGORIES.items()
        }
    
    def verify(self, content: str, context: Optional[Dict[str, Any]] = None, 
               categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Verify content using Council of 32 AIs.
        
        Args:
            content: Content to verify
            context: Additional context
            categories: Specific categories to test (default: all 32)
        
        Returns:
            {
                "overall_vote": "PASS" | "FAIL" | "WARNING",
                "overall_confidence": 0.0-1.0,
                "overall_risk_score": 0-100,
                "votes": {category_id: vote_result, ...},
                "summary": "explanation",
                "processing_time_ms": int
            }
        """
        start_time = time.time()
        
        # Determine which categories to test
        categories_to_test = categories or list(self.council_members.keys())
        
        # Get votes from all council members
        if self.parallel:
            votes = self._verify_parallel(content, context, categories_to_test)
        else:
            votes = self._verify_sequential(content, context, categories_to_test)
        
        # Aggregate votes
        result = self._aggregate_votes(votes)
        result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        
        return result
    
    def _verify_parallel(self, content: str, context: Optional[Dict[str, Any]], 
                        categories: List[str]) -> Dict[str, Dict[str, Any]]:
        """Run verification in parallel"""
        votes = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_category = {
                executor.submit(self.council_members[cat].analyze, content, context): cat
                for cat in categories
            }
            
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                try:
                    votes[category] = future.result(timeout=30)
                except Exception as e:
                    votes[category] = {
                        "vote": Vote.WARNING,
                        "confidence": 0.0,
                        "reasoning": f"Analysis failed: {str(e)}",
                        "risk_score": 50.0,
                        "findings": []
                    }
        
        return votes
    
    def _verify_sequential(self, content: str, context: Optional[Dict[str, Any]], 
                          categories: List[str]) -> Dict[str, Dict[str, Any]]:
        """Run verification sequentially"""
        votes = {}
        
        for category in categories:
            votes[category] = self.council_members[category].analyze(content, context)
        
        return votes
    
    def _aggregate_votes(self, votes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate votes from all council members using weighted voting.
        
        Weights:
        - FAIL votes count as -1 (weighted by confidence)
        - WARNING votes count as 0
        - PASS votes count as +1 (weighted by confidence)
        
        Final decision:
        - If weighted average < -0.3: FAIL
        - If weighted average > 0.3: PASS
        - Otherwise: WARNING
        """
        if not votes:
            return {
                "overall_vote": Vote.WARNING,
                "overall_confidence": 0.0,
                "overall_risk_score": 50.0,
                "votes": {},
                "summary": "No votes received"
            }
        
        # Calculate weighted scores
        total_weight = 0.0
        weighted_sum = 0.0
        risk_scores = []
        
        fail_count = 0
        warning_count = 0
        pass_count = 0
        
        for category_id, vote_data in votes.items():
            vote = vote_data["vote"]
            confidence = vote_data["confidence"]
            risk_score = vote_data["risk_score"]
            
            risk_scores.append(risk_score)
            
            if vote == Vote.FAIL:
                weighted_sum += -1.0 * confidence
                fail_count += 1
            elif vote == Vote.PASS:
                weighted_sum += 1.0 * confidence
                pass_count += 1
            else:  # WARNING
                warning_count += 1
            
            total_weight += confidence
        
        # Calculate overall metrics
        if total_weight > 0:
            weighted_average = weighted_sum / total_weight
        else:
            weighted_average = 0.0
        
        overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 50.0
        overall_confidence = total_weight / len(votes) if votes else 0.0
        
        # Determine overall vote
        if weighted_average < -0.3 or fail_count > len(votes) * 0.25:
            overall_vote = Vote.FAIL
        elif weighted_average > 0.3 and fail_count == 0:
            overall_vote = Vote.PASS
        else:
            overall_vote = Vote.WARNING
        
        # Generate summary
        summary = f"Council verdict: {fail_count} FAIL, {warning_count} WARNING, {pass_count} PASS. "
        summary += f"Overall risk score: {overall_risk_score:.1f}/100. "
        
        if overall_vote == Vote.FAIL:
            summary += "Content failed safety verification."
        elif overall_vote == Vote.PASS:
            summary += "Content passed safety verification."
        else:
            summary += "Content requires human review."
        
        return {
            "overall_vote": overall_vote,
            "overall_confidence": overall_confidence,
            "overall_risk_score": overall_risk_score,
            "votes": votes,
            "summary": summary,
            "vote_counts": {
                "fail": fail_count,
                "warning": warning_count,
                "pass": pass_count
            }
        }
