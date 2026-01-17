import { supabaseAdmin } from './supabaseAdmin'

export async function checkUnlocked(userId: string): Promise<boolean> {
  const { data, error } = await supabaseAdmin
    .from('sessions')
    .select('unlocked_until')
    .eq('owner_id', userId)
    .single()

  if (error || !data) {
    return false
  }

  if (!data.unlocked_until) {
    return false
  }

  const unlockedUntil = new Date(data.unlocked_until)
  return unlockedUntil > new Date()
}

export async function setUnlockedUntil(
  userId: string,
  unlockedUntil: Date
): Promise<void> {
  const { error } = await supabaseAdmin
    .from('sessions')
    .upsert(
      {
        owner_id: userId,
        unlocked_until: unlockedUntil.toISOString()
      },
      {
        onConflict: 'owner_id'
      }
    )

  if (error) {
    throw new Error(`Failed to update session: ${error.message}`)
  }
}

export async function getUnlockedUntil(userId: string): Promise<Date | null> {
  const { data, error } = await supabaseAdmin
    .from('sessions')
    .select('unlocked_until')
    .eq('owner_id', userId)
    .single()

  if (error || !data || !data.unlocked_until) {
    return null
  }

  return new Date(data.unlocked_until)
}

export async function lockNow(userId: string): Promise<void> {
  const { error } = await supabaseAdmin
    .from('sessions')
    .update({ unlocked_until: new Date().toISOString() })
    .eq('owner_id', userId)

  if (error) {
    throw new Error(`Failed to lock session: ${error.message}`)
  }
}

