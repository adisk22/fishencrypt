# Camera Setup Guide

## Finding the Right Camera

If you have multiple cameras (built-in webcam, external USB camera, etc.), you need to find which camera index corresponds to your fish tank camera.

### Method 1: List All Cameras (Recommended)

Run the camera discovery script:

```bash
```

This will:
- Scan cameras 0-4
- Show which ones are available
- Display their resolution and properties
- Optionally let you preview each camera

### Method 2: Test Cameras with Debug Tool

The debug tool accepts a camera index as an argument:

```bash
# Test camera 0 (default)
python debug_camera.py

# Test camera 1
python debug_camera.py 1

# Test camera 2
python debug_camera.py 2

# List available cameras
python debug_camera.py --list
```

### Method 3: Preview Cameras

Use the list script to preview cameras:

```bash
# List all cameras
python list_cameras.py

# Preview a specific camera
python list_cameras.py 0  # Preview camera 0
python list_cameras.py 1  # Preview camera 1
```

In preview mode:
- Press `q` to quit
- Press `n` for next camera
- Press `p` for previous camera

## Setting Camera for Fish KMS Server

Once you know which camera index to use:

### Option 1: Environment Variable (Recommended)

Edit `fish-kms/.env`:

```env
CAMERA_INDEX=1  # Change to your camera index
```

Then restart the server.

### Option 2: Command Line (Temporary)

You can also set it when starting the server:

**Windows PowerShell:**
```powershell
$env:CAMERA_INDEX=1; python server.py
```

**Windows CMD:**
```cmd
set CAMERA_INDEX=1 && python server.py
```

**macOS/Linux:**
```bash
CAMERA_INDEX=1 python server.py
```

## Common Camera Indices

- **Camera 0**: Usually the default/built-in camera
- **Camera 1**: Usually the first external USB camera
- **Camera 2**: Second external camera, or sometimes a different built-in camera

## Troubleshooting

### "Camera X not available"

1. **Check camera is connected**: Ensure USB camera is plugged in
2. **Check camera permissions**: Some systems require camera permissions
3. **Try different index**: Run `python list_cameras.py` to find available cameras
4. **Check if camera is in use**: Close other apps using the camera (Zoom, Teams, etc.)

### "Wrong camera showing"

1. **List cameras**: Run `python list_cameras.py` to see all available cameras
2. **Test each**: Use `python debug_camera.py 0`, `python debug_camera.py 1`, etc.
3. **Update .env**: Once you find the right one, update `CAMERA_INDEX` in `.env`

### Camera works in preview but not in server

1. **Check .env file**: Make sure `CAMERA_INDEX` is set correctly
2. **Restart server**: Environment variables are loaded at startup
3. **Check logs**: Server will print which camera it's trying to use

## Quick Reference

```bash
# List all cameras
python list_cameras.py

# Test camera 0 with debug tool
python debug_camera.py 0

# Test camera 1 with debug tool
python debug_camera.py 1

# Set camera for server (in .env)
CAMERA_INDEX=1
```

## Example Workflow

1. **Discover cameras**:
   ```bash
   python list_cameras.py
   ```
   Output:
   ```
   ✓ Camera 0: Available (640x480)
   ✗ Camera 1: Not available
   ✓ Camera 2: Available (1920x1080)  # This is your fish tank camera!
   ```

2. **Test the fish tank camera**:
   ```bash
   python debug_camera.py 2
   ```
   Verify you see the fish tank feed.

3. **Update server config**:
   Edit `fish-kms/.env`:
   ```env
   CAMERA_INDEX=2
   ```

4. **Restart server**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

The server will now use camera 2 for motion detection!

