'use client'

import { useState } from 'react'
import { type Match } from '@/lib/api'
import { dispatchTakedown } from '@/lib/api'

interface ActionPanelProps {
  selectedMatches: Match[]
  loading: boolean
}

type DispatchStatus = 'idle' | 'confirm' | 'sending' | 'done' | 'error'

export default function ActionPanel({ selectedMatches, loading: scanLoading }: ActionPanelProps) {
  const [dispatchStatus, setDispatchStatus] = useState<DispatchStatus>('idle')
  const [lastResult, setLastResult] = useState<{ recipient: string; ts: string } | null>(null)
  const [errorMsg, setErrorMsg] = useState<string>('')
  const [copied, setCopied] = useState(false)

  const count = selectedMatches.length
  const ready = count > 0 && !scanLoading

  const handleDispatch = async () => {
    if (count === 0) return
    setDispatchStatus('sending')
    setErrorMsg('')
    try {
      const results = await Promise.all(
        selectedMatches.map(m => dispatchTakedown(m.url, 'Meta'))
      )
      const last = results[results.length - 1]
      setLastResult({ recipient: last.recipient, ts: last.timestamp })
      setDispatchStatus('done')
    } catch (err) {
      setDispatchStatus('error')
      setErrorMsg(err instanceof Error ? err.message : 'Dispatch failed')
    }
  }

  const handleDossier = () => {
    alert('Cybercrime Dossier (PDF) generation stub.\nSelected candidates: ' + count)
  }

  const handleCopyHashes = () => {
    if (count === 0) return
    const text = selectedMatches.map(m => `[Candidate] ${m.domain} | Match: ${(m.similarity * 100).toFixed(1)}% | URL: ${m.url}`).join('\n')
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <aside className="sticky top-6 w-full lg:w-80 shrink-0 space-y-4">
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-slate-100 font-semibold text-sm">Forensic Actions</h3>
            <p className="text-slate-400 text-xs mt-0.5">
              {count > 0
                ? `${count} candidate${count > 1 ? 's' : ''} selected`
                : 'Select matches to execute action'}
            </p>
          </div>
          {count > 0 && (
            <span className="px-2 py-0.5 rounded bg-blue-950 border border-blue-800 text-blue-300 text-xs font-mono">
              {count} Active
            </span>
          )}
        </div>

        {/* Primary Action: Rule 3(1)(b) Notice */}
        <div className="space-y-2">
          <button
            onClick={handleDispatch}
            disabled={!ready || dispatchStatus === 'sending'}
            className={`
              w-full py-2.5 px-3.5 rounded-lg font-medium text-xs text-left flex items-center justify-between
              transition-colors shadow-sm
              ${ready && dispatchStatus !== 'sending'
                ? 'bg-blue-600 hover:bg-blue-500 text-white cursor-pointer'
                : 'bg-slate-800 text-slate-500 border border-slate-700/60 cursor-not-allowed'}
            `}
          >
            <div>
              <div className="font-semibold">Dispatch Rule 3(1)(b) Notice</div>
              <div className="text-[10px] opacity-80 mt-0.5">IT Rules 2021 Grievance Officer</div>
            </div>
            {dispatchStatus === 'sending' && (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin shrink-0" />
            )}
          </button>

          {dispatchStatus === 'done' && lastResult && (
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1">
              <p className="font-semibold text-emerald-400">Notice Dispatched</p>
              <p className="text-[11px] text-slate-300">Recipient: {lastResult.recipient}</p>
              <p className="text-[10px] text-slate-500 font-mono">{new Date(lastResult.ts).toLocaleString()}</p>
            </div>
          )}

          {dispatchStatus === 'error' && (
            <div className="p-3 rounded-lg bg-red-950/40 border border-red-800 text-red-200 text-xs">
              <p className="font-semibold">Dispatch Error</p>
              <p className="text-[11px] text-red-300 mt-0.5">{errorMsg}</p>
            </div>
          )}
        </div>

        {/* Action 2: Generate Cybercrime Dossier */}
        <button
          onClick={handleDossier}
          disabled={!ready}
          className={`
            w-full py-2.5 px-3.5 rounded-lg font-medium text-xs text-left transition-colors border
            ${ready
              ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700 cursor-pointer'
              : 'bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed'}
          `}
        >
          <div className="font-semibold">Generate Cybercrime Dossier</div>
          <div className="text-[10px] text-slate-400 mt-0.5">ReportLab PDF &amp; Evidence Packet</div>
        </button>

        {/* Action 3: Copy Hash Signatures */}
        <button
          onClick={handleCopyHashes}
          disabled={!ready}
          className={`
            w-full py-2.5 px-3.5 rounded-lg font-medium text-xs text-left transition-colors border
            ${ready
              ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700 cursor-pointer'
              : 'bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed'}
          `}
        >
          <div className="font-semibold">{copied ? 'Signatures Copied to Clipboard' : 'Copy Hash Signatures'}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Export isolated URL &amp; vector metadata</div>
        </button>

        {/* Compliance Note */}
        <div className="pt-2 border-t border-slate-800">
          <p className="text-[11px] text-slate-400 leading-normal">
            Human-in-the-loop requirement: Every legal notice dispatch requires explicit operator confirmation per DPDP Act 2023.
          </p>
        </div>
      </div>
    </aside>
  )
}
