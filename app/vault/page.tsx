'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import StatusChip from '@/components/StatusChip'
import SecretModal from '@/components/SecretModal'

interface Secret {
  id: string
  title: string
  created_at: string
}

export default function VaultPage() {
  const router = useRouter()
  const [unlockedUntil, setUnlockedUntil] = useState<Date | null>(null)
  const [secrets, setSecrets] = useState<Secret[]>([])
  const [loading, setLoading] = useState(true)
  const [unlocking, setUnlocking] = useState(false)
  const [locking, setLocking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedSecret, setSelectedSecret] = useState<Secret | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newSecretTitle, setNewSecretTitle] = useState('')
  const [newSecretValue, setNewSecretValue] = useState('')
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    checkSession()
    loadSecrets()
  }, [])

  const checkSession = async () => {
    try {
      const response = await fetch('/api/session/status', {
        method: 'GET'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.unlockedUntil) {
          setUnlockedUntil(new Date(data.unlockedUntil))
        }
      }
    } catch (err) {
      // Session status endpoint might not exist, that's okay
    }
  }

  const loadSecrets = async () => {
    try {
      const response = await fetch('/api/secrets/list')
      if (response.status === 401) {
        router.push('/login')
        return
      }

      const data = await response.json()
      if (data.ok) {
        setSecrets(data.secrets || [])
      }
    } catch (err) {
      setError('Failed to load secrets')
    } finally {
      setLoading(false)
    }
  }

  const handleUnlock = async () => {
    setUnlocking(true)
    setError(null)

    try {
      const response = await fetch('/api/session/unlock', {
        method: 'POST'
      })

      if (response.status === 401) {
        router.push('/login')
        return
      }

      const data = await response.json()

      if (!data.ok) {
        setError(data.error || 'Failed to unlock vault')
        return
      }

      setUnlockedUntil(new Date(data.unlockedUntil))
    } catch (err) {
      setError('An error occurred')
    } finally {
      setUnlocking(false)
    }
  }

  const handleLock = async () => {
    setLocking(true)
    setError(null)

    try {
      const response = await fetch('/api/session/lock', {
        method: 'POST'
      })

      if (response.status === 401) {
        router.push('/login')
        return
      }

      const data = await response.json()

      if (!data.ok) {
        setError(data.error || 'Failed to lock vault')
        return
      }

      setUnlockedUntil(null)
    } catch (err) {
      setError('An error occurred')
    } finally {
      setLocking(false)
    }
  }

  const handleCreateSecret = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setError(null)

    try {
      const response = await fetch('/api/secrets/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newSecretTitle,
          plaintext: newSecretValue
        })
      })

      if (response.status === 401) {
        router.push('/login')
        return
      }

      const data = await response.json()

      if (!data.ok) {
        setError(data.error || 'Failed to create secret')
        setCreating(false)
        return
      }

      // Reset form and reload secrets
      setNewSecretTitle('')
      setNewSecretValue('')
      setShowAddForm(false)
      await loadSecrets()
    } catch (err) {
      setError('An error occurred')
    } finally {
      setCreating(false)
    }
  }

  const isUnlocked = unlockedUntil && new Date(unlockedUntil) > new Date()

  return (
    <div className="min-h-screen bg-carbon-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-4 drop-shadow-[0_0_12px_rgba(176,38,255,0.4)]">FishVault</h1>
          <div className="flex items-center gap-4 mb-4">
            <StatusChip unlockedUntil={unlockedUntil} />
            {!isUnlocked ? (
              <button
                onClick={handleUnlock}
                disabled={unlocking}
                className="px-5 py-2.5 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon disabled:bg-carbon-600 disabled:cursor-not-allowed text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
              >
                {unlocking ? 'Unlocking...' : 'Unlock Vault'}
              </button>
            ) : (
              <button
                onClick={handleLock}
                disabled={locking}
                className="px-5 py-2.5 bg-red-900/90 hover:bg-red-800 border border-red-700/50 text-red-100 rounded-xl font-medium disabled:bg-carbon-600 disabled:cursor-not-allowed transition-all duration-200"
              >
                {locking ? 'Locking...' : 'Lock Now'}
              </button>
            )}
          </div>
          {error && (
            <div className="bg-red-950/90 border border-red-800 text-red-200 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
        </div>

        <div className="bg-carbon-800 rounded-xl p-6 border border-carbon-600">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-white">Secrets</h2>
            {isUnlocked && (
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="px-4 py-2 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
              >
                {showAddForm ? 'Cancel' : 'Add Secret'}
              </button>
            )}
          </div>

          {showAddForm && isUnlocked && (
            <form onSubmit={handleCreateSecret} className="mb-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  value={newSecretTitle}
                  onChange={(e) => setNewSecretTitle(e.target.value)}
                  required
                  className="w-full px-4 py-2 bg-carbon-700 border border-carbon-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-neon-purple focus:border-neon-purple/50 transition-all"
                  placeholder="Secret title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Secret Value
                </label>
                <textarea
                  value={newSecretValue}
                  onChange={(e) => setNewSecretValue(e.target.value)}
                  required
                  rows={4}
                  className="w-full px-4 py-2 bg-carbon-700 border border-carbon-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-neon-purple focus:border-neon-purple/50 transition-all"
                  placeholder="Enter your secret..."
                />
              </div>
              <button
                type="submit"
                disabled={creating}
                className="px-4 py-2 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon disabled:bg-carbon-600 disabled:cursor-not-allowed text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
              >
                {creating ? 'Creating...' : 'Create Secret'}
              </button>
            </form>
          )}

          {loading ? (
            <div className="text-gray-400">Loading secrets...</div>
          ) : secrets.length === 0 ? (
            <div className="text-gray-400">No secrets yet. Add one to get started.</div>
          ) : (
            <div className="space-y-2">
              {secrets.map((secret) => (
                <div
                  key={secret.id}
                  className="flex items-center justify-between p-4 bg-carbon-700 rounded-lg border border-carbon-600 hover:border-neon-purple/30 transition-colors"
                >
                  <div>
                    <div className="text-white font-medium">{secret.title}</div>
                    <div className="text-sm text-gray-400">
                      {new Date(secret.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  {isUnlocked ? (
                    <button
                      onClick={() => setSelectedSecret(secret)}
                      className="px-4 py-2 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
                    >
                      View
                    </button>
                  ) : (
                    <span className="text-gray-500 text-sm">Unlock to view</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selectedSecret && (
        <SecretModal
          secretId={selectedSecret.id}
          secretTitle={selectedSecret.title}
          onClose={() => setSelectedSecret(null)}
        />
      )}
    </div>
  )
}

