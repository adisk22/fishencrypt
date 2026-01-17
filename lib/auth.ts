import { cookies } from 'next/headers'

const COOKIE_NAME = 'fishvault_user_id'

export async function getUserId(): Promise<string | null> {
  const cookieStore = await cookies()
  const userId = cookieStore.get(COOKIE_NAME)?.value
  return userId || null
}

export async function setUserId(userId: string) {
  const cookieStore = await cookies()
  cookieStore.set(COOKIE_NAME, userId, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 30 // 30 days
  })
}

export async function clearUserId() {
  const cookieStore = await cookies()
  cookieStore.delete(COOKIE_NAME)
}

