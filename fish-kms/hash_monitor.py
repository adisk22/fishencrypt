"""
Live hash monitor - Shows entropy hash updating in real-time from camera motion.
Useful for verifying that motion detection is working and generating different hashes.
"""

import cv2
import time
from vision import capture_frames, compute_motion_entropy
from entropy import generate_entropy_camera


def monitor_hash_live(camera_index: int = 0, update_interval: float = 1.0):
    """
    Monitor and display entropy hash updating in real-time.
    
    Args:
        camera_index: Camera device index
        update_interval: Seconds between hash updates
    """
    print("=" * 70)
    print("Fish KMS - Live Hash Monitor")
    print("=" * 70)
    print(f"Camera: {camera_index}")
    print(f"Update interval: {update_interval} seconds")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    previous_hash = None
    hash_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Generate entropy from camera
            entropy_bytes, status, motion_score = generate_entropy_camera(camera_index)
            
            # Convert to hex for display
            hash_hex = entropy_bytes.hex()
            hash_short = hash_hex[:32]  # First 32 chars (16 bytes)
            hash_full = hash_hex  # Full hash
            
            # Check if hash changed
            hash_changed = (previous_hash != hash_hex)
            previous_hash = hash_hex
            
            # Calculate stats
            hash_count += 1
            elapsed = time.time() - start_time
            hashes_per_sec = hash_count / elapsed if elapsed > 0 else 0
            
            # Clear screen (works on most terminals)
            print("\033[2J\033[H", end="")  # ANSI escape codes to clear screen
            
            # Display header
            print("=" * 70)
            print("Fish KMS - Live Hash Monitor")
            print("=" * 70)
            print(f"Camera: {camera_index} | Status: {status:4s} | Motion: {motion_score:6.2f}")
            print(f"Updates: {hash_count} | Elapsed: {elapsed:6.1f}s | Rate: {hashes_per_sec:.2f} hashes/sec")
            print("=" * 70)
            print()
            
            # Display hash
            print("ENTROPY HASH (Full):")
            print("-" * 70)
            print(hash_full)
            print()
            
            print("ENTROPY HASH (Short - First 32 chars):")
            print("-" * 70)
            print(hash_short + "...")
            print()
            
            # Show hash bytes in different formats
            print("HASH BYTES (First 16 bytes):")
            print("-" * 70)
            first_16 = entropy_bytes[:16]
            print(f"Hex:     {first_16.hex()}")
            print(f"Decimal: {', '.join(str(b) for b in first_16)}")
            print()
            
            # Show change indicator
            if hash_changed:
                change_indicator = "✓ CHANGED" if hash_count > 1 else "Initial"
                print(f"Status: {change_indicator:20s} | Hash is updating!")
            else:
                print(f"Status: {'⚠ UNCHANGED':20s} | Same hash as previous")
            
            print()
            print("=" * 70)
            print("Press Ctrl+C to stop")
            print("=" * 70)
            
            # Wait before next update
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Monitoring stopped")
        print(f"Total hashes generated: {hash_count}")
        print(f"Total time: {elapsed:.1f} seconds")
        print(f"Average rate: {hashes_per_sec:.2f} hashes/second")
        print("=" * 70)


def compare_hashes(camera_index: int = 0, num_samples: int = 10):
    """
    Capture multiple hash samples and compare them to verify uniqueness.
    
    Args:
        camera_index: Camera device index
        num_samples: Number of hash samples to capture
    """
    print("=" * 70)
    print("Fish KMS - Hash Comparison Test")
    print("=" * 70)
    print(f"Camera: {camera_index}")
    print(f"Capturing {num_samples} hash samples...")
    print("=" * 70)
    print()
    
    hashes = []
    motion_scores = []
    
    for i in range(num_samples):
        print(f"Capturing sample {i+1}/{num_samples}...", end=" ", flush=True)
        
        entropy_bytes, status, motion_score = generate_entropy_camera(camera_index)
        hash_hex = entropy_bytes.hex()
        
        hashes.append(hash_hex)
        motion_scores.append(motion_score)
        
        print(f"✓ Motion: {motion_score:.2f}, Status: {status}")
        time.sleep(0.5)  # Small delay between samples
    
    print()
    print("=" * 70)
    print("HASH COMPARISON RESULTS")
    print("=" * 70)
    print()
    
    # Check for uniqueness
    unique_hashes = len(set(hashes))
    print(f"Unique hashes: {unique_hashes}/{num_samples}")
    print(f"Motion scores: min={min(motion_scores):.2f}, max={max(motion_scores):.2f}, avg={sum(motion_scores)/len(motion_scores):.2f}")
    print()
    
    if unique_hashes == num_samples:
        print("✓ SUCCESS: All hashes are unique! Motion detection is working.")
    elif unique_hashes > num_samples * 0.5:
        print("⚠ PARTIAL: Some hashes are unique. Motion may be minimal.")
    else:
        print("✗ WARNING: Many duplicate hashes. Motion may not be detected.")
    
    print()
    print("Hash samples (first 32 chars):")
    print("-" * 70)
    for i, hash_hex in enumerate(hashes):
        print(f"{i+1:2d}. {hash_hex[:32]}... (motion: {motion_scores[i]:.2f})")
    
    print()
    print("=" * 70)


def main():
    """Main entry point."""
    import sys
    
    camera_index = 0
    mode = "live"
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            mode = "compare"
            if len(sys.argv) > 2:
                try:
                    num_samples = int(sys.argv[2])
                except ValueError:
                    num_samples = 10
            else:
                num_samples = 10
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Fish KMS Hash Monitor")
            print()
            print("Usage:")
            print("  python hash_monitor.py              # Live monitoring (default)")
            print("  python hash_monitor.py <camera>     # Use specific camera")
            print("  python hash_monitor.py --compare    # Compare multiple hashes")
            print("  python hash_monitor.py --compare 20 # Compare 20 hashes")
            print()
            return
        else:
            try:
                camera_index = int(sys.argv[1])
            except ValueError:
                print(f"Invalid camera index: {sys.argv[1]}")
                return
    
    if mode == "compare":
        compare_hashes(camera_index, num_samples)
    else:
        # Live monitoring
        update_interval = 1.0  # Update every second
        monitor_hash_live(camera_index, update_interval)


if __name__ == "__main__":
    main()

