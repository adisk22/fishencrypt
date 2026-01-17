'use client'

import { useState } from 'react'

interface SecretModalProps {
  secretId: string
  secretTitle: string
  onClose: () => void
}

export default function SecretModal({
  secretId,
  secretTitle,
  onClose
}: SecretModalProps) {
  const [plaintext, setPlaintext] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDecrypt = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/secrets/decrypt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ secretId })
      })

      const data = await response.json()

      if (!data.ok) {
        setError(data.error || 'Failed to decrypt secret')
        return
      }

      setPlaintext(data.plaintext)
    } catch (err) {
      setError('An error occurred while decrypting')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (plaintext) {
      navigator.clipboard.writeText(plaintext)
    }
  }

  return (
    <div className="fixed inset-0 bg-carbon-950/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-carbon-800 rounded-xl p-6 max-w-md w-full mx-4 border border-carbon-600 shadow-neon-lg">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">{secretTitle}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-neon-purple-light transition-colors"
          >
            ✕
          </button>
        </div>

        {!plaintext && !error && (
          <div className="space-y-4">
            <p className="text-gray-300">
              Click the button below to decrypt and view this secret.
            </p>
            <button
              onClick={handleDecrypt}
              disabled={loading}
              className="w-full px-4 py-2.5 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon disabled:bg-carbon-600 disabled:cursor-not-allowed text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
            >
              {loading ? 'Decrypting...' : 'Decrypt Secret'}
            </button>
          </div>
        )}

        {error && (
          <div className="space-y-4">
            <div className="bg-red-950/90 border border-red-800 text-red-200 px-4 py-3 rounded-lg">
              {error}
            </div>
            <button
              onClick={handleDecrypt}
              disabled={loading}
              className="w-full px-4 py-2.5 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon disabled:bg-carbon-600 disabled:cursor-not-allowed text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
            >
              Retry
            </button>
          </div>
        )}

        {plaintext && (
          <div className="space-y-4">
            <div className="bg-carbon-900 border border-carbon-600 rounded-lg p-4">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words">
                {plaintext}
              </pre>
            </div>
            <button
              onClick={handleCopy}
              className="w-full px-4 py-2.5 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
            >
              Copy to Clipboard
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

