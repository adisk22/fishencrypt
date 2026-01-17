# FishVault Setup Checklist

Quick checklist to verify your setup is complete.

## Pre-Setup
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.10+ installed (`python --version`)
- [ ] Supabase account created
- [ ] Webcam available (optional - has fallback)

## Supabase Setup
- [ ] Supabase project created
- [ ] SQL schema executed (users, secrets, sessions tables)
- [ ] Project URL copied
- [ ] Service role key copied

## Fish KMS Server (Part B)
- [ ] Navigated to `fish-kms/` directory
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created in `fish-kms/` with:
  - [ ] `FISH_KMS_API_KEY=dev_secret`
  - [ ] `FISH_KMS_PORT=8000`
  - [ ] `ENTROPY_MODE=camera` (or `demo`)
- [ ] Server starts successfully (`uvicorn server:app --host 0.0.0.0 --port 8000`)
- [ ] Health endpoint works (`http://localhost:8000/health`)

## Next.js App (Part A)
- [ ] In project root directory
- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` file created with:
  - [ ] `NEXT_PUBLIC_SUPABASE_URL` (from Supabase)
  - [ ] `SUPABASE_SERVICE_ROLE_KEY` (from Supabase)
  - [ ] `FISH_KMS_URL=http://localhost:8000`
  - [ ] `FISH_KMS_API_KEY=dev_secret` (matches Fish KMS)
- [ ] Dev server starts (`npm run dev`)

## Integration Test
- [ ] Both services running simultaneously
- [ ] Can access `http://localhost:3000`
- [ ] Login page loads
- [ ] Can login with email
- [ ] Vault page loads after login
- [ ] Can unlock vault (button works)
- [ ] Can create a secret
- [ ] Can view/decrypt a secret
- [ ] Fish KMS logs show operations

## Troubleshooting
If any step fails, check:
- [ ] All environment variables are set correctly
- [ ] API keys match between services
- [ ] Database tables exist in Supabase
- [ ] Ports 3000 and 8000 are not in use
- [ ] Virtual environment is activated for Fish KMS

---

**All checked?** You're ready to demo! 🐟🔐

