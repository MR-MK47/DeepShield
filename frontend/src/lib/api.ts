const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const TOKEN_KEY = 'deepshield_session_token'

export interface Match {
  url: string
  domain: string
  similarity: number
  thumbnail: string
  hash_signature?: string
}

export interface AnalyzeResponse {
  status: string
  vector: number[]
  vector_kind?: 'arcface' | 'phash' | string
  hash: string
  hash_kind?: string
}

export interface Operator {
  id: number
  name: string
  email: string
  created_at: number
}

interface AuthResponse {
  status: string
  token: string
  user: Operator
}

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return window.localStorage.getItem(TOKEN_KEY)
}

function authHeaders(initial: Record<string, string> = {}): Record<string, string> {
  const headers = { ...initial }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

async function responseError(response: Response, fallback: string): Promise<Error> {
  const payload = await response.json().catch(() => ({}))
  const detail = typeof payload.detail === 'string' ? payload.detail : fallback
  return new Error(detail)
}

async function authRequest(path: string, payload: Record<string, string>): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw await responseError(response, `Authentication failed (${response.status}).`)
  const result = (await response.json()) as AuthResponse
  window.localStorage.setItem(TOKEN_KEY, result.token)
  return result
}

export async function registerOperator(name: string, email: string, password: string): Promise<AuthResponse> {
  return authRequest('/api/auth/register', { name, email, password })
}

export async function loginOperator(email: string, password: string): Promise<AuthResponse> {
  return authRequest('/api/auth/login', { email, password })
}

export async function getCurrentOperator(): Promise<Operator> {
  const response = await fetch(`${API_BASE}/api/auth/me`, { headers: authHeaders() })
  if (!response.ok) throw await responseError(response, 'Please sign in again.')
  const result = (await response.json()) as { user: Operator }
  return result.user
}

export async function logoutOperator(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/api/auth/logout`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!response.ok) throw await responseError(response, 'Could not end the server session.')
  } finally {
    if (typeof window !== 'undefined') window.localStorage.removeItem(TOKEN_KEY)
  }
}

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', body: formData })
  if (!response.ok) throw await responseError(response, `Image analysis failed (${response.status}).`)
  return (await response.json()) as AnalyzeResponse
}

export async function searchMatches(
  vector: number[],
  queryText?: string,
  threshold: number = 0.30
): Promise<Match[]> {
  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vector, threshold, query_text: queryText }),
  })
  if (!response.ok) throw await responseError(response, `Search failed (${response.status}).`)
  return (await response.json()) as Match[]
}

export async function previewTakedown(
  targetUrl: string,
  platform: string,
  victimName: string,
  hashSignature: string
): Promise<{ recipient: string; notice_text: string; notice_type: string }> {
  const response = await fetch(`${API_BASE}/api/takedown/preview`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      target_url: targetUrl,
      platform,
      victim_name: victimName,
      hash_signature: hashSignature,
    }),
  })
  if (!response.ok) throw await responseError(response, `Notice preview failed (${response.status}).`)
  return response.json()
}

export async function dispatchTakedown(
  targetUrl: string,
  platform: string,
  victimName: string,
  hashSignature: string
): Promise<{ status: string; notice_type: string; recipient: string; timestamp: string; dispatch_id?: string }> {
  const response = await fetch(`${API_BASE}/api/takedown/email`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      target_url: targetUrl,
      platform,
      victim_name: victimName,
      hash_signature: hashSignature,
    }),
  })
  if (!response.ok) throw await responseError(response, `Takedown request failed (${response.status}).`)
  return response.json()
}

export async function generateDossier(matches: Match[], victimName = 'Aggrieved Individual'): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/dossier`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ victim_name: victimName, matches }),
  })
  if (!response.ok) throw await responseError(response, `Dossier generation failed (${response.status}).`)
  return response.blob()
}
