"""
Fish KMS Server - Centralized encryption authority.
Provides encryption/decryption services with fish tank entropy gating.
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from crypto import encrypt_aes_gcm, decrypt_aes_gcm
from entropy import get_entropy
from state import get_state

# Load environment variables
load_dotenv()

# Configuration
FISH_KMS_API_KEY = os.getenv("FISH_KMS_API_KEY", "dev_secret")
FISH_KMS_PORT = int(os.getenv("FISH_KMS_PORT", "8000"))
UNLOCK_WINDOW_SECONDS = int(os.getenv("UNLOCK_WINDOW_SECONDS", "600"))
ENTROPY_MODE = os.getenv("ENTROPY_MODE", "camera")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))

# Initialize FastAPI app
app = FastAPI(title="Fish KMS Server", version="1.0.0")

# Initialize state
state = get_state()


# Request/Response Models
class UnlockRequest(BaseModel):
    ownerId: str


class UnlockResponse(BaseModel):
    ok: bool
    unlockedUntil: Optional[str] = None
    error: Optional[str] = None


class EncryptRequest(BaseModel):
    ownerId: str
    plaintext: str


class EncryptResponse(BaseModel):
    ciphertext: str
    nonce: str


class DecryptRequest(BaseModel):
    ownerId: str
    ciphertext: str
    nonce: str


class DecryptResponse(BaseModel):
    plaintext: str


class HealthResponse(BaseModel):
    ok: bool
    mode: str
    entropyStatus: str
    motionScore: Optional[float] = None


class StatusResponse(BaseModel):
    unlockedCount: int
    totalOwners: int


# Auth middleware helper
def verify_api_key(x_fish_auth: Optional[str] = Header(None)) -> None:
    """Verify X-FISH-AUTH header matches API key."""
    if x_fish_auth != FISH_KMS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint showing server status and entropy mode."""
    entropy_bytes, entropy_status, motion_score = get_entropy(ENTROPY_MODE, CAMERA_INDEX)
    
    return HealthResponse(
        ok=True,
        mode=ENTROPY_MODE,
        entropyStatus=entropy_status,
        motionScore=motion_score if motion_score > 0 else None
    )


@app.post("/unlock", response_model=UnlockResponse)
async def unlock(
    request: UnlockRequest,
    x_fish_auth: Optional[str] = Header(None, alias="X-FISH-AUTH")
):
    """
    Unlock vault for owner using entropy liveness check.
    Stores unlock state for UNLOCK_WINDOW_SECONDS.
    """
    verify_api_key(x_fish_auth)
    
    owner_id = request.ownerId
    
    # Perform entropy check (liveness gate)
    entropy_bytes, entropy_status, motion_score = get_entropy(ENTROPY_MODE, CAMERA_INDEX)
    print(f"Unlock request for {owner_id}: entropy_status={entropy_status}, motion={motion_score:.2f}")
    
    # Unlock owner for configured window
    unlocked_until_epoch = state.unlock(owner_id, UNLOCK_WINDOW_SECONDS)
    unlocked_until_iso = datetime.fromtimestamp(unlocked_until_epoch).isoformat()
    
    print(f"Unlock OK: {owner_id} unlocked until {unlocked_until_iso}")
    
    return UnlockResponse(
        ok=True,
        unlockedUntil=unlocked_until_iso
    )


@app.post("/encrypt", response_model=EncryptResponse)
async def encrypt(
    request: EncryptRequest,
    x_fish_auth: Optional[str] = Header(None, alias="X-FISH-AUTH")
):
    """
    Encrypt plaintext for owner.
    Requires owner to be unlocked (within time window).
    """
    verify_api_key(x_fish_auth)
    
    owner_id = request.ownerId
    plaintext = request.plaintext
    
    # Check if unlocked (optional for encrypt - you can remove this if you want)
    # For now, we'll allow encrypt even if not unlocked (as per requirements)
    # But decrypt will require unlock
    
    # Get or create master key for owner
    master_key = state.get_or_create_master_key(owner_id)
    
    # Encrypt
    ciphertext_b64, nonce_b64 = encrypt_aes_gcm(master_key, plaintext)
    
    print(f"Encrypt OK: {owner_id} encrypted {len(plaintext)} bytes")
    
    return EncryptResponse(
        ciphertext=ciphertext_b64,
        nonce=nonce_b64
    )


@app.post("/decrypt", response_model=DecryptResponse)
async def decrypt(
    request: DecryptRequest,
    x_fish_auth: Optional[str] = Header(None, alias="X-FISH-AUTH")
):
    """
    Decrypt ciphertext for owner.
    Requires owner to be unlocked (within time window).
    """
    verify_api_key(x_fish_auth)
    
    owner_id = request.ownerId
    ciphertext_b64 = request.ciphertext
    nonce_b64 = request.nonce
    
    # Check if unlocked
    if not state.is_unlocked(owner_id):
        raise HTTPException(
            status_code=403,
            detail="Vault is locked. Please unlock first."
        )
    
    # Get master key (must exist if we have secrets)
    master_key = state.get_or_create_master_key(owner_id)
    
    # Decrypt
    try:
        plaintext = decrypt_aes_gcm(master_key, ciphertext_b64, nonce_b64)
        print(f"Decrypt OK: {owner_id} decrypted {len(plaintext)} bytes")
        
        return DecryptResponse(plaintext=plaintext)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {str(e)}")


@app.get("/status", response_model=StatusResponse)
async def status(
    x_fish_auth: Optional[str] = Header(None, alias="X-FISH-AUTH")
):
    """Get server status: unlocked users count."""
    verify_api_key(x_fish_auth)
    
    unlocked_count = state.get_unlocked_count()
    total_owners = len(state.master_keys)
    
    return StatusResponse(
        unlockedCount=unlocked_count,
        totalOwners=total_owners
    )


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Fish KMS Server on port {FISH_KMS_PORT}")
    print(f"Entropy mode: {ENTROPY_MODE}")
    print(f"Unlock window: {UNLOCK_WINDOW_SECONDS} seconds")
    uvicorn.run(app, host="0.0.0.0", port=FISH_KMS_PORT)

