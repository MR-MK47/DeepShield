'use client'

import { useState } from 'react'
import Link from 'next/link'
import { registerOperator } from '@/lib/api'

export default function SignupClient() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmed, setConfirmed] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    if (!confirmed) {
      setError('Confirm that you understand search results are unverified candidates.')
      return
    }
    setLoading(true)
    try {
      await registerOperator(name, email, password)
      window.location.assign('/scan')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not create the account. Check the backend and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center px-6 py-12 font-sans">
      <div className="w-full max-w-sm space-y-6">
        <Link href="/" className="flex items-center gap-2.5 justify-center">
          <span className="w-8 h-8 bg-blue-600 flex items-center justify-center font-bold text-white text-xs">DS</span>
          <span className="text-lg font-bold tracking-tight">DeepShield</span>
        </Link>
        <section className="bg-slate-900/60 border border-slate-800 p-6 space-y-5">
          <div>
            <h1 className="text-lg font-bold">Create operator account</h1>
            <p className="text-xs text-slate-400 mt-1">Account data is stored in a local SQLite database on the backend.</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4 text-sm">
            <div className="space-y-1">
              <label htmlFor="signup-name" className="block text-xs font-medium text-slate-300">Full name</label>
              <input id="signup-name" autoComplete="name" value={name} onChange={event => setName(event.target.value)} required maxLength={120} className="w-full bg-slate-950 border border-slate-700 px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div className="space-y-1">
              <label htmlFor="signup-email" className="block text-xs font-medium text-slate-300">Email address</label>
              <input id="signup-email" type="email" autoComplete="email" value={email} onChange={event => setEmail(event.target.value)} required maxLength={254} className="w-full bg-slate-950 border border-slate-700 px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div className="space-y-1">
              <label htmlFor="signup-password" className="block text-xs font-medium text-slate-300">Password</label>
              <input id="signup-password" type="password" autoComplete="new-password" value={password} onChange={event => setPassword(event.target.value)} required minLength={8} maxLength={256} className="w-full bg-slate-950 border border-slate-700 px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
              <p className="text-[11px] text-slate-500">Use at least 8 characters. Do not reuse a password from another service.</p>
            </div>
            <label className="flex items-start gap-2 text-xs leading-relaxed text-slate-300">
              <input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} required className="mt-0.5" />
              <span>I understand search results are similarity candidates, not proof of deepfake content, and notices/reports must be reviewed before use.</span>
            </label>
            {error && <p role="alert" className="text-xs text-red-300 border border-red-900 bg-red-950/30 p-3">{error}</p>}
            <button type="submit" disabled={loading || !confirmed} className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-2.5 text-sm">
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>
          <p className="text-xs text-center text-slate-400 border-t border-slate-800 pt-4">
            Already registered? <Link href="/login" className="text-blue-300 underline">Sign in</Link>
          </p>
          <Link href="/scan" className="block text-center text-xs text-slate-400 underline">Continue to public scan (legal actions require sign-in)</Link>
        </section>
      </div>
    </main>
  )
}
