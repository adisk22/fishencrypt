"""
Utility script to list all available cameras and test them.
"""

import cv2


def list_available_cameras(max_test: int = 5):
    """
    List all available cameras by testing indices 0 to max_test.
    
    Args:
        max_test: Maximum camera index to test (default: 5)
    """
    print("Scanning for available cameras...")
    print("-" * 50)
    
    available_cameras = []
    
    for i in range(max_test):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Try to read a frame to confirm it works
            ret, frame = cap.read()
            if ret:
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps
                })
                
                print(f"✓ Camera {i}: Available")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")
                print()
            else:
                print(f"✗ Camera {i}: Opens but cannot read frames")
        else:
            print(f"✗ Camera {i}: Not available")
        
        if cap.isOpened():
            cap.release()
    
    print("-" * 50)
    if available_cameras:
        print(f"\nFound {len(available_cameras)} available camera(s):")
        for cam in available_cameras:
            print(f"  - Camera {cam['index']} ({cam['width']}x{cam['height']})")
        print("\nTo use a specific camera:")
        print("  - Debug tool: python debug_camera.py <index>")
        print("  - Server: Set CAMERA_INDEX=<index> in .env file")
    else:
        print("\nNo cameras found! Check your camera connection.")
    
    return available_cameras


def test_camera_preview(camera_index: int):
    """
    Open a preview window for the specified camera.
    Press 'q' to quit.
    
    Args:
        camera_index: Camera index to test
    """
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_index}")
        return
    
    print(f"Testing camera {camera_index}")
    print("Press 'q' to quit, 'n' for next camera, 'p' for previous camera")
    
    current_index = camera_index
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Camera {current_index} stopped working")
            break
        
        # Add camera info overlay
        cv2.putText(frame, f"Camera {current_index}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 'n' for next, 'p' for previous", (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow(f"Camera {current_index} Preview", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'):
            # Try next camera
            cap.release()
            current_index += 1
            cap = cv2.VideoCapture(current_index)
            if not cap.isOpened():
                print(f"Camera {current_index} not available")
                current_index -= 1
                cap = cv2.VideoCapture(current_index)
        elif key == ord('p'):
            # Try previous camera
            if current_index > 0:
                cap.release()
                current_index -= 1
                cap = cv2.VideoCapture(current_index)
                if not cap.isOpened():
                    print(f"Camera {current_index} not available")
                    current_index += 1
                    cap = cv2.VideoCapture(current_index)
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Camera {current_index} preview closed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific camera
        try:
            camera_index = int(sys.argv[1])
            test_camera_preview(camera_index)
        except ValueError:
            print(f"Invalid camera index: {sys.argv[1]}")
    else:
        # List all cameras
        cameras = list_available_cameras()
        
        if cameras:
            print("\nWould you like to preview a camera? (y/n): ", end='')
            try:
                response = input().strip().lower()
                if response == 'y':
                    print("Enter camera index to preview: ", end='')
                    index = int(input().strip())
                    if any(cam['index'] == index for cam in cameras):
                        test_camera_preview(index)
                    else:
                        print(f"Camera {index} is not available")
            except (ValueError, KeyboardInterrupt):
                print("\nCancelled")

