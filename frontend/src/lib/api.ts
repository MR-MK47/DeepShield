const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Match {
  url: string
  domain: string
  similarity: number
  thumbnail: string
}

export interface AnalyzeResponse {
  status: string
  vector: number[]
  hash: string
}

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as any).detail || `Scan failed: ${res.statusText}`)
  }

  return res.json() as Promise<AnalyzeResponse>
}

export async function searchMatches(
  vector: number[],
  queryText?: string,
  threshold: number = 0.55
): Promise<Match[]> {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vector, threshold, query_text: queryText }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as any).detail || `Search failed: ${res.statusText}`)
  }

  return res.json() as Promise<Match[]>
}

export async function dispatchTakedown(
  targetUrl: string,
  platform: string
): Promise<{ status: string; notice_type: string; recipient: string; timestamp: string }> {
  const res = await fetch(`${API_BASE}/api/takedown/email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_url: targetUrl, platform }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as any).detail || `Takedown failed: ${res.statusText}`)
  }

  return res.json()
}

export async function generateDossier(matches: Match[]): Promise<Blob> {
  // Dossier generation is backend-side; placeholder for Phase 4
  // Returns an empty blob to indicate client-side stub
  return new Blob([], { type: 'application/pdf' })
}
