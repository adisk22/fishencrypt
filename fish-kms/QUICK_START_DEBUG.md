# Quick Start: Fish Motion Debug Tool

## Run the Debug Tool

```bash
cd fish-kms
python debug_camera.py
```

## What to Look For

1. **Motion Score** (top-left of screen):
   - Should be > 0.5 when fish are moving
   - > 3.0 = "LIVE" (green) = Good!
   - 0.5-3.0 = "LOW" (orange) = Still works
   - < 0.5 = "NO MOTION" (red) = Problem

2. **Green Circles**:
   - Should appear when fish move
   - Each circle = detected motion region

3. **Motion History Graph** (top-right):
   - Green line should fluctuate when fish move
   - Flat line = no motion detected

## If Motion Score is 0

1. **Check camera is working**: You should see live video
2. **Move something in front of camera**: Your hand, a pen, etc.
   - If motion score increases → camera works, fish might be too still
   - If motion score stays 0 → camera/capture issue

3. **Press 'r'** to reset background model

4. **Press 's'** to test entropy capture (same as KMS server uses)

## The Fixes Applied

✅ **Added frame delays** (100ms between frames) - ensures motion is captured
✅ **Improved motion detection** - uses Gaussian blur + thresholding
✅ **Lowered thresholds** - more sensitive (3.0 for LIVE, 0.5 for LOW)
✅ **Background subtraction** - better at detecting moving objects

If motion is still 0 after these fixes, the issue is likely:
- Camera hardware/software problem
- Fish moving too slowly
- Lighting too uniform (no contrast)

