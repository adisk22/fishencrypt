"""
Entropy generation for Fish KMS.
Supports camera-based entropy (preferred) and demo fallback mode.
"""

import os
from typing import Tuple
from vision import capture_frames, compute_motion_entropy, check_camera_available


def generate_entropy_camera(camera_index: int = 0) -> Tuple[bytes, str, float]:
    """
    Generate entropy from camera motion detection.
    
    Args:
        camera_index: Camera device index
        
    Returns:
        Tuple of (entropy_bytes, status, motion_score)
        status: "LIVE" if motion above threshold, "LOW" if below
        motion_score: Average motion detected (0-255 scale)
    """
    # Capture frames with 100ms delay between frames to ensure motion is captured
    frames = capture_frames(camera_index, num_frames=10, delay_ms=100)
    
    if frames is None or len(frames) == 0:
        # Camera unavailable, fallback to demo
        return generate_entropy_demo()
    
    entropy_bytes, motion_score = compute_motion_entropy(frames)
    
    # Much more sensitive thresholds for fish movement detection
    # LIVE: any noticeable motion (fish moving)
    # LOW: even minimal motion (still usable for entropy)
    live_threshold = 1.0  # Very sensitive - detects even small movements
    low_threshold = 0.1   # Extremely low - catches any motion
    
    if motion_score >= live_threshold:
        status = "LIVE"
    elif motion_score >= low_threshold:
        status = "LOW"
    else:
        status = "LOW"  # Still use it, but mark as low (even 0.0 is acceptable)
    
    return entropy_bytes, status, motion_score


def generate_entropy_demo() -> Tuple[bytes, str, float]:
    """
    Generate entropy using os.urandom (fallback mode).
    
    Returns:
        Tuple of (entropy_bytes, status, motion_score)
        status: Always "DEMO"
        motion_score: Always 0.0 (not applicable)
    """
    entropy_bytes = os.urandom(32)
    return entropy_bytes, "DEMO", 0.0


def get_entropy(entropy_mode: str, camera_index: int = 0) -> Tuple[bytes, str, float]:
    """
    Get entropy based on configured mode.
    
    Args:
        entropy_mode: "camera" or "demo"
        camera_index: Camera device index (only used in camera mode)
        
    Returns:
        Tuple of (entropy_bytes, status, motion_score)
    """
    if entropy_mode == "camera":
        try:
            if not check_camera_available(camera_index):
                print(f"Camera {camera_index} not available, falling back to demo mode")
                return generate_entropy_demo()
            return generate_entropy_camera(camera_index)
        except Exception as e:
            print(f"Camera entropy failed: {e}, falling back to demo mode")
            return generate_entropy_demo()
    else:
        return generate_entropy_demo()

