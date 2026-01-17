# Hash Monitor - Verify Entropy is Changing

## Overview

The `hash_monitor.py` tool displays the entropy hash updating in real-time, allowing you to verify that:
- Motion detection is working
- The hash is actually changing when fish move
- Different motion generates different hashes

## Usage

### Live Hash Monitoring (Recommended)

Watch the hash update in real-time:

```bash
python hash_monitor.py
```

This will:
- Show the full entropy hash (64 hex characters)
- Display hash updates every second
- Show motion score and status
- Indicate when the hash changes

**Example output:**
```
======================================================================
Fish KMS - Live Hash Monitor
======================================================================
Camera: 0 | Status: LIVE | Motion:  12.45
Updates: 15 | Elapsed:  15.0s | Rate: 1.00 hashes/sec
======================================================================

ENTROPY HASH (Full):
----------------------------------------------------------------------
a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2

ENTROPY HASH (Short - First 32 chars):
----------------------------------------------------------------------
a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5...

HASH BYTES (First 16 bytes):
----------------------------------------------------------------------
Hex:     a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5
Decimal: 163, 242, 177, 196, 213, 230, 247, 168, 185, 192, 209, 226, 243, 164, 181

Status: ✓ CHANGED            | Hash is updating!
```

### Compare Multiple Hashes

Test if hashes are unique across multiple samples:

```bash
python hash_monitor.py --compare
```

Or specify number of samples:

```bash
python hash_monitor.py --compare 20
```

This will:
- Capture multiple hash samples
- Compare them for uniqueness
- Show statistics (min/max/avg motion scores)
- Display all hash samples

**Example output:**
```
======================================================================
HASH COMPARISON RESULTS
======================================================================

Unique hashes: 18/20
Motion scores: min=2.15, max=15.32, avg=8.45

✓ SUCCESS: All hashes are unique! Motion detection is working.

Hash samples (first 32 chars):
----------------------------------------------------------------------
 1. a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5... (motion: 12.45)
 2. b4e3c2d1f0e9d8c7b6a5f4e3d2c1b0... (motion: 8.32)
 3. c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1... (motion: 15.23)
...
```

### Use Specific Camera

```bash
python hash_monitor.py 1  # Use camera 1
```

## What to Look For

### ✓ Good Signs

1. **Hash is changing**: Status shows "✓ CHANGED" frequently
2. **Different hashes**: Each update shows a different hash value
3. **Motion score > 0**: Shows motion is being detected
4. **Status = LIVE**: Fish movement is being captured

### ⚠ Warning Signs

1. **Hash not changing**: Status shows "⚠ UNCHANGED" repeatedly
   - **Fix**: Check if fish are actually moving, or increase sensitivity

2. **Motion score = 0**: No motion detected
   - **Fix**: Verify camera is pointing at fish tank, check lighting

3. **Same hash multiple times**: Hash comparison shows duplicates
   - **Fix**: Fish may be too still, or camera not capturing motion

## Integration with Debug Tool

The debug tool (`debug_camera.py`) also shows hash when you press `s`:

```bash
python debug_camera.py
# Press 's' to see current hash
```

## Understanding the Hash

- **Full hash**: 64 hex characters (32 bytes) - SHA-256 output
- **Changes with motion**: Different motion patterns = different hashes
- **Deterministic**: Same motion pattern = same hash (but fish movement is random)
- **Used for encryption**: This hash is used to gate unlock operations

## Troubleshooting

### Hash Never Changes

1. **Check motion detection**: Run `python debug_camera.py` to see if motion is detected
2. **Verify camera**: Make sure camera is pointing at fish tank
3. **Check fish movement**: Fish need to be moving for hash to change
4. **Increase sensitivity**: See `SENSITIVITY_IMPROVEMENTS.md`

### Hash Changes Too Slowly

- This is normal if fish are slow-moving
- Hash should change at least once every few seconds
- If motion score is > 0, it's working correctly

### Want Faster Updates

Edit `hash_monitor.py` and change:
```python
update_interval = 0.5  # Update every 0.5 seconds instead of 1.0
```

## Quick Test

Run this to quickly verify everything works:

```bash
# 1. Check hash is updating
python hash_monitor.py

# 2. In another terminal, compare 10 samples
python hash_monitor.py --compare 10
```

If hashes are unique and changing, your motion detection is working perfectly! 🎉

