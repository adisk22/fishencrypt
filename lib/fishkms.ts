const FISH_KMS_URL = process.env.FISH_KMS_URL || 'http://localhost:8000'
const FISH_KMS_API_KEY = process.env.FISH_KMS_API_KEY || 'dev_secret'

export interface UnlockResponse {
  ok: boolean
  error?: string
}

export interface EncryptResponse {
  ciphertext: string
  nonce: string
}

export interface DecryptResponse {
  plaintext: string
}

export async function unlockVault(ownerId: string): Promise<UnlockResponse> {
  const response = await fetch(`${FISH_KMS_URL}/unlock`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-FISH-AUTH': FISH_KMS_API_KEY
    },
    body: JSON.stringify({ ownerId })
  })

  if (!response.ok) {
    return { ok: false, error: `HTTP ${response.status}` }
  }

  return await response.json()
}

export async function encryptSecret(
  ownerId: string,
  plaintext: string
): Promise<EncryptResponse> {
  const response = await fetch(`${FISH_KMS_URL}/encrypt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-FISH-AUTH': FISH_KMS_API_KEY
    },
    body: JSON.stringify({ ownerId, plaintext })
  })

  if (!response.ok) {
    throw new Error(`Encrypt failed: HTTP ${response.status}`)
  }

  return await response.json()
}

export async function decryptSecret(
  ownerId: string,
  ciphertext: string,
  nonce: string
): Promise<DecryptResponse> {
  const response = await fetch(`${FISH_KMS_URL}/decrypt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-FISH-AUTH': FISH_KMS_API_KEY
    },
    body: JSON.stringify({ ownerId, ciphertext, nonce })
  })

  if (!response.ok) {
    throw new Error(`Decrypt failed: HTTP ${response.status}`)
  }

  return await response.json()
}

