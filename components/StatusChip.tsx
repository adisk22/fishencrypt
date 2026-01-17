'use client'

interface StatusChipProps {
  unlockedUntil: Date | null
}

export default function StatusChip({ unlockedUntil }: StatusChipProps) {
  const isUnlocked = unlockedUntil && new Date(unlockedUntil) > new Date()

  if (isUnlocked && unlockedUntil) {
    const timeStr = new Date(unlockedUntil).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
    return (
      <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-neon-purple/20 text-neon-purple-light border border-neon-purple/50">
        Unlocked until {timeStr}
      </span>
    )
  }

  return (
    <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-carbon-700 text-gray-400 border border-carbon-500">
      Locked
    </span>
  )
}

