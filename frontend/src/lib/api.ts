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

export interface ScanHistoryEntry {
  scan_id: string
  query_text: string
  threshold: number
  matches: Match[]
  match_count: number
  created_at: number
}

export interface ContactSuggestion {
  email: string
  source_url: string
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
  if (!response.ok) {
    if (response.status === 401) window.localStorage.removeItem(TOKEN_KEY)
    throw await responseError(response, 'Please sign in again.')
  }
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
  threshold: number = 0.30,
  saveHistory = false
): Promise<Match[]> {
  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ vector, threshold, query_text: queryText, save_history: saveHistory }),
  })
  if (!response.ok) throw await responseError(response, `Search failed (${response.status}).`)
  return (await response.json()) as Match[]
}

export interface EmailTestResult {
  status: 'accepted_by_smtp'
  recipient: string
  timestamp: string
  message_id: string
}

export async function sendTestEmail(): Promise<EmailTestResult> {
  const response = await fetch(`${API_BASE}/api/email/test`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!response.ok) throw await responseError(response, `Test email failed (${response.status}).`)
  return (await response.json()) as EmailTestResult
}

export async function discoverContactEmails(
  targetUrl: string
): Promise<{ domain: string; contacts: ContactSuggestion[]; suggested_email: string | null }> {
  const response = await fetch(`${API_BASE}/api/takedown/contact-suggestions`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ target_url: targetUrl }),
  })
  if (!response.ok) throw await responseError(response, `Contact discovery failed (${response.status}).`)
  return response.json()
}

export async function previewTakedown(
  targetUrl: string,
  recipient: string,
  victimName: string,
  hashSignature: string
): Promise<{ preview_id: string; recipient: string; target_domain: string; delivery_mode: 'mock' | 'resend' | 'smtp'; notice_text: string; notice_type: string; expires_in_seconds: number }> {
  const response = await fetch(`${API_BASE}/api/takedown/preview`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      target_url: targetUrl,
      recipient,
      victim_name: victimName,
      hash_signature: hashSignature,
    }),
  })
  if (!response.ok) throw await responseError(response, `Notice preview failed (${response.status}).`)
  return response.json()
}


export async function fetchScanHistory(limit = 25): Promise<ScanHistoryEntry[]> {
  const response = await fetch(`${API_BASE}/api/matches?limit=${encodeURIComponent(String(limit))}`, {
    headers: authHeaders(),
  })
  if (!response.ok) throw await responseError(response, `Could not load scan history (${response.status}).`)
  return (await response.json()) as ScanHistoryEntry[]
}

export async function deleteScanHistory(scanId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/matches/${encodeURIComponent(scanId)}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!response.ok) throw await responseError(response, `Could not delete scan history (${response.status}).`)
}

export async function dispatchTakedown(
  previewId: string
): Promise<{ status: string; notice_type: string; recipient: string; timestamp: string; dispatch_id?: string }> {
  const response = await fetch(`${API_BASE}/api/takedown/email`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ preview_id: previewId }),
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
