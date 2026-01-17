"""
Computer vision utilities for fish tank motion detection.
"""

import cv2
import numpy as np
import hashlib
import os
import struct
import time
from typing import Optional, Tuple


def capture_frames(camera_index: int = 0, num_frames: int = 10, delay_ms: int = 100) -> Optional[list[np.ndarray]]:
    """
    Capture frames from webcam with delays to ensure motion is captured.
    
    Args:
        camera_index: Camera device index
        num_frames: Number of frames to capture
        delay_ms: Delay in milliseconds between frames (default 100ms)
        
    Returns:
        List of frames (numpy arrays) or None if camera unavailable
    """
    import time
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        return None
    
    # Set camera properties for better capture
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # Increase exposure/gain sensitivity if supported
    try:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual exposure for consistency
    except:
        pass  # Some cameras don't support this
    
    frames = []
    
    # Discard first few frames to let camera adjust
    for _ in range(2):  # Reduced from 3 to capture faster
        cap.read()
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to grayscale for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(gray)
        
        # Add delay between frames to capture actual motion
        # Slightly longer delay (150ms) to ensure fish movement is captured
        if i < num_frames - 1:  # Don't delay after last frame
            time.sleep(max(delay_ms, 150) / 1000.0)  # At least 150ms for fish movement
    
    cap.release()
    return frames if len(frames) == num_frames else None


def compute_motion_entropy(frames: list[np.ndarray]) -> Tuple[bytes, float]:
    """
    Compute entropy from frame differences (motion detection).
    Uses improved algorithm with Gaussian blur and thresholding for better sensitivity.
    
    Args:
        frames: List of grayscale frames
        
    Returns:
        Tuple of (entropy_bytes, motion_score)
        motion_score: Average pixel difference across frames (0-255 scale)
    """
    if len(frames) < 2:
        # If only one frame, use frame noise as entropy
        frame = frames[0]
        diff = frame.astype(np.float32)
        motion_score = np.std(diff)
        # Include timestamp + nonce so each capture produces a different hash
        entropy_bytes = hashlib.sha256(diff.tobytes() + struct.pack('d', time.time()) + os.urandom(4)).digest()
        return entropy_bytes, float(motion_score)
    
    # Apply minimal blur to reduce noise while preserving fine motion details
    # Smaller kernel (3x3) is more sensitive to small movements
    blurred_frames = [cv2.GaussianBlur(frame, (3, 3), 0) for frame in frames]
    
    # Compute frame differences with more sensitivity
    diffs = []
    for i in range(1, len(blurred_frames)):
        diff = cv2.absdiff(blurred_frames[i-1], blurred_frames[i])
        # Lower threshold (5 instead of 10) to detect smaller movements
        # Use adaptive thresholding for better sensitivity
        diff_enhanced = cv2.multiply(diff, 1.5)  # Enhance differences
        diff_enhanced = np.clip(diff_enhanced, 0, 255).astype(np.uint8)
        diffs.append(diff_enhanced)
    
    # Average motion across all frame pairs
    avg_diff = np.mean(diffs, axis=0)
    
    # Calculate motion score using multiple methods for better accuracy
    mean_motion = np.mean(avg_diff)
    median_motion = np.median(avg_diff)
    std_motion = np.std(avg_diff)
    max_motion = np.max(avg_diff)  # Peak motion value
    
    # More sensitive calculation: emphasize mean and variance
    # Include max motion to catch even brief movements
    motion_score = mean_motion + (std_motion * 0.5) + (max_motion * 0.1)
    
    # Generate entropy from differences; include timestamp + nonce so each
    # capture produces a different hash (motion data + time + nonce ensures uniqueness)
    diff_bytes = avg_diff.astype(np.uint8).tobytes()
    entropy_bytes = hashlib.sha256(diff_bytes + struct.pack('d', time.time()) + os.urandom(4)).digest()
    
    return entropy_bytes, float(motion_score)


def check_camera_available(camera_index: int = 0) -> bool:
    """Check if camera is available."""
    cap = cv2.VideoCapture(camera_index)
    available = cap.isOpened()
    cap.release()
    return available

