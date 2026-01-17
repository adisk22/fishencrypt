import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export default async function Home() {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get('fishvault_user_id')?.value

    if (userId) {
      redirect('/vault')
    } else {
      redirect('/login')
    }
  } catch {
    redirect('/login')
  }
}

