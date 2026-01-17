import { NextRequest, NextResponse } from 'next/server'
import { getUserId } from '@/lib/auth'
import { unlockVault } from '@/lib/fishkms'
import { setUnlockedUntil } from '@/lib/session'

const UNLOCK_WINDOW_MINUTES = parseInt(
  process.env.UNLOCK_WINDOW_MINUTES || '10',
  10
)

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId()

    if (!userId) {
      return NextResponse.json(
        { ok: false, error: 'Not authenticated' },
        { status: 401 }
      )
    }

    // Call Fish KMS to unlock
    const unlockResult = await unlockVault(userId)

    if (!unlockResult.ok) {
      return NextResponse.json(
        { ok: false, error: unlockResult.error || 'Unlock failed' },
        { status: 400 }
      )
    }

    // Set unlocked_until to now + window
    const unlockedUntil = new Date()
    unlockedUntil.setMinutes(unlockedUntil.getMinutes() + UNLOCK_WINDOW_MINUTES)

    await setUnlockedUntil(userId, unlockedUntil)

    return NextResponse.json({
      ok: true,
      unlockedUntil: unlockedUntil.toISOString()
    })
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

