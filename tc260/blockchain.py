"""
Blockchain Logging System
Immutable audit trail for AI safety verifications.
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime


class Block:
    """
    A single block in the blockchain.
    """
    
    def __init__(
        self,
        index: int,
        timestamp: float,
        data: Dict[str, Any],
        previous_hash: str
    ):
        """Initialize a block"""
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the hash of this block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2):
        """
        Mine the block (Proof of Work).
        
        Args:
            difficulty: Number of leading zeros required in hash
        """
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }


class VerificationBlockchain:
    """
    Blockchain for storing AI safety verification records.
    Provides immutable audit trail for compliance.
    """
    
    def __init__(self, difficulty: int = 2):
        """
        Initialize blockchain.
        
        Args:
            difficulty: Mining difficulty (number of leading zeros)
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_verifications: List[Dict[str, Any]] = []
        
        # Create genesis block
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data={
                "type": "GENESIS",
                "message": "Council of AI - EU260 Safety Verification Blockchain",
                "created_at": datetime.utcnow().isoformat()
            },
            previous_hash="0"
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_verification(
        self,
        verification_id: str,
        content_hash: str,
        verification_result: Dict[str, Any],
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a verification to pending verifications.
        
        Args:
            verification_id: Unique verification ID
            content_hash: SHA256 hash of the content verified
            verification_result: Result from Council of 32 AIs
            user_id: User who requested verification
            metadata: Optional additional metadata
        
        Returns:
            Pending verification record
        """
        verification_record = {
            "verification_id": verification_id,
            "content_hash": content_hash,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_vote": verification_result.get("overall_vote"),
            "overall_risk_score": verification_result.get("overall_risk_score"),
            "overall_confidence": verification_result.get("overall_confidence"),
            "categories_tested": len(verification_result.get("votes", {})),
            "metadata": metadata or {}
        }
        
        self.pending_verifications.append(verification_record)
        
        return verification_record
    
    def mine_pending_verifications(self) -> Optional[Block]:
        """
        Mine a new block containing all pending verifications.
        
        Returns:
            The newly mined block, or None if no pending verifications
        """
        if not self.pending_verifications:
            return None
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data={
                "type": "VERIFICATIONS",
                "verifications": self.pending_verifications,
                "count": len(self.pending_verifications)
            },
            previous_hash=self.get_latest_block().hash
        )
        
        # Mine the block
        new_block.mine_block(self.difficulty)
        
        # Add to chain
        self.chain.append(new_block)
        
        # Clear pending verifications
        self.pending_verifications = []
        
        return new_block
    
    def add_feedback(
        self,
        feedback_id: str,
        verification_id: str,
        feedback_type: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Block:
        """
        Add human feedback to the blockchain.
        
        Args:
            feedback_id: Unique feedback ID
            verification_id: ID of the verification being reviewed
            feedback_type: Type of feedback (CORRECT, INCORRECT, etc.)
            user_id: User providing feedback
            metadata: Optional additional metadata
        
        Returns:
            The newly mined block
        """
        feedback_record = {
            "feedback_id": feedback_id,
            "verification_id": verification_id,
            "feedback_type": feedback_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Create and mine block immediately for feedback
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data={
                "type": "FEEDBACK",
                "feedback": feedback_record
            },
            previous_hash=self.get_latest_block().hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
        return new_block
    
    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain.
        
        Returns:
            True if blockchain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Check if block was properly mined
            if not current_block.hash.startswith("0" * self.difficulty):
                return False
        
        return True
    
    def get_verification_history(self, verification_id: str) -> List[Dict[str, Any]]:
        """
        Get complete history of a verification from the blockchain.
        
        Args:
            verification_id: Verification ID to search for
        
        Returns:
            List of all blockchain records related to this verification
        """
        history = []
        
        for block in self.chain:
            # Check verifications
            if block.data.get("type") == "VERIFICATIONS":
                for verification in block.data.get("verifications", []):
                    if verification.get("verification_id") == verification_id:
                        history.append({
                            "block_index": block.index,
                            "block_hash": block.hash,
                            "timestamp": block.timestamp,
                            "type": "VERIFICATION",
                            "data": verification
                        })
            
            # Check feedback
            elif block.data.get("type") == "FEEDBACK":
                feedback = block.data.get("feedback", {})
                if feedback.get("verification_id") == verification_id:
                    history.append({
                        "block_index": block.index,
                        "block_hash": block.hash,
                        "timestamp": block.timestamp,
                        "type": "FEEDBACK",
                        "data": feedback
                    })
        
        return history
    
    def get_user_verifications(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all verifications by a specific user.
        
        Args:
            user_id: User ID to search for
        
        Returns:
            List of verifications by this user
        """
        verifications = []
        
        for block in self.chain:
            if block.data.get("type") == "VERIFICATIONS":
                for verification in block.data.get("verifications", []):
                    if verification.get("user_id") == user_id:
                        verifications.append({
                            "block_index": block.index,
                            "block_hash": block.hash,
                            "timestamp": block.timestamp,
                            "verification": verification
                        })
        
        return verifications
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """
        Export the entire blockchain.
        
        Returns:
            List of all blocks as dictionaries
        """
        return [block.to_dict() for block in self.chain]
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the blockchain.
        
        Returns:
            Chain statistics
        """
        total_verifications = 0
        total_feedback = 0
        
        for block in self.chain[1:]:  # Skip genesis block
            if block.data.get("type") == "VERIFICATIONS":
                total_verifications += block.data.get("count", 0)
            elif block.data.get("type") == "FEEDBACK":
                total_feedback += 1
        
        return {
            "total_blocks": len(self.chain),
            "total_verifications": total_verifications,
            "total_feedback": total_feedback,
            "pending_verifications": len(self.pending_verifications),
            "chain_valid": self.is_chain_valid(),
            "difficulty": self.difficulty,
            "latest_block_hash": self.get_latest_block().hash,
            "created_at": self.chain[0].data.get("created_at")
        }
