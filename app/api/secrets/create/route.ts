import { NextRequest, NextResponse } from 'next/server'
import { getUserId } from '@/lib/auth'
import { checkUnlocked } from '@/lib/session'
import { encryptSecret } from '@/lib/fishkms'
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

    const { title, plaintext } = await request.json()

    if (!title || typeof title !== 'string') {
      return NextResponse.json(
        { ok: false, error: 'Title is required' },
        { status: 400 }
      )
    }

    if (!plaintext || typeof plaintext !== 'string') {
      return NextResponse.json(
        { ok: false, error: 'Secret value is required' },
        { status: 400 }
      )
    }

    // Encrypt via Fish KMS
    const { ciphertext, nonce } = await encryptSecret(userId, plaintext)

    // Store in database
    const { error: insertError } = await supabaseAdmin
      .from('secrets')
      .insert({
        owner_id: userId,
        title: title.trim(),
        ciphertext,
        nonce
      })

    if (insertError) {
      return NextResponse.json(
        { ok: false, error: 'Failed to save secret' },
        { status: 500 }
      )
    }

    return NextResponse.json({ ok: true })
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    )
  }
}

