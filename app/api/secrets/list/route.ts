import { NextRequest, NextResponse } from 'next/server'
import { getUserId } from '@/lib/auth'
import { supabaseAdmin } from '@/lib/supabaseAdmin'

export async function GET(request: NextRequest) {
  try {
    const userId = await getUserId()

    if (!userId) {
      return NextResponse.json(
        { ok: false, error: 'Not authenticated' },
        { status: 401 }
      )
    }

    const { data, error } = await supabaseAdmin
      .from('secrets')
      .select('id, title, created_at')
      .eq('owner_id', userId)
      .order('created_at', { ascending: false })

    if (error) {
      return NextResponse.json(
        { ok: false, error: 'Failed to fetch secrets' },
        { status: 500 }
      )
    }

    return NextResponse.json({ ok: true, secrets: data || [] })
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

