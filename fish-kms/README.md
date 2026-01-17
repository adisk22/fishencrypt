# Fish KMS Server

Centralized encryption authority for FishVault. Provides encryption/decryption services with fish tank entropy gating.

## Overview

The Fish KMS Server is a Python FastAPI service that:
- Provides encryption/decryption services to the Next.js FishVault app
- Uses live fish tank entropy (camera frames/motion) to gate access
- Maintains stable per-owner master keys (never exposed to clients)
- Includes fallback mode if camera-based entropy fails

## Features

- **Fish Tank Entropy**: Uses camera motion detection to generate entropy and gate unlock operations
- **Stable Keys**: Per-owner master keys ensure secrets remain decryptable
- **Unlock Window**: Time-based unlock sessions (default 10 minutes)
- **Fallback Mode**: Demo mode using `os.urandom` if camera is unavailable
- **API Key Auth**: Requires `X-FISH-AUTH` header for all requests

## Prerequisites

- Python 3.10 or higher
- Webcam (optional - falls back to demo mode if unavailable)
- Virtual environment (recommended)

## Installation

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate virtual environment:**
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   FISH_KMS_API_KEY=dev_secret
   FISH_KMS_PORT=8000
   UNLOCK_WINDOW_SECONDS=600
   ENTROPY_MODE=camera
   CAMERA_INDEX=0
   ```

## Running the Server

**Start the server:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Or use the built-in runner:
```bash
python server.py
```

The server will start on `http://localhost:8000` (or the port specified in `.env`).

## Configuration

### Environment Variables

- `FISH_KMS_API_KEY`: API key required in `X-FISH-AUTH` header (default: `dev_secret`)
- `FISH_KMS_PORT`: Server port (default: `8000`)
- `UNLOCK_WINDOW_SECONDS`: Duration of unlock window in seconds (default: `600` = 10 minutes)
- `ENTROPY_MODE`: `camera` or `demo` (default: `camera`)
  - `camera`: Uses webcam for motion-based entropy
  - `demo`: Uses `os.urandom` as fallback
- `CAMERA_INDEX`: Camera device index (default: `0`)

### Fallback Mode

If camera is unavailable or `ENTROPY_MODE=demo`, the server automatically falls back to using `os.urandom` for entropy. This ensures the server always works, even without a webcam.

## API Endpoints

All endpoints require the `X-FISH-AUTH` header with the API key.

### GET /health

Health check endpoint.

**Response:**
```json
{
  "ok": true,
  "mode": "camera",
  "entropyStatus": "LIVE",
  "motionScore": 12.5
}
```

- `mode`: Current entropy mode (`camera` or `demo`)
- `entropyStatus`: `LIVE` (motion detected), `LOW` (minimal motion), or `DEMO` (fallback)
- `motionScore`: Average motion detected (0-255 scale, only in camera mode)

### POST /unlock

Unlock vault for owner using entropy liveness check.

**Request:**
```json
{
  "ownerId": "uuid-string"
}
```

**Response:**
```json
{
  "ok": true,
  "unlockedUntil": "2024-01-01T12:00:00"
}
```

Unlocks the owner for `UNLOCK_WINDOW_SECONDS`. The unlock state is stored in memory.

### POST /encrypt

Encrypt plaintext for owner.

**Request:**
```json
{
  "ownerId": "uuid-string",
  "plaintext": "secret value"
}
```

**Response:**
```json
{
  "ciphertext": "base64-encoded-ciphertext",
  "nonce": "base64-encoded-nonce"
}
```

Uses AES-256-GCM encryption with a stable per-owner master key.

### POST /decrypt

Decrypt ciphertext for owner. **Requires owner to be unlocked.**

**Request:**
```json
{
  "ownerId": "uuid-string",
  "ciphertext": "base64-encoded-ciphertext",
  "nonce": "base64-encoded-nonce"
}
```

**Response:**
```json
{
  "plaintext": "decrypted secret value"
}
```

**Errors:**
- `403`: Vault is locked (owner not unlocked or unlock expired)
- `400`: Decryption failed (invalid ciphertext/nonce)

### GET /status

Get server status (unlocked users count).

**Response:**
```json
{
  "unlockedCount": 2,
  "totalOwners": 5
}
```

## Architecture

### Key Management

- **Stable Master Keys**: Each owner gets a persistent 32-byte master key
- **In-Memory Storage**: Keys stored in memory (optionally persisted to `state.json`)
- **Never Exposed**: Master keys are never returned to clients

### Entropy Generation

**Camera Mode:**
1. Captures 10 frames from webcam
2. Computes frame differences to detect motion
3. Generates entropy bytes from motion data
4. Returns status: `LIVE` (motion > threshold) or `LOW` (motion < threshold)

**Demo Mode:**
- Uses `os.urandom(32)` for entropy
- Always returns status: `DEMO`

### Unlock Window

- Unlock state stored in memory: `ownerId -> unlocked_until_epoch`
- Unlock expires after `UNLOCK_WINDOW_SECONDS`
- Encrypt operations work regardless of unlock status
- Decrypt operations require active unlock

## Security Notes

**For Hackathon/Demo:**
- Master keys stored in plaintext in `state.json` (acceptable for demo)
- API key authentication via header
- All encryption/decryption server-side only

**For Production:**
- Encrypt `state.json` with a master password
- Use stronger API key management
- Add rate limiting
- Implement audit logging
- Consider key rotation policies

## Troubleshooting

**Camera not working:**
- Set `ENTROPY_MODE=demo` in `.env`
- Server will automatically fall back to demo mode if camera unavailable

**Port already in use:**
- Change `FISH_KMS_PORT` in `.env` to a different port
- Update Next.js app's `FISH_KMS_URL` accordingly

**Import errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

## File Structure

```
fish-kms/
├── server.py          # FastAPI main server
├── crypto.py          # AES-GCM encryption/decryption
├── entropy.py         # Entropy generation (camera/demo)
├── vision.py          # Camera/motion detection
├── state.py           # State management (keys, unlock store)
├── requirements.txt   # Python dependencies
├── README.md          # This file
├── .env.example       # Environment variable template
└── state.json         # Persistent state (created at runtime)
```

## Integration with Next.js App

The Next.js FishVault app (Part A) calls this server from its API routes:
- `/api/session/unlock` → calls `POST /unlock`
- `/api/secrets/create` → calls `POST /encrypt`
- `/api/secrets/decrypt` → calls `POST /decrypt`

Ensure the Next.js app's `.env.local` has:
```env
FISH_KMS_URL=http://localhost:8000
FISH_KMS_API_KEY=dev_secret
```

## License

Hackathon project - use as needed.

