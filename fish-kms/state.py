"""
State management for Fish KMS.
Manages master keys and unlock store in memory.
Optionally persists to disk for hackathon demo.
"""

import json
import os
import time
from typing import Dict, Optional
from crypto import generate_master_key


class KMSState:
    """Manages KMS state: master keys and unlock store."""
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize state manager.
        
        Args:
            state_file: Optional path to JSON file for persistence
        """
        self.master_keys: Dict[str, bytes] = {}  # ownerId -> key bytes
        self.unlock_store: Dict[str, float] = {}  # ownerId -> unlocked_until_epoch
        self.state_file = state_file
        
        # Load from disk if file exists
        if state_file and os.path.exists(state_file):
            self.load_from_disk()
    
    def get_or_create_master_key(self, owner_id: str) -> bytes:
        """
        Get existing master key or create a new one for owner.
        
        Args:
            owner_id: Owner UUID string
            
        Returns:
            32-byte master key
        """
        if owner_id not in self.master_keys:
            self.master_keys[owner_id] = generate_master_key()
            self.save_to_disk()
            print(f"Generated new master key for owner {owner_id}")
        return self.master_keys[owner_id]
    
    def is_unlocked(self, owner_id: str) -> bool:
        """
        Check if owner is currently unlocked.
        
        Args:
            owner_id: Owner UUID string
            
        Returns:
            True if unlocked and within time window
        """
        if owner_id not in self.unlock_store:
            return False
        
        unlocked_until = self.unlock_store[owner_id]
        return time.time() < unlocked_until
    
    def unlock(self, owner_id: str, unlock_window_seconds: int) -> float:
        """
        Unlock owner for specified time window.
        
        Args:
            owner_id: Owner UUID string
            unlock_window_seconds: Duration of unlock window
            
        Returns:
            Unix timestamp when unlock expires
        """
        unlocked_until = time.time() + unlock_window_seconds
        self.unlock_store[owner_id] = unlocked_until
        print(f"Unlocked owner {owner_id} until {unlocked_until}")
        return unlocked_until
    
    def get_unlocked_until(self, owner_id: str) -> Optional[float]:
        """Get unlock expiration timestamp for owner, or None if not unlocked."""
        return self.unlock_store.get(owner_id)
    
    def get_unlocked_count(self) -> int:
        """Get count of currently unlocked owners."""
        now = time.time()
        return sum(1 for until in self.unlock_store.values() if until > now)
    
    def save_to_disk(self):
        """Save master keys to disk (plaintext for hackathon demo)."""
        if not self.state_file:
            return
        
        try:
            # Convert bytes to base64 for JSON serialization
            keys_dict = {
                owner_id: key.hex()  # Store as hex string
                for owner_id, key in self.master_keys.items()
            }
            
            data = {
                "master_keys": keys_dict,
                "unlock_store": self.unlock_store
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save state to disk: {e}")
    
    def load_from_disk(self):
        """Load master keys from disk."""
        if not self.state_file or not os.path.exists(self.state_file):
            return
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            # Convert hex strings back to bytes
            keys_dict = data.get("master_keys", {})
            self.master_keys = {
                owner_id: bytes.fromhex(key_hex)
                for owner_id, key_hex in keys_dict.items()
            }
            
            self.unlock_store = data.get("unlock_store", {})
            print(f"Loaded state from {self.state_file}")
        except Exception as e:
            print(f"Failed to load state from disk: {e}")


# Global state instance
_state: Optional[KMSState] = None


def get_state() -> KMSState:
    """Get global state instance."""
    global _state
    if _state is None:
        _state = KMSState(state_file="state.json")
    return _state

