"""
PDCA Cycle - Plan-Do-Check-Act (Japanese Framework)
Continuous improvement framework for AI safety governance.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class PDCAPhase(str, Enum):
    """PDCA cycle phases"""
    PLAN = "PLAN"
    DO = "DO"
    CHECK = "CHECK"
    ACT = "ACT"


class PDCACycle:
    """
    PDCA (Plan-Do-Check-Act) cycle implementation for AI safety.
    
    PLAN: Define AI safety requirements and policies
    DO: Execute verification using Council of 32 AIs
    CHECK: Review results and validate accuracy
    ACT: Implement improvements and corrective actions
    """
    
    def __init__(self, db_session=None):
        """Initialize PDCA cycle"""
        self.db = db_session
        self.cycles = {}
    
    def create_cycle(
        self,
        user_id: str,
        project_name: str,
        frameworks: List[str],
        risk_threshold: float = 70.0
    ) -> Dict[str, Any]:
        """
        PLAN: Create a new PDCA cycle.
        
        Args:
            user_id: User creating the cycle
            project_name: Name of the project/system being verified
            frameworks: List of frameworks to comply with (e.g., ["TC260", "EU_AI_ACT"])
            risk_threshold: Maximum acceptable risk score (0-100)
        
        Returns:
            PDCA cycle record
        """
        cycle_id = f"pdca_{int(datetime.utcnow().timestamp() * 1000)}"
        
        cycle = {
            "cycle_id": cycle_id,
            "user_id": user_id,
            "project_name": project_name,
            "phase": PDCAPhase.PLAN,
            "frameworks": frameworks,
            "risk_threshold": risk_threshold,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "plan": {
                "objectives": [],
                "policies": [],
                "success_criteria": []
            },
            "do": {
                "verifications": [],
                "total_verifications": 0
            },
            "check": {
                "reviews": [],
                "accuracy": 0.0,
                "issues_found": 0
            },
            "act": {
                "actions": [],
                "improvements": []
            }
        }
        
        self.cycles[cycle_id] = cycle
        return cycle
    
    def add_objective(self, cycle_id: str, objective: str) -> Dict[str, Any]:
        """
        PLAN: Add an objective to the cycle.
        
        Example objectives:
        - "Ensure all AI outputs are bias-free"
        - "Comply with EU AI Act by Aug 2, 2026"
        - "Achieve 95% accuracy on harmful content detection"
        """
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        cycle["plan"]["objectives"].append({
            "objective": objective,
            "added_at": datetime.utcnow().isoformat()
        })
        cycle["updated_at"] = datetime.utcnow().isoformat()
        
        return cycle
    
    def add_policy(self, cycle_id: str, policy: str) -> Dict[str, Any]:
        """
        PLAN: Add a policy to the cycle.
        
        Example policies:
        - "All AI outputs must be verified before deployment"
        - "High-risk content requires human review"
        - "Monthly compliance audits required"
        """
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        cycle["plan"]["policies"].append({
            "policy": policy,
            "added_at": datetime.utcnow().isoformat()
        })
        cycle["updated_at"] = datetime.utcnow().isoformat()
        
        return cycle
    
    def execute_verification(
        self,
        cycle_id: str,
        verification_id: str,
        verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        DO: Record a verification execution.
        
        Args:
            cycle_id: PDCA cycle ID
            verification_id: ID of the verification
            verification_result: Result from Council of 32 AIs
        
        Returns:
            Updated cycle
        """
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        # Move to DO phase if still in PLAN
        if cycle["phase"] == PDCAPhase.PLAN:
            cycle["phase"] = PDCAPhase.DO
        
        # Record verification
        cycle["do"]["verifications"].append({
            "verification_id": verification_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_vote": verification_result.get("overall_vote"),
            "overall_risk_score": verification_result.get("overall_risk_score"),
            "passed": verification_result.get("overall_vote") == "PASS"
        })
        cycle["do"]["total_verifications"] += 1
        cycle["updated_at"] = datetime.utcnow().isoformat()
        
        return cycle
    
    def add_review(
        self,
        cycle_id: str,
        reviewer_id: str,
        verification_id: str,
        is_accurate: bool,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        CHECK: Add a human review of a verification.
        
        Args:
            cycle_id: PDCA cycle ID
            reviewer_id: ID of the reviewer
            verification_id: ID of the verification being reviewed
            is_accurate: Whether the AI verification was accurate
            notes: Optional review notes
        
        Returns:
            Updated cycle
        """
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        # Move to CHECK phase
        if cycle["phase"] in [PDCAPhase.PLAN, PDCAPhase.DO]:
            cycle["phase"] = PDCAPhase.CHECK
        
        # Record review
        review = {
            "reviewer_id": reviewer_id,
            "verification_id": verification_id,
            "is_accurate": is_accurate,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        cycle["check"]["reviews"].append(review)
        
        # Update accuracy
        total_reviews = len(cycle["check"]["reviews"])
        accurate_reviews = sum(1 for r in cycle["check"]["reviews"] if r["is_accurate"])
        cycle["check"]["accuracy"] = accurate_reviews / total_reviews if total_reviews > 0 else 0.0
        
        # Count issues
        if not is_accurate:
            cycle["check"]["issues_found"] += 1
        
        cycle["updated_at"] = datetime.utcnow().isoformat()
        
        return cycle
    
    def add_action(
        self,
        cycle_id: str,
        action_type: str,
        description: str,
        assigned_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        ACT: Add a corrective action or improvement.
        
        Args:
            cycle_id: PDCA cycle ID
            action_type: Type of action ("CORRECTIVE" or "IMPROVEMENT")
            description: Description of the action
            assigned_to: Optional user ID assigned to implement
        
        Returns:
            Updated cycle
        """
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        # Move to ACT phase
        cycle["phase"] = PDCAPhase.ACT
        
        # Record action
        action = {
            "action_id": f"act_{int(datetime.utcnow().timestamp() * 1000)}",
            "action_type": action_type,
            "description": description,
            "assigned_to": assigned_to,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None
        }
        cycle["act"]["actions"].append(action)
        cycle["updated_at"] = datetime.utcnow().isoformat()
        
        return cycle
    
    def complete_action(self, cycle_id: str, action_id: str) -> Dict[str, Any]:
        """
        ACT: Mark an action as completed.
        
        Returns:
            Updated cycle
        """
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        # Find and update action
        for action in cycle["act"]["actions"]:
            if action["action_id"] == action_id:
                action["status"] = "COMPLETED"
                action["completed_at"] = datetime.utcnow().isoformat()
                break
        
        cycle["updated_at"] = datetime.utcnow().isoformat()
        
        # Check if all actions are completed
        all_completed = all(
            action["status"] == "COMPLETED"
            for action in cycle["act"]["actions"]
        )
        
        if all_completed and cycle["act"]["actions"]:
            # Cycle complete - can start a new cycle
            cycle["status"] = "COMPLETED"
            cycle["completed_at"] = datetime.utcnow().isoformat()
        
        return cycle
    
    def get_cycle_status(self, cycle_id: str) -> Dict[str, Any]:
        """
        Get current status of a PDCA cycle.
        
        Returns:
            Status summary
        """
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        return {
            "cycle_id": cycle_id,
            "project_name": cycle["project_name"],
            "current_phase": cycle["phase"],
            "created_at": cycle["created_at"],
            "updated_at": cycle["updated_at"],
            "plan": {
                "objectives_count": len(cycle["plan"]["objectives"]),
                "policies_count": len(cycle["plan"]["policies"])
            },
            "do": {
                "total_verifications": cycle["do"]["total_verifications"],
                "passed": sum(1 for v in cycle["do"]["verifications"] if v["passed"]),
                "failed": sum(1 for v in cycle["do"]["verifications"] if not v["passed"])
            },
            "check": {
                "total_reviews": len(cycle["check"]["reviews"]),
                "accuracy": cycle["check"]["accuracy"],
                "issues_found": cycle["check"]["issues_found"]
            },
            "act": {
                "total_actions": len(cycle["act"]["actions"]),
                "pending_actions": sum(1 for a in cycle["act"]["actions"] if a["status"] == "PENDING"),
                "completed_actions": sum(1 for a in cycle["act"]["actions"] if a["status"] == "COMPLETED")
            },
            "status": cycle.get("status", "IN_PROGRESS")
        }
    
    def get_all_cycles(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all PDCA cycles, optionally filtered by user.
        
        Returns:
            List of cycle status summaries
        """
        cycles = list(self.cycles.values())
        
        if user_id:
            cycles = [c for c in cycles if c["user_id"] == user_id]
        
        return [self.get_cycle_status(c["cycle_id"]) for c in cycles]
