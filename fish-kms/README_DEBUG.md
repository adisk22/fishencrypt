# Fish Motion Tracker - Debug Tool

## Overview

The `debug_camera.py` tool provides a visual interface to see exactly what the Fish KMS server is detecting. It shows:

- **Live camera feed** with motion overlay
- **Motion heatmap** (red = high motion, blue = low motion)
- **Motion regions** (green circles show detected movement areas)
- **Real-time motion score** and status
- **Motion history graph** showing motion over time

## Usage

### Basic Usage

```bash
cd fish-kms
python debug_camera.py
```

### Find Available Cameras

If you're not sure which camera to use:

```bash
# List all available cameras
python list_cameras.py

# Or use the built-in list feature
python debug_camera.py --list
```

### Specify Camera Index

If you have multiple cameras:

```bash
python debug_camera.py 0  # Use camera index 0 (default)
python debug_camera.py 1  # Use camera index 1
python debug_camera.py 2  # Use camera index 2
```

See `CAMERA_SETUP.md` for detailed camera setup instructions.

### Keyboard Controls

- **`q`** - Quit the tracker
- **`r`** - Reset background (useful if lighting changes)
- **`s`** - Capture a sample and test entropy generation

## What You'll See

### Main Window: "Fish Motion Tracker"
- Live camera feed with colored overlay
- Motion regions marked with green circles
- Motion score and status in top-left
- Motion history graph in top-right

### Secondary Window: "Motion Mask"
- Black and white image showing detected motion
- White areas = motion detected
- Black areas = no motion

## Understanding the Display

### Motion Score
- **> 3.0**: Status = "LIVE" (green) - Fish are clearly moving
- **0.5 - 3.0**: Status = "LOW" (orange) - Minimal motion detected
- **< 0.5**: Status = "NO MOTION" (red) - No significant motion

### Motion Regions (Green Circles)
- Each circle represents a detected motion area
- Larger areas = more significant motion
- Multiple circles = multiple moving objects (or parts of fish)

### Motion History Graph
- Shows motion score over the last 100 frames
- Helps identify patterns in fish movement
- Green line = current motion level

## Troubleshooting

### Motion Score Always 0

**Possible causes:**
1. **Camera capturing too fast** - Frames are identical
   - **Solution**: The improved `vision.py` now adds 100ms delays between frames

2. **Lighting too uniform** - No contrast for motion detection
   - **Solution**: Ensure good lighting with some variation

3. **Camera not focused** - Everything is blurry
   - **Solution**: Adjust camera focus

4. **Fish moving too slowly** - Motion below detection threshold
   - **Solution**: The thresholds have been lowered (3.0 for LIVE, 0.5 for LOW)

### Reset Background

If lighting conditions change or camera moves:
- Press **`r`** to reset the background model
- This helps the tracker adapt to new conditions

### Test Entropy Capture

Press **`s`** to test the actual entropy capture process:
- Captures 10 frames with delays (same as KMS server)
- Shows the motion score that would be used
- Displays the generated entropy hash

## Integration with KMS Server

The debug tool uses the same motion detection algorithms as the KMS server:
- Same `capture_frames()` function
- Same `compute_motion_entropy()` function
- Same thresholds and sensitivity

If motion is detected in the debug tool, it should work in the KMS server too.

## Tips for Best Results

1. **Good Lighting**: Ensure the fish tank is well-lit
2. **Stable Camera**: Mount camera securely to avoid shake
3. **Clear View**: Keep camera lens clean
4. **Active Fish**: More active fish = higher motion scores
5. **Reset When Needed**: Press `r` if conditions change

## Example Output

When running, you'll see console output like:

```
Fish Motion Tracker Started
Press 'q' to quit, 'r' to reset background, 's' to capture sample
--------------------------------------------------
Sample 60: Motion Score = 12.45, Regions = 3, Status = LIVE
Sample 120: Motion Score = 8.32, Regions = 2, Status = LIVE
Sample 180: Motion Score = 2.15, Regions = 1, Status = LOW

Testing entropy capture...
  Captured 10 frames
  Motion Score: 15.23
  Entropy: a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6...
  Status: LIVE
```

## Next Steps

Once you see motion being detected in the debug tool:

1. Verify motion score is > 0.5 (preferably > 3.0)
2. Check that green circles appear when fish move
3. Test entropy capture with `s` key
4. If working here, the KMS server should work too!

If motion is still 0 in the debug tool, the issue is with camera/capture, not the KMS server code.

