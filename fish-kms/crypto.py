"""
Cryptography utilities for Fish KMS.
Uses AES-256-GCM for encryption/decryption.
"""

import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend


def generate_master_key() -> bytes:
    """Generate a random 32-byte master key for AES-256."""
    return AESGCM.generate_key(bit_length=256)


def encrypt_aes_gcm(key: bytes, plaintext: str) -> tuple[str, str]:
    """
    Encrypt plaintext using AES-256-GCM.
    
    Args:
        key: 32-byte encryption key
        plaintext: String to encrypt
        
    Returns:
        Tuple of (ciphertext_b64, nonce_b64) as base64 strings
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256")
    
    # Generate 12-byte nonce for GCM (random bytes)
    nonce = os.urandom(12)
    
    # Create cipher and encrypt
    aesgcm = AESGCM(key)
    plaintext_bytes = plaintext.encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
    
    # Return base64-encoded strings
    ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
    nonce_b64 = base64.b64encode(nonce).decode('utf-8')
    
    return ciphertext_b64, nonce_b64


def decrypt_aes_gcm(key: bytes, ciphertext_b64: str, nonce_b64: str) -> str:
    """
    Decrypt ciphertext using AES-256-GCM.
    
    Args:
        key: 32-byte decryption key
        ciphertext_b64: Base64-encoded ciphertext
        nonce_b64: Base64-encoded nonce
        
    Returns:
        Decrypted plaintext string
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256")
    
    # Decode base64
    try:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
    except Exception as e:
        raise ValueError(f"Invalid base64 encoding: {e}")
    
    # Decrypt
    aesgcm = AESGCM(key)
    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")

