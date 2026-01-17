# Motion Detection Sensitivity Improvements

## Changes Made

The motion detection has been made **much more sensitive** to detect fish movement. Here's what was changed:

### 1. Lowered Motion Thresholds

**Before:**
- LIVE threshold: 3.0
- LOW threshold: 0.5
- Background subtraction threshold: 25
- Contour area filter: 100 pixels

**After:**
- LIVE threshold: **1.0** (3x more sensitive)
- LOW threshold: **0.1** (5x more sensitive)
- Background subtraction threshold: **10** (2.5x more sensitive)
- Contour area filter: **30 pixels** (3x more sensitive)

### 2. Improved Motion Detection Algorithm

- **Smaller blur kernel**: Changed from (5,5) to (3,3) to preserve fine motion details
- **Motion enhancement**: Multiplies differences by 1.3-1.5x to amplify small movements
- **Better scoring**: Now includes max motion value to catch brief movements
- **Slower background adaptation**: Changed from 0.5 to 0.3 to detect slow-moving fish

### 3. Enhanced Frame Processing

- **Longer delays**: Minimum 150ms between frames to ensure motion is captured
- **Better exposure**: Attempts to set manual exposure for consistency
- **Reduced warm-up frames**: Faster to start detecting

## What This Means

The system should now detect:
- ✅ **Slow-moving fish** (previously missed)
- ✅ **Small fish movements** (fins, tails)
- ✅ **Subtle water movement** (ripples, bubbles)
- ✅ **Any pixel-level changes** (much more sensitive)

## Testing

Run the debug tool to see the improvements:

```bash
python debug_camera.py
```

You should now see:
- Higher motion scores when fish move
- More green circles (motion regions detected)
- "LIVE" status more often
- Better detection of slow movements

## If Still Not Sensitive Enough

If fish movement is still not being detected, you can:

1. **Lower thresholds further** in `entropy.py`:
   ```python
   live_threshold = 0.5  # Even more sensitive
   low_threshold = 0.05
   ```

2. **Reduce blur more** in `vision.py`:
   ```python
   blurred_frames = [cv2.GaussianBlur(frame, (1, 1), 0) for frame in frames]  # Minimal blur
   ```

3. **Increase motion enhancement** in `vision.py`:
   ```python
   diff_enhanced = cv2.multiply(diff, 2.0)  # Double the differences
   ```

4. **Check camera quality**: Poor lighting or low resolution can affect detection

## Status Indicators

- **LIVE** (green): Motion score > 1.0 - Fish clearly moving
- **LOW** (orange): Motion score > 0.1 - Minimal motion detected
- **NO MOTION** (red): Motion score < 0.1 - No movement detected

Even "LOW" status will work for unlocking - the system is very permissive now!

