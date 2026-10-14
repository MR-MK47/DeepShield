'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { deleteScanHistory, fetchScanHistory, type ScanHistoryEntry } from '@/lib/api'

export default function HistoryClient() {
  const [entries, setEntries] = useState<ScanHistoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const reload = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setEntries(await fetchScanHistory(100))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not load your scan history.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  const removeEntry = async (entry: ScanHistoryEntry) => {
    if (!window.confirm(`Delete this saved scan and its candidate metadata? This cannot be undone.`)) return
    setDeletingId(entry.scan_id)
    setError('')
    try {
      await deleteScanHistory(entry.scan_id)
      setEntries(current => current.filter(item => item.scan_id !== entry.scan_id))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not delete the scan history entry.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <main className="min-h-screen bg-[#080c14] text-slate-100 font-sans">
      <header className="border-b border-slate-800 bg-[#080c14]/90">
        <div className="max-w-5xl mx-auto px-5 py-4 flex items-center justify-between gap-3">
          <Link href="/" className="font-bold tracking-tight">DeepShield</Link>
          <nav className="flex items-center gap-4 text-xs text-slate-300">
            <Link href="/scan" className="underline hover:text-white">New scan</Link>
            <Link href="/login" className="underline hover:text-white">Operator sign in</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-5 py-8 space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Saved scan history</h1>
            <p className="text-sm text-slate-400 mt-2 max-w-2xl">
              Only scans you explicitly saved are listed. History contains candidate URLs, similarity scores, query text and evidence signatures — never reference photos or face vectors.
            </p>
          </div>
          <button type="button" onClick={() => void reload()} disabled={loading} className="border border-slate-700 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 disabled:opacity-50">
            {loading ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>

        {error && (
          <div role="alert" className="border border-red-900 bg-red-950/30 text-red-200 p-4 text-sm space-y-2">
            <p>{error}</p>
            {/sign in|session expired|operator/i.test(error) && <Link href="/login" className="underline text-blue-300">Sign in to view saved history</Link>}
          </div>
        )}

        {!loading && !error && entries.length === 0 && (
          <div className="border border-slate-800 bg-slate-900/40 p-6 space-y-3">
            <h2 className="font-semibold">No saved scans yet</h2>
            <p className="text-sm text-slate-400">Run a scan while signed in and select “Save these results to my account history”. Saving is optional and off by default.</p>
            <Link href="/scan" className="inline-block text-sm text-blue-300 underline">Go to scan console</Link>
          </div>
        )}

        <div className="space-y-4">
          {entries.map(entry => (
            <section key={entry.scan_id} className="border border-slate-800 bg-slate-900/50">
              <div className="p-4 border-b border-slate-800 flex flex-wrap justify-between items-start gap-3">
                <div className="space-y-1 min-w-0">
                  <h2 className="font-semibold text-sm break-words">{entry.query_text || 'Image search without a text query'}</h2>
                  <p className="text-xs text-slate-400">
                    {new Date(entry.created_at * 1000).toLocaleString()} · {Math.round(entry.threshold * 100)}% threshold · {entry.match_count} candidate(s)
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono">Scan ID: {entry.scan_id}</p>
                </div>
                <button
                  type="button"
                  onClick={() => void removeEntry(entry)}
                  disabled={deletingId === entry.scan_id}
                  className="border border-red-900 text-red-300 hover:bg-red-950/40 px-3 py-2 text-xs disabled:opacity-50"
                >
                  {deletingId === entry.scan_id ? 'Deleting…' : 'Delete history'}
                </button>
              </div>
              {entry.matches.length === 0 ? (
                <p className="p-4 text-xs text-slate-500">This saved search had no candidates above the selected threshold.</p>
              ) : (
                <div className="divide-y divide-slate-800">
                  {entry.matches.map((match, index) => (
                    <div key={`${entry.scan_id}-${match.url}-${index}`} className="p-4 grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-2">
                      <div className="min-w-0 space-y-1">
                        <p className="text-xs text-slate-200">{match.domain}</p>
                        <a href={match.url} target="_blank" rel="noopener noreferrer" className="block text-xs text-blue-300 hover:text-blue-200 break-all underline">{match.url}</a>
                        <p className="text-[10px] text-slate-500 break-all">{match.hash_signature || 'No signature recorded'}</p>
                      </div>
                      <div className="text-xs text-slate-300 sm:text-right">{(match.similarity * 100).toFixed(1)}% similarity</div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          ))}
        </div>

        <p className="text-[11px] text-slate-500 border-t border-slate-800 pt-4">
          Saved metadata can still contain sensitive URLs or search terms. Delete entries when they are no longer needed. Candidate similarity is not proof of synthetic or unlawful content.
        </p>
      </div>
    </main>
  )
}
