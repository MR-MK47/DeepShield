'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function SignupClient() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    alert('Account creation stub: Use the scan console directly.')
    window.location.href = '/scan'
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col justify-center items-center px-6 py-12 font-sans">
      <div className="w-full max-w-sm space-y-6">
        <Link href="/" className="flex items-center gap-2.5 justify-center">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white text-xs">
            DS
          </div>
          <span className="text-lg font-bold text-slate-100 tracking-tight">DeepShield</span>
        </Link>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-5">
          <div>
            <h1 className="text-lg font-bold text-slate-100">Create Operator Account</h1>
            <p className="text-xs text-slate-400 mt-0.5">Register for legal takedown dispatch access</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div className="space-y-1">
              <label htmlFor="name" className="block font-medium text-slate-300">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                required
              />
            </div>

            <div className="space-y-1">
              <label htmlFor="email" className="block font-medium text-slate-300">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="operator@deepshield.org"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                required
              />
            </div>

            <div className="space-y-1">
              <label htmlFor="password" className="block font-medium text-slate-300">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                required
                minLength={8}
              />
            </div>

            <label className="flex items-start gap-2 text-slate-400 cursor-pointer pt-1">
              <input type="checkbox" className="w-3.5 h-3.5 mt-0.5 rounded border-slate-800 bg-slate-900 text-blue-500 focus:ring-0" required />
              <span>
                I agree to the{' '}
                <a href="#" className="text-blue-400 hover:text-blue-300">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-blue-400 hover:text-blue-300">Privacy Policy</a>
              </span>
            </label>

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 rounded-lg transition-colors cursor-pointer mt-2"
            >
              Create Account
            </button>
          </form>

          <div className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800">
            Already registered?{' '}
            <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium">
              Sign in
            </Link>
          </div>

          <Link
            href="/scan"
            className="block w-full text-center border border-slate-800 bg-slate-900 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-medium transition-colors"
          >
            Open Scan Console Without Account
          </Link>
        </div>
      </div>
    </div>
  )
}
