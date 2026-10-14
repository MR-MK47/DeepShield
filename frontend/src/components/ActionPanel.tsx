'use client'

import { useState } from 'react'
import Link from 'next/link'
import { type Match, dispatchTakedown, generateDossier } from '@/lib/api'

interface ActionPanelProps {
  selectedMatches: Match[]
  loading: boolean
}
type Platform = 'Meta' | 'Google' | 'X' | 'TikTok'

export default function ActionPanel({ selectedMatches, loading }: ActionPanelProps) {
  const [showReview, setShowReview] = useState(false)
  const [platform, setPlatform] = useState<Platform>('Meta')
  const [victimName, setVictimName] = useState('')
  const [dispatchLoading, setDispatchLoading] = useState(false)
  const [dispatchMessage, setDispatchMessage] = useState('')
  const [dispatchError, setDispatchError] = useState('')
  const [dossierLoading, setDossierLoading] = useState(false)
  const [dossierError, setDossierError] = useState('')
  const [copied, setCopied] = useState(false)

  const count = selectedMatches.length
  const ready = count > 0 && !loading
  const missingEvidence = selectedMatches.some(match => !match.hash_signature)

  const confirmDispatch = async () => {
    if (!count || missingEvidence || dispatchLoading) return
    setDispatchLoading(true)
    setDispatchError('')
    setDispatchMessage('')
    try {
      const results = []
      // Sequential requests make it clear which notice was accepted before
      // continuing to the next URL; a failure stops the batch immediately.
      for (const match of selectedMatches) {
        const result = await dispatchTakedown(
          match.url,
          platform,
          victimName.trim() || 'Aggrieved Individual',
          match.hash_signature as string,
        )
        results.push(result)
      }
      setDispatchMessage(
        `Email provider accepted ${results.length} notice request(s). This does not mean the content has been removed.`,
      )
      setShowReview(false)
    } catch (error) {
      setDispatchError(error instanceof Error ? error.message : 'Notice dispatch failed.')
    } finally {
      setDispatchLoading(false)
    }
  }

  const handleDossier = async () => {
    if (!ready || dossierLoading) return
    const confirmed = window.confirm(
      `Generate a PDF containing ${count} selected candidate(s)? Review the URLs and similarity results first. The report is not proof that the content is a deepfake.`,
    )
    if (!confirmed) return
    setDossierLoading(true)
    setDossierError('')
    try {
      const blob = await generateDossier(selectedMatches, victimName.trim() || 'Aggrieved Individual')
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `DeepShield_Candidate_Evidence_${Date.now()}.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (error) {
      setDossierError(error instanceof Error ? error.message : 'PDF generation failed.')
    } finally {
      setDossierLoading(false)
    }
  }

  const copySignatures = async () => {
    if (!count) return
    const text = selectedMatches
      .map(match => `Domain: ${match.domain}\nSimilarity candidate: ${(match.similarity * 100).toFixed(1)}%\nSignature: ${match.hash_signature || 'Not available'}\nURL: ${match.url}`)
      .join('\n\n')
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1800)
    } catch {
      setDispatchError('Clipboard access was blocked by the browser. Select and copy the candidate details manually.')
    }
  }

  return (
    <aside className="sticky top-6 w-full lg:w-80 shrink-0 space-y-4">
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="pb-3 border-b border-slate-800">
          <h3 className="text-slate-100 font-semibold text-sm">Forensic actions</h3>
          <p className="text-slate-400 text-xs mt-1">
            {count ? `${count} candidate(s) selected` : 'Select candidates before taking action.'}
          </p>
        </div>

        <div className="space-y-2">
          <button
            type="button"
            onClick={() => { setDispatchError(''); setDispatchMessage(''); setShowReview(true) }}
            disabled={!ready || dispatchLoading}
            className="w-full py-2.5 px-3.5 rounded-lg font-medium text-xs text-left bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white"
          >
            <span className="block font-semibold">Review legal notice</span>
            <span className="block text-[10px] opacity-80 mt-0.5">Nothing is sent until you confirm.</span>
          </button>
          {dispatchMessage && <p role="status" className="p-3 rounded-lg border border-emerald-800 bg-emerald-950/30 text-emerald-200 text-xs">{dispatchMessage}</p>}
          {dispatchError && (
            <div className="p-3 rounded-lg border border-red-800 bg-red-950/30 text-red-200 text-xs">
              <p>{dispatchError}</p>
              {/Please sign in|Session expired|sign in again/i.test(dispatchError) && <Link href="/login" className="inline-block mt-2 text-blue-300 underline">Sign in to continue</Link>}
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={handleDossier}
          disabled={!ready || dossierLoading}
          className="w-full py-2.5 px-3.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs text-left"
        >
          <span className="block font-semibold">{dossierLoading ? 'Generating PDF…' : 'Generate evidence report'}</span>
          <span className="block text-[10px] text-slate-400 mt-0.5">Review and confirm before export.</span>
        </button>
        {dossierError && <p role="alert" className="text-xs text-red-300">{dossierError} {(/sign in|session expired/i.test(dossierError)) && <Link href="/login" className="underline">Sign in</Link>}</p>}

        <button
          type="button"
          onClick={copySignatures}
          disabled={!ready}
          className="w-full py-2.5 px-3.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs text-left"
        >
          <span className="block font-semibold">{copied ? 'Candidate details copied' : 'Copy candidate evidence'}</span>
          <span className="block text-[10px] text-slate-400 mt-0.5">Copies the URL and actual available signature.</span>
        </button>
        <p className="pt-2 border-t border-slate-800 text-[11px] text-slate-400">
          Similarity candidates are not proof of a deepfake. Verify source evidence and notice details before sending.
        </p>
      </div>

      {showReview && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="notice-review-title">
          <div className="w-full max-w-xl max-h-[90vh] overflow-y-auto rounded-xl border border-slate-700 bg-slate-900 p-5 sm:p-6 space-y-4">
            <div>
              <h2 id="notice-review-title" className="text-lg font-semibold text-white">Review before dispatch</h2>
              <p className="text-sm text-slate-400 mt-1">Check every URL, recipient platform, name and evidence signature. This action sends real email when configured.</p>
            </div>
            <div className="space-y-1">
              <label htmlFor="complainant-name" className="block text-xs text-slate-300">Complainant name</label>
              <input id="complainant-name" value={victimName} onChange={event => setVictimName(event.target.value)} maxLength={120} placeholder="Aggrieved Individual" className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white" />
            </div>
            <div className="space-y-1">
              <label htmlFor="notice-platform" className="block text-xs text-slate-300">Destination platform</label>
              <select id="notice-platform" value={platform} onChange={event => setPlatform(event.target.value as Platform)} className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white">
                <option value="Meta">Meta</option>
                <option value="Google">Google</option>
                <option value="X">X</option>
                <option value="TikTok">TikTok</option>
              </select>
            </div>
            <div className="rounded-lg border border-slate-800 divide-y divide-slate-800">
              {selectedMatches.map((match, index) => (
                <div key={match.url} className="p-3 space-y-1">
                  <p className="text-xs text-slate-200">{index + 1}. {match.domain} · {(match.similarity * 100).toFixed(1)}% similarity</p>
                  <p className="text-[11px] text-slate-400 break-all">{match.url}</p>
                  <p className="text-[10px] text-slate-500 break-all">Evidence: {match.hash_signature || 'Missing signature'}</p>
                </div>
              ))}
            </div>
            {missingEvidence && <p role="alert" className="text-xs text-red-300">At least one selected candidate has no evidence signature. Run a fresh search before dispatching.</p>}
            {dispatchError && <p role="alert" className="text-xs text-red-300">{dispatchError}</p>}
            <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2">
              <button type="button" onClick={() => setShowReview(false)} disabled={dispatchLoading} className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-200 disabled:opacity-50">Cancel</button>
              <button type="button" onClick={confirmDispatch} disabled={dispatchLoading || missingEvidence} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                {dispatchLoading ? 'Sending…' : `Confirm and send ${count} notice(s)`}
              </button>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
