import { NextRequest, NextResponse } from 'next/server'
import { supabaseAdmin } from '@/lib/supabaseAdmin'
import { setUserId } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json()

    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { ok: false, error: 'Email is required' },
        { status: 400 }
      )
    }

    // Check if user exists
    let { data: existingUser, error: fetchError } = await supabaseAdmin
      .from('users')
      .select('id')
      .eq('email', email.toLowerCase().trim())
      .single()

    let userId: string

    if (fetchError || !existingUser) {
      // Create new user
      const { data: newUser, error: createError } = await supabaseAdmin
        .from('users')
        .insert({ email: email.toLowerCase().trim() })
        .select('id')
        .single()

      if (createError || !newUser) {
        return NextResponse.json(
          { ok: false, error: 'Failed to create user' },
          { status: 500 }
        )
      }

      userId = newUser.id
    } else {
      userId = existingUser.id
    }

    await setUserId(userId)

    return NextResponse.json({ ok: true })
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

