'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'
import ImageUploader from '@/components/ImageUploader'
import MatchGrid from '@/components/MatchGrid'
import ActionPanel from '@/components/ActionPanel'
import { type Match } from '@/lib/api'

export default function ScanClient() {
  const [matches, setMatches] = useState<Match[]>([])
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [scanLoading, setScanLoading] = useState(false)
  const [hasScanned, setHasScanned] = useState(false)
  const [lastQuery, setLastQuery] = useState<string>('')
  const [lastThreshold, setLastThreshold] = useState<number>(0.55)

  const handleScanStart = useCallback(() => {
    setHasScanned(false)
  }, [])

  const handleMatchesFound = useCallback((found: Match[], queryText: string, threshold: number) => {
    setMatches(found)
    setSelectedIds(new Set())
    setScanLoading(false)
    setHasScanned(true)
    setLastQuery(queryText)
    setLastThreshold(threshold)
  }, [])

  const handleToggle = useCallback((id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const handleSelectAll = useCallback(() => {
    setSelectedIds(new Set(matches.map((_, i) => `match-${i}`)))
  }, [matches])

  const handleDeselectAll = useCallback(() => {
    setSelectedIds(new Set())
  }, [])

  const selectedMatches = matches.filter((_, i) => selectedIds.has(`match-${i}`))
  const thresholdPercent = Math.round(lastThreshold * 100)

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-[#080c14]/90 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white text-sm shadow-sm">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <span className="text-base font-bold text-slate-100 font-display tracking-tight">DeepShield</span>
              <span className="text-xs text-slate-400 ml-2 font-mono">v0.2</span>
            </div>
          </Link>

          <div className="flex items-center gap-4 text-xs text-slate-400 font-mono">
            <span>DPDP Act 2023 Compliant</span>
            <span className="text-slate-800">|</span>
            <span>RAM Vector Lifecycle</span>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="max-w-7xl w-full mx-auto px-6 py-8 flex-1 space-y-8">
        {/* Title */}
        <div className="space-y-1 max-w-3xl">
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-slate-100 tracking-tight">
            Forensic Deepfake Scan &amp; Impersonation Search
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 leading-normal">
            Extract ArcFace biometric vectors and query public endpoints for candidate deepfake matches.
          </p>
        </div>

        {/* Upload Control Station */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm">
          <ImageUploader onMatchesFound={handleMatchesFound} onScanStart={handleScanStart} />
        </section>

        {/* Match Candidates & Actions */}
        {matches.length > 0 && (
          <div className="flex flex-col lg:flex-row gap-6 pt-2">
            <section className="flex-1 min-w-0">
              <MatchGrid
                matches={matches}
                selectedIds={selectedIds}
                onToggle={handleToggle}
                onSelectAll={handleSelectAll}
                onDeselectAll={handleDeselectAll}
              />
            </section>

            <ActionPanel
              selectedMatches={selectedMatches}
              loading={scanLoading}
            />
          </div>
        )}

        {/* Informative Empty State Report */}
        {hasScanned && matches.length === 0 && (
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 max-w-2xl mx-auto space-y-4">
            <div className="space-y-1">
              <h3 className="text-base font-semibold font-display text-slate-200">
                No matches found exceeding {thresholdPercent}% similarity{lastQuery ? ` for "${lastQuery}"` : ''}
              </h3>
              <p className="text-xs text-slate-400 leading-normal">
                The OSINT crawl evaluated candidate public web images against your 512-D face vector, but none scored above the selected threshold ({thresholdPercent}%).
              </p>
            </div>

            <div className="pt-3 border-t border-slate-800 space-y-2">
              <p className="text-xs font-medium text-slate-300">Suggested steps to improve search recall:</p>
              <ul className="text-xs text-slate-400 space-y-1.5 list-disc pl-4">
                <li>Verify spelling or try alternate name keywords in the target query input.</li>
                <li>Adjust the similarity threshold slider to a lower setting (e.g. 50% or 45%).</li>
                <li>Ensure the uploaded photo has clear facial lighting and un-occluded features.</li>
              </ul>
            </div>
          </div>
        )}
      </main>

      {/* Minimal Footer */}
      <footer className="border-t border-slate-800 py-4 text-xs text-slate-400 bg-[#080c14]">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between font-mono text-[11px]">
          <p>DeepShield System &middot; Rule 3(1)(b) IT Rules 2021</p>
          <p>Zero Biometric Persistence</p>
        </div>
      </footer>
    </div>
  )
}
