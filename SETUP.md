# FishVault - Complete Setup Guide

This guide will walk you through setting up both parts of the FishVault project:
- **Part A**: Next.js FishVault App (Frontend + Backend API)
- **Part B**: Fish KMS Server (Encryption Service)

## Prerequisites

Before starting, ensure you have:

- **Node.js 18+** and npm installed
- **Python 3.10+** installed
- **Supabase account** (free tier works)
- **Webcam** (optional - server has fallback mode)

## Part 1: Supabase Database Setup

### Step 1.1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in:
   - Project name: `fishvault` (or your choice)
   - Database password: (save this securely)
   - Region: Choose closest to you
4. Wait for project to be created (~2 minutes)

### Step 1.2: Run Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the following SQL:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create secrets table
CREATE TABLE IF NOT EXISTS secrets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid REFERENCES users(id) ON DELETE CASCADE,
  title text NOT NULL,
  ciphertext text NOT NULL,
  nonce text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
  owner_id uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  unlocked_until timestamptz
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_secrets_owner_id ON secrets(owner_id);
CREATE INDEX IF NOT EXISTS idx_sessions_owner_id ON sessions(owner_id);
```

4. Click **Run** (or press Ctrl+Enter)
5. Verify tables were created by going to **Table Editor** - you should see `users`, `secrets`, and `sessions`

### Step 1.3: Get Supabase Credentials

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy the following values (you'll need them later):
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **service_role key** (under "Project API keys" - the `service_role` key, NOT the `anon` key)

⚠️ **Important**: Keep the `service_role` key secret - it has admin access to your database!

## Part 2: Fish KMS Server Setup (Part B)

### Step 2.1: Navigate to Fish KMS Directory

```bash
cd fish-kms
```

### Step 2.2: Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Step 2.3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn
- Cryptography
- OpenCV (for camera)
- Other dependencies

### Step 2.4: Create Environment File

Create a file named `.env` in the `fish-kms` directory:

**Windows (PowerShell):**
```powershell
New-Item -Path .env -ItemType File
```

**macOS/Linux:**
```bash
touch .env
```

Then open `.env` and add:

```env
FISH_KMS_API_KEY=dev_secret
FISH_KMS_PORT=8000
UNLOCK_WINDOW_SECONDS=600
ENTROPY_MODE=camera
CAMERA_INDEX=0
```

**Note**: 
- If you don't have a webcam or want to skip camera setup, set `ENTROPY_MODE=demo`
- The `FISH_KMS_API_KEY` must match what you'll use in the Next.js app

### Step 2.5: Test Fish KMS Server

Start the server:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Or use the convenience script:
- **Windows**: `start.bat`
- **macOS/Linux**: `chmod +x start.sh && ./start.sh`

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2.6: Verify Server is Running

Open a new terminal (keep server running) and test:

```bash
curl http://localhost:8000/health
```

Or visit `http://localhost:8000/health` in your browser.

You should see JSON like:
```json
{
  "ok": true,
  "mode": "camera",
  "entropyStatus": "LIVE",
  "motionScore": 12.5
}
```

If camera isn't available, you'll see `"entropyStatus": "DEMO"` - that's fine!

✅ **Fish KMS Server is ready!** Keep it running in this terminal.

## Part 3: Next.js App Setup (Part A)

### Step 3.1: Navigate to Project Root

Open a **new terminal window** (keep Fish KMS running) and:

```bash
cd ..  # Go back to project root (fishencrypt)
# or navigate to where your Next.js app is
```

### Step 3.2: Install Dependencies

```bash
npm install
```

This will install:
- Next.js 14+
- React
- Supabase client
- Other dependencies

### Step 3.3: Create Environment File

Create a file named `.env.local` in the project root:

**Windows (PowerShell):**
```powershell
New-Item -Path .env.local -ItemType File
```

**macOS/Linux:**
```bash
touch .env.local
```

Then open `.env.local` and add:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
FISH_KMS_URL=http://localhost:8000
FISH_KMS_API_KEY=dev_secret
UNLOCK_WINDOW_MINUTES=10
```

**Replace:**
- `NEXT_PUBLIC_SUPABASE_URL` with your Supabase Project URL from Step 1.3
- `SUPABASE_SERVICE_ROLE_KEY` with your Supabase service_role key from Step 1.3
- `FISH_KMS_API_KEY` must match the one in `fish-kms/.env`

### Step 3.4: Start Next.js Development Server

```bash
npm run dev
```

You should see:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
```

✅ **Next.js App is ready!**

## Part 4: Verify Everything Works

### Step 4.1: Check Both Services

You should now have **two terminals running**:

1. **Terminal 1**: Fish KMS Server on `http://localhost:8000`
2. **Terminal 2**: Next.js App on `http://localhost:3000`

### Step 4.2: Test the Application

1. Open browser to `http://localhost:3000`
2. You should be redirected to `/login`
3. Enter any email address (e.g., `test@example.com`)
4. Click "Continue"
5. You should be redirected to `/vault`

### Step 4.3: Test Full Flow

1. **Unlock Vault**: Click "Unlock Vault" button
   - This calls Fish KMS `/unlock` endpoint
   - Check Terminal 1 (Fish KMS) - you should see unlock logs
   - Status should change to "Unlocked until HH:MM"

2. **Create Secret**: 
   - Click "Add Secret"
   - Enter a title (e.g., "My Password")
   - Enter a secret value (e.g., "secret123")
   - Click "Create Secret"
   - Check Terminal 1 - you should see "Encrypt OK" log

3. **View Secret**:
   - Click "View" on the secret you created
   - Click "Decrypt Secret" in the modal
   - You should see the plaintext
   - Check Terminal 1 - you should see "Decrypt OK" log

## Troubleshooting

### Issue: Fish KMS Server won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
# Activate venv first
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

---

### Issue: Camera not working

**Error**: Camera errors in Fish KMS logs

**Solution**: Set `ENTROPY_MODE=demo` in `fish-kms/.env`:
```env
ENTROPY_MODE=demo
```
Restart the Fish KMS server.

---

### Issue: Next.js can't connect to Supabase

**Error**: `Missing Supabase environment variables`

**Solution**: 
1. Check `.env.local` exists in project root
2. Verify `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
3. Restart Next.js dev server (Ctrl+C, then `npm run dev`)

---

### Issue: Next.js can't connect to Fish KMS

**Error**: `Failed to unlock vault` or connection errors

**Solution**:
1. Verify Fish KMS is running on `http://localhost:8000`
2. Test manually: `curl http://localhost:8000/health`
3. Check `FISH_KMS_URL` in `.env.local` matches Fish KMS port
4. Check `FISH_KMS_API_KEY` matches in both `.env.local` and `fish-kms/.env`

---

### Issue: Database errors

**Error**: `relation "users" does not exist`

**Solution**: 
1. Go to Supabase SQL Editor
2. Re-run the SQL schema from Step 1.2
3. Verify tables exist in Table Editor

---

### Issue: "Vault is locked" when trying to decrypt

**Solution**: 
1. Click "Unlock Vault" first
2. Wait for status to show "Unlocked until..."
3. Then try to decrypt

---

### Issue: Port already in use

**Error**: `Port 3000 is already in use` or `Port 8000 is already in use`

**Solution**: 
- For Next.js: Change port with `npm run dev -- -p 3001`
- For Fish KMS: Change `FISH_KMS_PORT=8001` in `fish-kms/.env` and update `FISH_KMS_URL` in `.env.local`

## Next Steps After Setup

Once everything is working:

1. **Test with multiple users**: Create secrets with different email addresses
2. **Test unlock expiration**: Wait 10 minutes after unlocking, try to decrypt
3. **Test camera entropy**: If using camera mode, move objects in front of camera and check `/health` endpoint
4. **Review logs**: Check both terminal windows for operation logs

## Production Considerations

For production deployment, consider:

1. **Security**:
   - Use strong, unique API keys
   - Enable Supabase Row Level Security (RLS)
   - Encrypt `state.json` in Fish KMS
   - Use HTTPS for all connections

2. **Deployment**:
   - Deploy Next.js to Vercel/Netlify
   - Deploy Fish KMS to a VPS/cloud instance
   - Set up environment variables in deployment platform

3. **Monitoring**:
   - Add logging/monitoring
   - Set up alerts for failures
   - Monitor unlock/encrypt/decrypt operations

## Quick Reference

### Environment Variables Summary

**Fish KMS (`fish-kms/.env`):**
```env
FISH_KMS_API_KEY=dev_secret
FISH_KMS_PORT=8000
UNLOCK_WINDOW_SECONDS=600
ENTROPY_MODE=camera  # or "demo"
CAMERA_INDEX=0
```

**Next.js (`.env.local`):**
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
FISH_KMS_URL=http://localhost:8000
FISH_KMS_API_KEY=dev_secret
UNLOCK_WINDOW_MINUTES=10
```

### Important URLs

- **Next.js App**: http://localhost:3000
- **Fish KMS Server**: http://localhost:8000
- **Fish KMS Health**: http://localhost:8000/health
- **Supabase Dashboard**: https://app.supabase.com

### Key Files

- **Next.js**: `.env.local` (environment variables)
- **Fish KMS**: `fish-kms/.env` (environment variables)
- **Fish KMS State**: `fish-kms/state.json` (created automatically, contains master keys)

---

**You're all set!** 🎉 Both services should now be running and communicating with each other.

