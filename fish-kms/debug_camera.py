"""
Visual debug tool for Fish KMS camera motion detection.
Shows live camera feed with motion tracking, heatmap, and statistics.
"""

import cv2
import numpy as np
import time
from vision import capture_frames, compute_motion_entropy
from typing import Optional, Tuple


class FishMotionTracker:
    """Real-time fish motion tracker with visual feedback."""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.background: Optional[np.ndarray] = None
        self.motion_history = []
        self.frame_count = 0
        
    def initialize(self) -> bool:
        """Initialize camera."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize background for background subtraction
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            # Convert to float32 for accumulateWeighted
            self.background = gray.astype(np.float32)
        
        return True
    
    def detect_motion_regions(self, frame: np.ndarray) -> Tuple[np.ndarray, float, list]:
        """
        Detect motion regions using background subtraction and optical flow.
        
        Returns:
            Tuple of (motion_mask, motion_score, motion_centers)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Use smaller blur kernel for more sensitivity to fine movements
        gray = cv2.GaussianBlur(gray, (9, 9), 0)  # Reduced from (21,21) for more detail
        gray_float = gray.astype(np.float32)  # Convert to float32 for accumulateWeighted
        
        # Initialize background if not set
        if self.background is None:
            self.background = gray_float.copy()
        
        # Background subtraction (convert background back to uint8 for comparison)
        background_uint8 = self.background.astype(np.uint8)
        frame_delta = cv2.absdiff(background_uint8, gray)
        
        # Much lower threshold (10 instead of 25) to detect smaller movements
        # Enhance differences for better sensitivity
        frame_delta_enhanced = cv2.multiply(frame_delta, 1.3)
        frame_delta_enhanced = np.clip(frame_delta_enhanced, 0, 255).astype(np.uint8)
        
        thresh = cv2.threshold(frame_delta_enhanced, 10, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=1)  # Reduced from 2 iterations
        
        # Update background more slowly (0.3 instead of 0.5) to adapt less quickly
        # This helps detect slow-moving fish
        cv2.accumulateWeighted(gray_float, self.background, 0.3)
        
        # Find contours (motion regions)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_centers = []
        for contour in contours:
            # Much lower area threshold (30 instead of 100) to detect smaller movements
            if cv2.contourArea(contour) > 30:  # More sensitive to small fish movements
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    motion_centers.append((cx, cy))
        
        # Calculate motion score - use enhanced delta for more sensitivity
        motion_score = np.mean(frame_delta_enhanced)
        
        return thresh, float(motion_score), motion_centers
    
    def draw_motion_overlay(self, frame: np.ndarray, motion_mask: np.ndarray, 
                           motion_centers: list, motion_score: float) -> np.ndarray:
        """Draw motion visualization overlay on frame."""
        overlay = frame.copy()
        
        # Create colored heatmap from motion mask
        heatmap = cv2.applyColorMap(motion_mask, cv2.COLORMAP_HOT)
        overlay = cv2.addWeighted(overlay, 0.7, heatmap, 0.3, 0)
        
        # Draw motion centers (potential fish locations)
        for cx, cy in motion_centers:
            cv2.circle(overlay, (cx, cy), 10, (0, 255, 0), 2)
            cv2.circle(overlay, (cx, cy), 2, (0, 255, 0), -1)
        
        # Draw motion score and status (updated thresholds for better sensitivity)
        status_color = (0, 255, 0) if motion_score > 1.0 else (0, 165, 255) if motion_score > 0.1 else (0, 0, 255)
        status_text = "LIVE" if motion_score > 1.0 else "LOW" if motion_score > 0.1 else "NO MOTION"
        
        cv2.putText(overlay, f"Motion Score: {motion_score:.2f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(overlay, f"Status: {status_text}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(overlay, f"Motion Regions: {len(motion_centers)}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(overlay, f"Frame: {self.frame_count}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Draw motion history graph
        self.motion_history.append(motion_score)
        if len(self.motion_history) > 100:
            self.motion_history.pop(0)
        
        if len(self.motion_history) > 1:
            graph_height = 60
            graph_width = 200
            graph_x = overlay.shape[1] - graph_width - 10
            graph_y = 10
            
            # Draw graph background
            cv2.rectangle(overlay, (graph_x, graph_y), 
                         (graph_x + graph_width, graph_y + graph_height), (0, 0, 0), -1)
            
            # Normalize motion history for display
            if max(self.motion_history) > 0:
                normalized = [int((h / max(self.motion_history)) * graph_height) 
                             for h in self.motion_history[-graph_width:]]
                
                # Draw graph line
                for i in range(1, len(normalized)):
                    x1 = graph_x + i - 1
                    y1 = graph_y + graph_height - normalized[i-1]
                    x2 = graph_x + i
                    y2 = graph_y + graph_height - normalized[i]
                    cv2.line(overlay, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        return overlay
    
    def run(self):
        """Run the visual debug tool."""
        if not self.initialize():
            print(f"Error: Could not open camera {self.camera_index}")
            return
        
        print("Fish Motion Tracker Started")
        print("Press 'q' to quit, 'r' to reset background, 's' to capture sample")
        print("-" * 50)
        
        last_sample_time = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            self.frame_count += 1
            
            # Detect motion
            motion_mask, motion_score, motion_centers = self.detect_motion_regions(frame)
            
            # Draw overlay
            display_frame = self.draw_motion_overlay(frame, motion_mask, motion_centers, motion_score)
            
            # Show frame
            cv2.imshow("Fish Motion Tracker - Press 'q' to quit", display_frame)
            
            # Show motion mask separately
            cv2.imshow("Motion Mask (White = Motion)", motion_mask)
            
            # Capture sample every 2 seconds for testing
            current_time = time.time()
            if current_time - last_sample_time > 2.0:
                status = 'LIVE' if motion_score > 1.0 else 'LOW' if motion_score > 0.1 else 'NO MOTION'
                print(f"Sample {self.frame_count}: Motion Score = {motion_score:.2f}, "
                      f"Regions = {len(motion_centers)}, Status = {status}")
                last_sample_time = current_time
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Reset background
                ret, frame = self.cap.read()
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.GaussianBlur(gray, (21, 21), 0)
                    self.background = gray.astype(np.float32)  # Convert to float32
                    print("Background reset")
            elif key == ord('s'):
                # Test entropy capture
                print("\nTesting entropy capture...")
                frames = capture_frames(self.camera_index, num_frames=10, delay_ms=100)
                if frames:
                    entropy_bytes, motion_score = compute_motion_entropy(frames)
                    hash_hex = entropy_bytes.hex()
                    print(f"  Captured {len(frames)} frames")
                    print(f"  Motion Score: {motion_score:.2f}")
                    print(f"  Entropy Hash (full): {hash_hex}")
                    print(f"  Entropy Hash (short): {hash_hex[:32]}...")
                    print(f"  Hash Length: {len(hash_hex)} chars ({len(entropy_bytes)} bytes)")
                    status = 'LIVE' if motion_score >= 1.0 else 'LOW' if motion_score >= 0.1 else 'NO MOTION'
                    print(f"  Status: {status}\n")
                else:
                    print("  Failed to capture frames\n")
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("\nFish Motion Tracker stopped.")


def list_cameras():
    """Quick function to list available cameras."""
    from vision import check_camera_available
    
    print("Checking for available cameras...")
    available = []
    for i in range(5):
        if check_camera_available(i):
            available.append(i)
            print(f"  Camera {i}: Available")
        else:
            print(f"  Camera {i}: Not available")
    
    if available:
        print(f"\nAvailable cameras: {', '.join(map(str, available))}")
        print(f"Using camera {available[0]} by default")
        return available[0]
    else:
        print("\nNo cameras found!")
        return None


def main():
    """Main entry point."""
    import sys
    
    camera_index = 0
    
    # Check for --list flag
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_cameras()
        return
    
    # Get camera index from command line or environment
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print(f"Invalid camera index: {sys.argv[1]}")
            print("\nUsage:")
            print("  python debug_camera.py              # Use camera 0")
            print("  python debug_camera.py 1           # Use camera 1")
            print("  python debug_camera.py --list      # List available cameras")
            return
    else:
        # Try to find an available camera
        from vision import check_camera_available
        if not check_camera_available(camera_index):
            print(f"Warning: Camera {camera_index} not available")
            print("Trying to find available camera...")
            found = False
            for i in range(1, 5):
                if check_camera_available(i):
                    camera_index = i
                    found = True
                    print(f"Found camera {i}, using it instead")
                    break
            if not found:
                print("No cameras found! Please check your camera connection.")
                print("\nTo list available cameras, run:")
                print("  python list_cameras.py")
                return
    
    print(f"Using camera {camera_index}")
    print("(Run 'python list_cameras.py' to see all available cameras)")
    print()
    
    tracker = FishMotionTracker(camera_index)
    tracker.run()


if __name__ == "__main__":
    main()

