"""
RLMAI - Reinforcement Learning from Manual AI Inspection
Continuous improvement system that learns from human feedback.
"""

import os
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    """Types of human feedback"""
    CORRECT = "CORRECT"  # AI was right
    INCORRECT = "INCORRECT"  # AI was wrong
    FALSE_POSITIVE = "FALSE_POSITIVE"  # AI flagged safe content
    FALSE_NEGATIVE = "FALSE_NEGATIVE"  # AI missed unsafe content
    SEVERITY_TOO_HIGH = "SEVERITY_TOO_HIGH"  # Risk score too high
    SEVERITY_TOO_LOW = "SEVERITY_TOO_LOW"  # Risk score too low


class RLMAIFeedback:
    """
    Stores and manages human feedback for RLMAI system.
    """
    
    def __init__(self, db_session=None):
        """Initialize RLMAI feedback system"""
        self.db = db_session
        self.feedback_log = []
    
    def record_feedback(
        self,
        verification_id: str,
        category_id: str,
        feedback_type: FeedbackType,
        user_id: str,
        notes: Optional[str] = None,
        corrected_vote: Optional[str] = None,
        corrected_risk_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Record human feedback on an AI verification.
        
        Args:
            verification_id: ID of the verification
            category_id: TC260 category (e.g., "TC260-01")
            feedback_type: Type of feedback
            user_id: ID of user providing feedback
            notes: Optional notes
            corrected_vote: Corrected vote if AI was wrong
            corrected_risk_score: Corrected risk score
        
        Returns:
            Feedback record
        """
        feedback = {
            "feedback_id": f"fb_{int(time.time() * 1000)}",
            "verification_id": verification_id,
            "category_id": category_id,
            "feedback_type": feedback_type,
            "user_id": user_id,
            "notes": notes,
            "corrected_vote": corrected_vote,
            "corrected_risk_score": corrected_risk_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in database if available
        if self.db:
            self._store_in_database(feedback)
        else:
            # Fallback to in-memory storage
            self.feedback_log.append(feedback)
        
        return feedback
    
    def get_feedback_stats(self, category_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback statistics for RLMAI improvement.
        
        Args:
            category_id: Optional filter by category
        
        Returns:
            Statistics on feedback
        """
        if self.db:
            return self._get_stats_from_database(category_id)
        else:
            return self._get_stats_from_memory(category_id)
    
    def get_training_data(self, category_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get training data for fine-tuning AI models.
        
        Args:
            category_id: TC260 category
            limit: Maximum number of examples
        
        Returns:
            List of training examples
        """
        if self.db:
            return self._get_training_data_from_database(category_id, limit)
        else:
            return self._get_training_data_from_memory(category_id, limit)
    
    def _store_in_database(self, feedback: Dict[str, Any]):
        """Store feedback in database (implementation depends on DB schema)"""
        # TODO: Implement database storage
        # For now, store in memory
        self.feedback_log.append(feedback)
    
    def _get_stats_from_database(self, category_id: Optional[str]) -> Dict[str, Any]:
        """Get stats from database"""
        # TODO: Implement database queries
        return self._get_stats_from_memory(category_id)
    
    def _get_stats_from_memory(self, category_id: Optional[str]) -> Dict[str, Any]:
        """Get stats from in-memory storage"""
        feedback_list = self.feedback_log
        
        if category_id:
            feedback_list = [f for f in feedback_list if f["category_id"] == category_id]
        
        if not feedback_list:
            return {
                "total_feedback": 0,
                "accuracy": 0.0,
                "false_positive_rate": 0.0,
                "false_negative_rate": 0.0
            }
        
        total = len(feedback_list)
        correct = sum(1 for f in feedback_list if f["feedback_type"] == FeedbackType.CORRECT)
        false_positives = sum(1 for f in feedback_list if f["feedback_type"] == FeedbackType.FALSE_POSITIVE)
        false_negatives = sum(1 for f in feedback_list if f["feedback_type"] == FeedbackType.FALSE_NEGATIVE)
        
        return {
            "total_feedback": total,
            "accuracy": correct / total if total > 0 else 0.0,
            "false_positive_rate": false_positives / total if total > 0 else 0.0,
            "false_negative_rate": false_negatives / total if total > 0 else 0.0,
            "category_id": category_id
        }
    
    def _get_training_data_from_database(self, category_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get training data from database"""
        # TODO: Implement database queries
        return self._get_training_data_from_memory(category_id, limit)
    
    def _get_training_data_from_memory(self, category_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get training data from in-memory storage"""
        # Filter feedback for this category
        category_feedback = [
            f for f in self.feedback_log 
            if f["category_id"] == category_id and f["corrected_vote"]
        ]
        
        # Return most recent examples
        return category_feedback[-limit:]


class RLMAITrainer:
    """
    Trains AI models using RLMAI feedback.
    Uses Gemini fine-tuning API.
    """
    
    def __init__(self, gemini_api_key: str):
        """Initialize RLMAI trainer"""
        self.api_key = gemini_api_key
        self.training_jobs = {}
    
    def create_training_job(
        self,
        category_id: str,
        training_data: List[Dict[str, Any]],
        base_model: str = "gemini-2.0-flash-exp"
    ) -> Dict[str, Any]:
        """
        Create a fine-tuning job for a specific category.
        
        Args:
            category_id: TC260 category
            training_data: List of training examples with feedback
            base_model: Base model to fine-tune
        
        Returns:
            Training job info
        """
        if len(training_data) < 10:
            return {
                "status": "INSUFFICIENT_DATA",
                "message": f"Need at least 10 examples, got {len(training_data)}",
                "category_id": category_id
            }
        
        # Format training data for Gemini
        formatted_data = self._format_training_data(training_data)
        
        # Create training job
        job = {
            "job_id": f"train_{category_id}_{int(time.time())}",
            "category_id": category_id,
            "base_model": base_model,
            "training_examples": len(formatted_data),
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.training_jobs[job["job_id"]] = job
        
        # TODO: Actually call Gemini fine-tuning API
        # For now, simulate training
        job["status"] = "TRAINING"
        
        return job
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a training job"""
        return self.training_jobs.get(job_id)
    
    def _format_training_data(self, training_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format training data for Gemini fine-tuning"""
        formatted = []
        
        for example in training_data:
            # Extract content and corrected labels
            formatted.append({
                "input": example.get("content", ""),
                "output": {
                    "vote": example.get("corrected_vote"),
                    "risk_score": example.get("corrected_risk_score"),
                    "reasoning": example.get("notes", "")
                }
            })
        
        return formatted


class RLMAISystem:
    """
    Complete RLMAI system that coordinates feedback collection and model training.
    """
    
    def __init__(self, db_session=None, gemini_api_key: Optional[str] = None):
        """Initialize RLMAI system"""
        self.feedback = RLMAIFeedback(db_session)
        self.trainer = RLMAITrainer(gemini_api_key or os.getenv("GEMINI_API_KEY", ""))
        self.improvement_threshold = 100  # Retrain after 100 feedback examples
    
    def submit_feedback(
        self,
        verification_id: str,
        category_id: str,
        feedback_type: FeedbackType,
        user_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Submit human feedback and trigger retraining if threshold reached.
        
        Returns:
            Feedback record + training job info if triggered
        """
        # Record feedback
        feedback_record = self.feedback.record_feedback(
            verification_id=verification_id,
            category_id=category_id,
            feedback_type=feedback_type,
            user_id=user_id,
            **kwargs
        )
        
        # Check if we should trigger retraining
        stats = self.feedback.get_feedback_stats(category_id)
        
        result = {
            "feedback": feedback_record,
            "stats": stats
        }
        
        if stats["total_feedback"] >= self.improvement_threshold:
            # Trigger retraining
            training_data = self.feedback.get_training_data(category_id)
            training_job = self.trainer.create_training_job(category_id, training_data)
            result["training_job"] = training_job
        
        return result
    
    def get_improvement_report(self) -> Dict[str, Any]:
        """
        Get report on RLMAI improvements across all categories.
        
        Returns:
            Report with accuracy trends and training status
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "categories": {},
            "overall_accuracy": 0.0,
            "active_training_jobs": 0
        }
        
        # Get stats for each category
        from tc260.council import CouncilOf32
        categories = list(CouncilOf32.RISK_CATEGORIES.keys())
        
        total_accuracy = 0.0
        categories_with_feedback = 0
        
        for category_id in categories:
            stats = self.feedback.get_feedback_stats(category_id)
            if stats["total_feedback"] > 0:
                report["categories"][category_id] = stats
                total_accuracy += stats["accuracy"]
                categories_with_feedback += 1
        
        if categories_with_feedback > 0:
            report["overall_accuracy"] = total_accuracy / categories_with_feedback
        
        # Count active training jobs
        report["active_training_jobs"] = sum(
            1 for job in self.trainer.training_jobs.values()
            if job["status"] in ["PENDING", "TRAINING"]
        )
        
        return report
