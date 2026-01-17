import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-carbon-900 flex flex-col items-center justify-center p-8">
      <h1 className="text-6xl font-bold text-white mb-2 drop-shadow-[0_0_12px_rgba(176,38,255,0.4)]">
        404
      </h1>
      <p className="text-gray-400 mb-6 text-lg">Page not found</p>
      <p className="text-gray-500 mb-8 text-center max-w-md">
        The page you&apos;re looking for doesn&apos;t exist. If you were trying to reach FishVault,
        use the links below.
      </p>
      <div className="flex gap-4">
        <Link
          href="/"
          className="px-5 py-2.5 bg-neon-purple hover:bg-neon-purple-light hover:shadow-neon text-white rounded-xl font-medium border border-neon-purple/50 transition-all duration-200"
        >
          Home
        </Link>
        <Link
          href="/login"
          className="px-5 py-2.5 bg-carbon-700 hover:bg-carbon-600 text-white rounded-xl font-medium border border-carbon-600 transition-all duration-200"
        >
          Login
        </Link>
      </div>
      <p className="text-gray-600 text-sm mt-8">
        Tip: If you see this on / or /login, check that the dev server is running and you&apos;re
        using the correct port (e.g. http://localhost:3000 or http://localhost:3003).
      </p>
    </div>
  )
}

