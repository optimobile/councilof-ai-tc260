"""
Council of AI - Complete API Routes
Enterprise-grade API for EU260 AI Safety Verification Platform
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib

from tc260.council import CouncilOf32, Vote
from tc260.rlmai import RLMAISystem, FeedbackType
from tc260.pdca import PDCACycle, PDCAPhase
from tc260.blockchain import VerificationBlockchain

# Initialize router
router = APIRouter()

# Initialize systems (in production, these would be singletons or from dependency injection)
council = CouncilOf32(parallel=True, max_workers=8)
rlmai = RLMAISystem()
pdca = PDCACycle()
blockchain = VerificationBlockchain(difficulty=2)


# ============================================================================
# Pydantic Models
# ============================================================================

class VerificationRequest(BaseModel):
    """Request for AI safety verification"""
    content: str = Field(..., description="Content to verify")
    categories: Optional[List[str]] = Field(None, description="Specific TC260 categories to test")
    user_id: str = Field(..., description="User requesting verification")
    project_name: Optional[str] = Field(None, description="Project name for PDCA tracking")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class VerificationResponse(BaseModel):
    """Response from AI safety verification"""
    verification_id: str
    overall_vote: str
    overall_risk_score: float
    overall_confidence: float
    summary: str
    votes: Dict[str, Any]
    processing_time_ms: int
    blockchain_pending: bool
    timestamp: str


class FeedbackRequest(BaseModel):
    """Request to submit feedback on a verification"""
    verification_id: str
    category_id: str
    feedback_type: FeedbackType
    user_id: str
    notes: Optional[str] = None
    corrected_vote: Optional[str] = None
    corrected_risk_score: Optional[float] = None


class PDCACycleRequest(BaseModel):
    """Request to create a PDCA cycle"""
    user_id: str
    project_name: str
    frameworks: List[str] = Field(default=["TC260", "EU_AI_ACT"])
    risk_threshold: float = Field(default=70.0, ge=0.0, le=100.0)


class PDCAObjectiveRequest(BaseModel):
    """Request to add objective to PDCA cycle"""
    cycle_id: str
    objective: str


class PDCAPolicyRequest(BaseModel):
    """Request to add policy to PDCA cycle"""
    cycle_id: str
    policy: str


class PDCAActionRequest(BaseModel):
    """Request to add action to PDCA cycle"""
    cycle_id: str
    action_type: str = Field(..., description="CORRECTIVE or IMPROVEMENT")
    description: str
    assigned_to: Optional[str] = None


# ============================================================================
# Council of 32 AIs - Verification Endpoints
# ============================================================================

@router.post("/verify", response_model=VerificationResponse)
async def verify_content(
    request: VerificationRequest,
    background_tasks: BackgroundTasks
):
    """
    Verify content using Council of 32 AIs.
    
    Returns immediate verification result and queues blockchain logging.
    """
    # Generate verification ID
    content_hash = hashlib.sha256(request.content.encode()).hexdigest()
    verification_id = f"ver_{int(datetime.utcnow().timestamp() * 1000)}"
    
    # Run Council of 32 AIs verification
    result = council.verify(
        content=request.content,
        categories=request.categories
    )
    
    # Add verification ID and timestamp
    result["verification_id"] = verification_id
    result["timestamp"] = datetime.utcnow().isoformat()
    
    # Add to blockchain (pending)
    blockchain.add_verification(
        verification_id=verification_id,
        content_hash=content_hash,
        verification_result=result,
        user_id=request.user_id,
        metadata=request.metadata
    )
    
    # Mine blockchain in background
    background_tasks.add_task(blockchain.mine_pending_verifications)
    
    # Track in PDCA if project specified
    if request.project_name:
        # Find or create PDCA cycle
        cycles = pdca.get_all_cycles(user_id=request.user_id)
        project_cycles = [c for c in cycles if c["project_name"] == request.project_name]
        
        if project_cycles:
            cycle_id = project_cycles[0]["cycle_id"]
            pdca.execute_verification(cycle_id, verification_id, result)
    
    return VerificationResponse(
        verification_id=verification_id,
        overall_vote=result["overall_vote"],
        overall_risk_score=result["overall_risk_score"],
        overall_confidence=result["overall_confidence"],
        summary=result["summary"],
        votes=result["votes"],
        processing_time_ms=result["processing_time_ms"],
        blockchain_pending=True,
        timestamp=result["timestamp"]
    )


@router.get("/verify/{verification_id}")
async def get_verification(verification_id: str):
    """
    Get verification details from blockchain.
    
    Returns complete immutable history of this verification.
    """
    history = blockchain.get_verification_history(verification_id)
    
    if not history:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {
        "verification_id": verification_id,
        "history": history,
        "total_records": len(history)
    }


@router.get("/verify/user/{user_id}")
async def get_user_verifications(user_id: str, limit: int = 100):
    """
    Get all verifications by a user.
    
    Returns verification history from blockchain.
    """
    verifications = blockchain.get_user_verifications(user_id)
    
    # Sort by timestamp (most recent first)
    verifications.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "user_id": user_id,
        "total_verifications": len(verifications),
        "verifications": verifications[:limit]
    }


# ============================================================================
# RLMAI - Feedback & Learning Endpoints
# ============================================================================

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Submit human feedback on a verification.
    
    Triggers RLMAI learning and blockchain logging.
    """
    # Submit to RLMAI system
    result = rlmai.submit_feedback(
        verification_id=request.verification_id,
        category_id=request.category_id,
        feedback_type=request.feedback_type,
        user_id=request.user_id,
        notes=request.notes,
        corrected_vote=request.corrected_vote,
        corrected_risk_score=request.corrected_risk_score
    )
    
    # Log to blockchain
    feedback_id = result["feedback"]["feedback_id"]
    background_tasks.add_task(
        blockchain.add_feedback,
        feedback_id=feedback_id,
        verification_id=request.verification_id,
        feedback_type=request.feedback_type,
        user_id=request.user_id,
        metadata={"notes": request.notes}
    )
    
    return result


@router.get("/rlmai/stats")
async def get_rlmai_stats(category_id: Optional[str] = None):
    """
    Get RLMAI improvement statistics.
    
    Shows accuracy trends and learning progress.
    """
    if category_id:
        return rlmai.feedback.get_feedback_stats(category_id)
    else:
        return rlmai.get_improvement_report()


@router.get("/rlmai/training")
async def get_training_jobs():
    """
    Get status of RLMAI training jobs.
    
    Shows active fine-tuning jobs.
    """
    return {
        "training_jobs": list(rlmai.trainer.training_jobs.values()),
        "total_jobs": len(rlmai.trainer.training_jobs)
    }


# ============================================================================
# PDCA Cycle - Governance Endpoints
# ============================================================================

@router.post("/pdca/cycle")
async def create_pdca_cycle(request: PDCACycleRequest):
    """
    Create a new PDCA cycle for continuous improvement.
    
    PLAN phase - Define objectives and policies.
    """
    cycle = pdca.create_cycle(
        user_id=request.user_id,
        project_name=request.project_name,
        frameworks=request.frameworks,
        risk_threshold=request.risk_threshold
    )
    
    return cycle


@router.post("/pdca/objective")
async def add_pdca_objective(request: PDCAObjectiveRequest):
    """
    Add an objective to a PDCA cycle.
    
    PLAN phase.
    """
    cycle = pdca.add_objective(request.cycle_id, request.objective)
    return pdca.get_cycle_status(request.cycle_id)


@router.post("/pdca/policy")
async def add_pdca_policy(request: PDCAPolicyRequest):
    """
    Add a policy to a PDCA cycle.
    
    PLAN phase.
    """
    cycle = pdca.add_policy(request.cycle_id, request.policy)
    return pdca.get_cycle_status(request.cycle_id)


@router.post("/pdca/action")
async def add_pdca_action(request: PDCAActionRequest):
    """
    Add a corrective action or improvement to a PDCA cycle.
    
    ACT phase.
    """
    cycle = pdca.add_action(
        cycle_id=request.cycle_id,
        action_type=request.action_type,
        description=request.description,
        assigned_to=request.assigned_to
    )
    
    return pdca.get_cycle_status(request.cycle_id)


@router.get("/pdca/cycle/{cycle_id}")
async def get_pdca_cycle(cycle_id: str):
    """
    Get status of a PDCA cycle.
    
    Returns current phase and progress.
    """
    return pdca.get_cycle_status(cycle_id)


@router.get("/pdca/cycles")
async def get_all_pdca_cycles(user_id: Optional[str] = None):
    """
    Get all PDCA cycles, optionally filtered by user.
    """
    return {
        "cycles": pdca.get_all_cycles(user_id),
        "total_cycles": len(pdca.get_all_cycles(user_id))
    }


# ============================================================================
# Blockchain - Audit & Compliance Endpoints
# ============================================================================

@router.get("/blockchain/stats")
async def get_blockchain_stats():
    """
    Get blockchain statistics.
    
    Shows total blocks, verifications, and chain validity.
    """
    return blockchain.get_chain_stats()


@router.post("/blockchain/mine")
async def mine_blockchain():
    """
    Manually trigger blockchain mining.
    
    Mines all pending verifications into a new block.
    """
    block = blockchain.mine_pending_verifications()
    
    if not block:
        return {"message": "No pending verifications to mine"}
    
    return {
        "message": "Block mined successfully",
        "block": block.to_dict()
    }


@router.get("/blockchain/export")
async def export_blockchain():
    """
    Export complete blockchain for compliance audits.
    
    Returns entire immutable audit trail.
    """
    return {
        "blockchain": blockchain.export_chain(),
        "stats": blockchain.get_chain_stats(),
        "exported_at": datetime.utcnow().isoformat()
    }


@router.get("/blockchain/validate")
async def validate_blockchain():
    """
    Validate blockchain integrity.
    
    Checks all blocks and hashes for tampering.
    """
    is_valid = blockchain.is_chain_valid()
    
    return {
        "valid": is_valid,
        "total_blocks": len(blockchain.chain),
        "message": "Blockchain is valid" if is_valid else "Blockchain has been tampered with",
        "validated_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# System Status & Health Endpoints
# ============================================================================

@router.get("/status")
async def get_system_status():
    """
    Get overall system status.
    
    Returns health check for all components.
    """
    return {
        "status": "operational",
        "version": "1.0.0",
        "components": {
            "council_of_32_ais": {
                "status": "operational",
                "total_categories": len(council.council_members),
                "parallel_processing": council.parallel
            },
            "rlmai": {
                "status": "operational",
                "total_feedback": len(rlmai.feedback.feedback_log),
                "active_training_jobs": sum(
                    1 for job in rlmai.trainer.training_jobs.values()
                    if job["status"] in ["PENDING", "TRAINING"]
                )
            },
            "pdca": {
                "status": "operational",
                "total_cycles": len(pdca.cycles)
            },
            "blockchain": {
                "status": "operational",
                "total_blocks": len(blockchain.chain),
                "pending_verifications": len(blockchain.pending_verifications),
                "chain_valid": blockchain.is_chain_valid()
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
