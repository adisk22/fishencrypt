# Installing OpenCV for Fish Motion Tracker

The `debug_camera.py` tool requires OpenCV (cv2). Here's how to install it:

## Quick Install

Make sure you're in the `fish-kms` directory and your virtual environment is activated, then run:

```bash
pip install opencv-python
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Step-by-Step

1. **Activate your virtual environment** (if using one):
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

2. **Navigate to fish-kms directory**:
   ```bash
   cd fish-kms
   ```

3. **Install OpenCV**:
   ```bash
   pip install opencv-python
   ```

   Or install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -c "import cv2; print('OpenCV version:', cv2.__version__)"
   ```

   You should see something like: `OpenCV version: 4.9.0.80`

5. **Run the debug tool**:
   ```bash
   python debug_camera.py
   ```

## Troubleshooting

### If pip install fails:

Try installing without version pinning:
```bash
pip install opencv-python numpy
```

### If you get "No module named 'numpy'":

OpenCV requires numpy:
```bash
pip install numpy opencv-python
```

### If you're not using a virtual environment:

Consider creating one to avoid conflicts:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

