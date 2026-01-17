# FishVault - Secrets Manager

Identity-themed secrets manager built with Next.js 14+ App Router. Secrets are encrypted via Fish KMS and never stored in plaintext.

## Prerequisites

- Node.js 18+ and npm
- Supabase account and project
- Fish KMS server running (see note below)

## Database Setup

Run the following SQL in your Supabase SQL Editor to create the required tables:

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

-- Optional: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_secrets_owner_id ON secrets(owner_id);
CREATE INDEX IF NOT EXISTS idx_sessions_owner_id ON sessions(owner_id);
```

**Note:** For this hackathon MVP, Row Level Security (RLS) is disabled. In production, you should enable RLS with appropriate policies.

## Installation

1. Clone the repository and navigate to the project directory.

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file in the root directory with the following variables:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   FISH_KMS_URL=http://localhost:8000
   FISH_KMS_API_KEY=dev_secret
   UNLOCK_WINDOW_MINUTES=10
   ```

   - `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL (found in Project Settings > API)
   - `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key (found in Project Settings > API, keep this secret!)
   - `FISH_KMS_URL`: URL of your Fish KMS server (default: http://localhost:8000)
   - `FISH_KMS_API_KEY`: API key for Fish KMS authentication
   - `UNLOCK_WINDOW_MINUTES`: Duration of unlock window in minutes (default: 10)

## Running the Application

1. **Ensure Fish KMS is running** at the URL specified in `FISH_KMS_URL` (default: http://localhost:8000)

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. **Login**: Enter your email address on the login page. A user account will be created automatically if it doesn't exist.

2. **Unlock Vault**: Click "Unlock Vault" to unlock your vault for 10 minutes (configurable via `UNLOCK_WINDOW_MINUTES`).

3. **Create Secrets**: Once unlocked, you can add new secrets with a title and value. Secrets are encrypted via Fish KMS before being stored.

4. **View Secrets**: Click "View" on any secret to decrypt and display it. You can copy the decrypted value to your clipboard.

5. **Lock Vault**: Click "Lock Now" to immediately lock your vault.

## Architecture

- **Frontend**: Next.js 14+ App Router with React Server Components and Client Components
- **Backend**: Next.js API Routes (server-side only)
- **Database**: Supabase Postgres
- **Encryption**: Fish KMS (external service)
- **Authentication**: Simple cookie-based auth (MVP-level)

## Important Notes

- **Fish KMS must be running** before using the application. The app will fail to encrypt/decrypt secrets if Fish KMS is unavailable.
- Secrets are never stored in plaintext in the database.
- The unlock window expires after the configured duration. Users must unlock again to create or view secrets.
- This is an MVP implementation. For production use, consider:
  - Enabling Supabase RLS
  - Implementing proper authentication (e.g., Supabase Auth)
  - Adding rate limiting
  - Implementing audit logging
  - Adding backup/recovery mechanisms

## Project Structure

```
fishvault/
├── app/
│   ├── api/              # API routes
│   │   ├── auth/
│   │   ├── session/
│   │   └── secrets/
│   ├── login/            # Login page
│   ├── vault/            # Vault page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Root page (redirects)
│   └── globals.css       # Global styles
├── components/            # React components
│   ├── SecretModal.tsx
│   └── StatusChip.tsx
├── lib/                   # Utility libraries
│   ├── supabaseAdmin.ts  # Supabase admin client
│   ├── auth.ts           # Cookie helpers
│   ├── fishkms.ts        # Fish KMS client
│   └── session.ts        # Session management
└── README.md
```

## API Routes

- `POST /api/auth/login` - Login/create user
- `POST /api/session/unlock` - Unlock vault
- `POST /api/session/lock` - Lock vault
- `GET /api/session/status` - Get unlock status
- `GET /api/secrets/list` - List all secrets for user
- `POST /api/secrets/create` - Create new secret
- `POST /api/secrets/decrypt` - Decrypt and view secret

