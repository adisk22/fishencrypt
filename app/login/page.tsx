'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })

      const data = await response.json()

      if (!data.ok) {
        setError(data.error || 'Login failed')
        setLoading(false)
        return
      }

      router.push('/vault')
    } catch (err) {
      setError('An error occurred')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-carbon-900">
      <div className="max-w-md w-full mx-4">
        <div className="bg-carbon-800 rounded-xl p-8 border border-carbon-600">
          <h1 className="text-3xl font-bold text-white mb-2 drop-shadow-[0_0_12px_rgba(176,38,255,0.4)]">FishVault</h1>
          <p className="text-gray-400 mb-6">Secrets Manager</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2.5 bg-carbon-700 border border-carbon-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-neon-purple focus:border-neon-purple/50 transition-all"
                placeholder="your@email.com"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="bg-red-950/90 border border-red-800 text-red-200 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon disabled:bg-carbon-600 disabled:cursor-not-allowed text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
            >
              {loading ? 'Continuing...' : 'Continue'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

