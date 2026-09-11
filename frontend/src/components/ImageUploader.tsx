'use client'

import { useCallback, useState, useEffect } from 'react'
import { analyzeImage, searchMatches, type Match } from '@/lib/api'

interface ImageUploaderProps {
  onMatchesFound: (matches: Match[], queryText: string, threshold: number) => void
  onScanStart?: () => void
}

export default function ImageUploader({ onMatchesFound, onScanStart }: ImageUploaderProps) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [queryText, setQueryText] = useState('')
  const [threshold, setThreshold] = useState<number>(0.55)

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const handleSelectFile = useCallback((file: File) => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setError(null)
  }, [previewUrl])

  const handleResetFile = useCallback(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setSelectedFile(null)
    setPreviewUrl(null)
    setError(null)
  }, [previewUrl])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      handleSelectFile(file)
    }
  }, [handleSelectFile])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleSelectFile(file)
    }
  }, [handleSelectFile])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile || loading) return

    onScanStart?.()
    setLoading(true)
    setProgress(5)
    setError(null)

    try {
      setProgress(10)
      const analyzeRes = await analyzeImage(selectedFile)
      setProgress(50)

      const matches = await searchMatches(analyzeRes.vector, queryText || undefined, threshold)
      setProgress(90)

      setProgress(100)
      onMatchesFound(matches, queryText, threshold)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Scan process failed. Check network connection and retry.'
      setError(errorMsg)
      onMatchesFound([], queryText, threshold)
    } finally {
      setLoading(false)
      setTimeout(() => setProgress(0), 400)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Selection / Preview Box */}
      {!previewUrl ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`
            relative border border-dashed rounded-xl p-8 text-center cursor-pointer
            transition-colors duration-150 bg-slate-900/60
            ${dragging ? 'border-blue-500 bg-slate-800/80' : 'border-slate-800 hover:border-slate-700'}
          `}
        >
          <input
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          <div className="w-12 h-12 rounded-lg bg-slate-800 border border-slate-700/80 mx-auto mb-3 flex items-center justify-center">
            <svg className="w-6 h-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>

          <p className="text-sm font-medium text-slate-200">
            Select or drag a reference image file
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Accepts JPG, PNG, WEBP. ArcFace extracts a 512-dimensional vector in RAM.
          </p>
        </div>
      ) : (
        <div className="relative border border-slate-800 bg-slate-900/60 rounded-xl p-5 flex flex-col items-center justify-center min-h-[240px]">
          <img
            src={previewUrl}
            alt="Reference target preview"
            className="max-h-56 rounded-lg object-contain border border-slate-800"
          />

          <button
            type="button"
            onClick={handleResetFile}
            disabled={loading}
            className="mt-4 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 border border-slate-700 rounded-lg transition-colors disabled:opacity-40"
          >
            Change Image
          </button>

          {/* Loading Overlay */}
          {loading && (
            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-950/90 rounded-xl p-6">
              <div className="w-8 h-8 border-2 border-slate-700 border-t-blue-500 rounded-full animate-spin mb-3" />
              <p className="text-xs font-medium text-slate-200">Processing vector &amp; crawling endpoints</p>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">{selectedFile?.name}</p>

              <div className="w-64 max-w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mt-4 border border-slate-700/50">
                <div
                  className="h-full bg-blue-500 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <span className="text-[11px] text-slate-400 font-mono mt-1.5">{progress}%</span>
            </div>
          )}
        </div>
      )}

      {/* Control Inputs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Target Name or Keyword Input */}
        <div className="md:col-span-2 space-y-1.5">
          <label htmlFor="queryText" className="block text-xs font-medium text-slate-300">
            Target Query or Name (Optional)
          </label>
          <input
            id="queryText"
            type="text"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            disabled={loading}
            placeholder="e.g., Target name or keyword"
            className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-40"
          />
        </div>

        {/* Threshold Slider & Value */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <label htmlFor="threshold" className="font-medium text-slate-300">
              Similarity Threshold
            </label>
            <span className="font-mono text-slate-200">{Math.round(threshold * 100)}%</span>
          </div>
          <div className="flex items-center gap-2 pt-1">
            <input
              id="threshold"
              type="range"
              min="0.30"
              max="0.90"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              disabled={loading}
              className="w-full accent-blue-500 bg-slate-900 rounded-lg h-2 cursor-pointer disabled:opacity-40"
            />
          </div>
        </div>
      </div>

      {/* Submit Action Button */}
      <button
        type="submit"
        disabled={loading || !selectedFile}
        className={`
          w-full py-3 px-5 rounded-lg font-medium text-xs transition-colors shadow-sm flex items-center justify-center gap-2
          ${loading || !selectedFile
            ? 'bg-slate-800 text-slate-500 border border-slate-700/60 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-500 text-white cursor-pointer'}
        `}
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Scanning Web Endpoints...</span>
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Execute Forensic Search</span>
          </>
        )}
      </button>

      {/* Error Output */}
      {error && (
        <div className="p-3.5 rounded-lg bg-red-950/40 border border-red-800/80 text-red-200 text-xs">
          <p className="font-semibold text-red-100">Search Error</p>
          <p className="text-red-300 mt-0.5">{error}</p>
        </div>
      )}
    </form>
  )
}
