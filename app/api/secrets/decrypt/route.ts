import { NextRequest, NextResponse } from 'next/server'
import { getUserId } from '@/lib/auth'
import { checkUnlocked } from '@/lib/session'
import { decryptSecret } from '@/lib/fishkms'
import { supabaseAdmin } from '@/lib/supabaseAdmin'

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId()

    if (!userId) {
      return NextResponse.json(
        { ok: false, error: 'Not authenticated' },
        { status: 401 }
      )
    }

    // Check if vault is unlocked
    const isUnlocked = await checkUnlocked(userId)
    if (!isUnlocked) {
      return NextResponse.json(
        { ok: false, error: 'Vault is locked. Please unlock first.' },
        { status: 403 }
      )
    }

    const { secretId } = await request.json()

    if (!secretId || typeof secretId !== 'string') {
      return NextResponse.json(
        { ok: false, error: 'Secret ID is required' },
        { status: 400 }
      )
    }

    // Fetch secret from database
    const { data: secret, error: fetchError } = await supabaseAdmin
      .from('secrets')
      .select('ciphertext, nonce')
      .eq('id', secretId)
      .eq('owner_id', userId)
      .single()

    if (fetchError || !secret) {
      return NextResponse.json(
        { ok: false, error: 'Secret not found' },
        { status: 404 }
      )
    }

    // Decrypt via Fish KMS
    const { plaintext } = await decryptSecret(
      userId,
      secret.ciphertext,
      secret.nonce
    )

    return NextResponse.json({ ok: true, plaintext })
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    )
  }
}

