import { NextRequest, NextResponse } from 'next/server'
import { getUserId } from '@/lib/auth'
import { getUnlockedUntil } from '@/lib/session'

export async function GET(request: NextRequest) {
  try {
    const userId = await getUserId()

    if (!userId) {
      return NextResponse.json(
        { ok: false, error: 'Not authenticated' },
        { status: 401 }
      )
    }

    const unlockedUntil = await getUnlockedUntil(userId)

    return NextResponse.json({
      ok: true,
      unlockedUntil: unlockedUntil?.toISOString() || null
    })
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

