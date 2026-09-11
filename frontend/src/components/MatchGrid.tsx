'use client'

import { useState } from 'react'
import { type Match } from '@/lib/api'

interface MatchGridProps {
  matches: Match[]
  selectedIds: Set<string>
  onToggle: (id: string) => void
  onSelectAll: () => void
  onDeselectAll: () => void
}

function DomainBadge({ domain }: { domain: string }) {
  return (
    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
      {domain}
    </span>
  )
}

function SimilarityBadge({ score }: { score: number }) {
  const percent = (score * 100).toFixed(1)
  const isHigh = score >= 0.80
  const isMed = score >= 0.60

  const colour =
    isHigh ? 'bg-red-950/50 text-red-300 border-red-800' :
    isMed ? 'bg-blue-950/50 text-blue-300 border-blue-800' :
    'bg-slate-800 text-slate-300 border-slate-700'

  return (
    <span className={`text-xs font-mono font-medium border px-2.5 py-0.5 rounded ${colour}`}>
      {percent}% match
    </span>
  )
}

export default function MatchGrid({
  matches,
  selectedIds,
  onToggle,
  onSelectAll,
  onDeselectAll,
}: MatchGridProps) {
  const [expandedMatch, setExpandedMatch] = useState<Match | null>(null)
  const allSelected = matches.length > 0 && selectedIds.size === matches.length

  if (matches.length === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2 text-xs">
          <span className="font-semibold text-slate-200 font-display">Candidates Isolated</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-slate-300">
            {matches.length}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <button
            onClick={allSelected ? onDeselectAll : onSelectAll}
            className="text-blue-400 hover:text-blue-300 transition-colors font-medium"
          >
            {allSelected ? 'Deselect All' : 'Select All'}
          </button>
          <span className="text-slate-800">|</span>
          <button
            onClick={onDeselectAll}
            disabled={selectedIds.size === 0}
            className="text-slate-400 hover:text-slate-200 disabled:opacity-40 transition-colors"
          >
            Clear Selection
          </button>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {matches.map((m, i) => {
          const id = `match-${i}`
          const checked = selectedIds.has(id)
          return (
            <div
              key={id}
              className={`
                group relative rounded-xl border overflow-hidden cursor-pointer
                transition-colors duration-150 bg-slate-900/60
                ${checked
                  ? 'border-blue-500 bg-slate-900/90'
                  : 'border-slate-800 hover:border-slate-700'}
              `}
            >
              {/* Select Checkbox (top-left) */}
              <div className="absolute top-3 left-3 z-10" onClick={(e) => { e.stopPropagation(); onToggle(id) }}>
                <div className={`
                  w-5 h-5 rounded border flex items-center justify-center transition-colors
                  ${checked ? 'bg-blue-600 border-blue-500 text-white' : 'border-slate-700 bg-slate-900/90'}
                `}>
                  {checked && (
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
              </div>

              {/* Similarity Badge (top-right) */}
              <div className="absolute top-3 right-3 z-10">
                <SimilarityBadge score={m.similarity} />
              </div>

              {/* Aspect 4/3 Responsive Evidence Frame */}
              <div
                onClick={() => onToggle(id)}
                className="relative w-full aspect-[4/3] bg-slate-950/90 rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center group/frame"
              >
                <img
                  src={m.thumbnail || m.url}
                  alt={`Candidate evidence from ${m.domain}`}
                  className="w-full h-full object-contain p-1 transition-transform duration-200 group-hover/frame:scale-[1.02]"
                  loading="lazy"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      'data:image/svg+xml;charset=UTF-8,' +
                      encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="300" height="225" fill="%230b0f19"><rect width="300" height="225"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23475569" font-size="12">Thumbnail unavailable</text></svg>`)
                  }}
                />

                {/* Expand Evidence Overlay Icon */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setExpandedMatch(m)
                  }}
                  className="absolute bottom-2 right-2 bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 text-slate-300 p-1.5 rounded-md opacity-0 group-hover/frame:opacity-100 transition-opacity backdrop-blur-sm shadow-md"
                  title="Expand Evidence Inspection"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                  </svg>
                </button>
              </div>

              {/* Metadata Footer */}
              <div className="p-3.5 space-y-2 border-t border-slate-800" onClick={() => onToggle(id)}>
                <div className="flex items-center justify-between gap-2">
                  <DomainBadge domain={m.domain} />
                  <span className="text-[10px] font-mono text-slate-500">#{i + 1}</span>
                </div>

                <p className="text-xs text-slate-400 font-mono truncate" title={m.url}>
                  {m.url}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Forensic Inspection Modal */}
      {expandedMatch && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md"
          onClick={() => setExpandedMatch(null)}
        >
          <div
            className="bg-slate-900 border border-slate-800 rounded-xl max-w-3xl w-full p-6 space-y-4 shadow-2xl relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-100 font-display">Forensic Evidence Inspection</h3>
                <p className="text-xs text-slate-400">Natural dimension rendering &amp; source metadata</p>
              </div>
              <button
                onClick={() => setExpandedMatch(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Evidence Image (Full aspect ratio) */}
            <div className="bg-slate-950 rounded-lg p-2 border border-slate-800 flex items-center justify-center max-h-[60vh] overflow-hidden">
              <img
                src={expandedMatch.thumbnail || expandedMatch.url}
                alt={`Full forensic evidence from ${expandedMatch.domain}`}
                className="max-h-[55vh] max-w-full object-contain rounded"
              />
            </div>

            {/* Evidence Metadata & Actions */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs pt-1">
              <div className="space-y-1">
                <span className="text-slate-400 font-medium">Similarity Match</span>
                <div>
                  <SimilarityBadge score={expandedMatch.similarity} />
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-slate-400 font-medium">Host Platform Domain</span>
                <div>
                  <DomainBadge domain={expandedMatch.domain} />
                </div>
              </div>

              <div className="space-y-1 flex flex-col justify-end">
                <a
                  href={expandedMatch.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium py-2 px-3 rounded-lg transition-colors text-xs"
                >
                  <span>Open Source URL</span>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <p className="text-[11px] font-mono text-slate-400 truncate" title={expandedMatch.url}>
                URL: {expandedMatch.url}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
