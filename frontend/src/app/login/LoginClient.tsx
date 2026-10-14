'use client'

import { useState } from 'react'
import Link from 'next/link'
import { loginOperator } from '@/lib/api'

export default function LoginClient() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await loginOperator(email, password)
      window.location.assign('/scan')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not sign in. Check the backend and try again.')
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
            <h1 className="text-lg font-bold">Sign in to DeepShield</h1>
            <p className="text-xs text-slate-400 mt-1">Use your operator account to export reports or send a notice.</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4 text-sm">
            <div className="space-y-1">
              <label htmlFor="login-email" className="block text-xs font-medium text-slate-300">Email address</label>
              <input id="login-email" type="email" autoComplete="email" value={email} onChange={event => setEmail(event.target.value)} required maxLength={254} className="w-full bg-slate-950 border border-slate-700 px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div className="space-y-1">
              <label htmlFor="login-password" className="block text-xs font-medium text-slate-300">Password</label>
              <input id="login-password" type="password" autoComplete="current-password" value={password} onChange={event => setPassword(event.target.value)} required className="w-full bg-slate-950 border border-slate-700 px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            </div>
            {error && <p role="alert" className="text-xs text-red-300 border border-red-900 bg-red-950/30 p-3">{error}</p>}
            <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-2.5 text-sm">
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
          <p className="text-xs text-center text-slate-400 border-t border-slate-800 pt-4">
            New here? <Link href="/signup" className="text-blue-300 underline">Create an operator account</Link>
          </p>
          <p className="text-[11px] text-slate-500">Password recovery email is not configured in this version. Keep your local operator password safe.</p>
          <Link href="/scan" className="block text-center text-xs text-slate-400 underline">Continue to public scan (legal actions require sign-in)</Link>
        </section>
      </div>
    </main>
  )
}
