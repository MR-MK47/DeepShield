'use client'

import { useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import Link from 'next/link'
import {
  type ContactSuggestion,
  type Match,
  dispatchTakedown,
  discoverContactEmails,
  generateDossier,
  previewTakedown,
} from '@/lib/api'

interface ActionPanelProps {
  selectedMatches: Match[]
  loading: boolean
}

interface NoticePreview {
  preview_id: string
  recipient: string
  target_domain: string
  delivery_mode: 'mock' | 'resend'
  notice_text: string
  notice_type: string
}

function getHost(url: string): string {
  try {
    return new URL(url).hostname
  } catch {
    return 'reported website'
  }
}

export default function ActionPanel({ selectedMatches, loading }: ActionPanelProps) {
  const [showReview, setShowReview] = useState(false)
  const [victimName, setVictimName] = useState('')
  const [recipient, setRecipient] = useState('')
  const [contactSuggestions, setContactSuggestions] = useState<ContactSuggestion[]>([])
  const [contactSearchLoading, setContactSearchLoading] = useState(false)
  const [contactMessage, setContactMessage] = useState('')
  const [preview, setPreview] = useState<NoticePreview | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [dispatchLoading, setDispatchLoading] = useState(false)
  const [dispatchMessage, setDispatchMessage] = useState('')
  const [dispatchError, setDispatchError] = useState('')
  const [dossierLoading, setDossierLoading] = useState(false)
  const [dossierError, setDossierError] = useState('')
  const [copied, setCopied] = useState(false)
  const recipientEdited = useRef(false)
  const contactRequestSequence = useRef(0)

  const count = selectedMatches.length
  const ready = count > 0 && !loading
  const missingEvidence = selectedMatches.some(match => !match.hash_signature)
  const canReviewNotice = ready && count === 1
  const targetUrl = selectedMatches[0]?.url || ''
  const targetDomain = getHost(targetUrl)

  const findContacts = async (url: string) => {
    if (!url || contactSearchLoading) return
    const requestId = ++contactRequestSequence.current
    setContactSearchLoading(true)
    setContactSuggestions([])
    setContactMessage('Searching public contact pages on this website…')
    try {
      const result = await discoverContactEmails(url)
      if (requestId !== contactRequestSequence.current) return
      setContactSuggestions(result.contacts || [])
      if (result.suggested_email) {
        if (!recipientEdited.current) setRecipient(result.suggested_email)
        setContactMessage(
          `Found ${result.contacts.length} public email address(es). Check the source page and verify the destination before sending.`,
        )
      } else {
        setContactMessage(
          'No public email address was found on the checked pages. You can enter a verified address manually.',
        )
      }
    } catch (error) {
      if (requestId !== contactRequestSequence.current) return
      setContactMessage(
        error instanceof Error
          ? `${error.message} You can still enter a verified address manually.`
          : 'Could not search contact pages. Enter a verified address manually.',
      )
    } finally {
      if (requestId === contactRequestSequence.current) setContactSearchLoading(false)
    }
  }

  const openReview = () => {
    setDispatchError('')
    setDispatchMessage('')
    setVictimName('')
    contactRequestSequence.current += 1
    setContactSearchLoading(false)
    setRecipient('')
    recipientEdited.current = false
    setContactSuggestions([])
    setContactMessage('')
    setPreview(null)
    setShowReview(true)
    void findContacts(targetUrl)
  }

  const closeReview = () => {
    contactRequestSequence.current += 1
    setContactSearchLoading(false)
    setShowReview(false)
    setPreview(null)
  }

  const requestPreview = async () => {
    if (count !== 1 || missingEvidence || previewLoading || !recipient.trim()) return
    setPreviewLoading(true)
    setPreview(null)
    setDispatchError('')
    try {
      const match = selectedMatches[0]
      const result = await previewTakedown(
        match.url,
        recipient.trim(),
        victimName.trim() || 'Aggrieved Individual',
        match.hash_signature as string,
      )
      setPreview(result)
      setRecipient(result.recipient)
    } catch (error) {
      setDispatchError(error instanceof Error ? error.message : 'Could not prepare the notice preview.')
    } finally {
      setPreviewLoading(false)
    }
  }

  const confirmDispatch = async () => {
    if (!preview || count !== 1 || missingEvidence || dispatchLoading) return
    setDispatchLoading(true)
    setDispatchError('')
    setDispatchMessage('')
    try {
      const result = await dispatchTakedown(preview.preview_id)
      setDispatchMessage(
        result.status === 'simulated_not_sent'
          ? 'Local test mode completed. No email was sent. To send real email, set NOTICE_EMAIL_MODE=resend and configure a valid Resend API key and verified sender domain.'
          : `Resend accepted the email for delivery to ${result.recipient} (reference: ${result.dispatch_id || 'not provided'}). Check your Resend dashboard for delivery status; acceptance does not mean the website has removed the content.`,
      )
      closeReview()
    } catch (error) {
      // A network error can leave provider acceptance uncertain. Do not reuse
      // this one-time preview, since doing so could accidentally duplicate a notice.
      setPreview(null)
      setDispatchError(error instanceof Error ? error.message : 'Notice dispatch failed. Check provider activity before retrying.')
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
      setDispatchError('Clipboard access was blocked by the browser. Copy the candidate details manually.')
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
            onClick={openReview}
            disabled={!canReviewNotice || dispatchLoading}
            className="w-full py-2.5 px-3.5 border border-blue-700 font-medium text-xs text-left bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white"
          >
            <span className="block font-semibold">Review legal notice</span>
            <span className="block text-[10px] opacity-80 mt-0.5">
              {count > 1 ? 'Select exactly one candidate for a notice.' : 'Check the website contact and draft before sending.'}
            </span>
          </button>
          {dispatchMessage && <p role="status" className="p-3 border border-emerald-800 bg-emerald-950/30 text-emerald-200 text-xs break-words">{dispatchMessage}</p>}
          {dispatchError && (
            <div className="p-3 border border-red-800 bg-red-950/30 text-red-200 text-xs break-words">
              <p>{dispatchError}</p>
              {/Please sign in|Session expired|sign in again/i.test(dispatchError) && <Link href="/login" className="inline-block mt-2 text-blue-300 underline">Sign in to continue</Link>}
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={handleDossier}
          disabled={!ready || dossierLoading}
          className="w-full py-2.5 px-3.5 border border-slate-700 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs text-left"
        >
          <span className="block font-semibold">{dossierLoading ? 'Generating PDF…' : 'Generate evidence report'}</span>
          <span className="block text-[10px] text-slate-400 mt-0.5">Review and confirm before export.</span>
        </button>
        {dossierError && <p role="alert" className="text-xs text-red-300">{dossierError} {(/sign in|session expired/i.test(dossierError)) && <Link href="/login" className="underline">Sign in</Link>}</p>}

        <button
          type="button"
          onClick={copySignatures}
          disabled={!ready}
          className="w-full py-2.5 px-3.5 border border-slate-700 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs text-left"
        >
          <span className="block font-semibold">{copied ? 'Candidate details copied' : 'Copy candidate evidence'}</span>
          <span className="block text-[10px] text-slate-400 mt-0.5">Copies the URL and actual available signature.</span>
        </button>
        <p className="pt-2 border-t border-slate-800 text-[11px] text-slate-400">
          Similarity candidates are not proof of a deepfake. Verify source evidence and notice details before sending.
        </p>
      </div>

      {showReview && typeof document !== 'undefined' && createPortal(
        <div
          className="fixed inset-0 z-[1000] flex items-start sm:items-center justify-center overflow-y-auto bg-slate-950/95 p-3 sm:p-6 backdrop-blur-sm"
          role="presentation"
          onMouseDown={event => { if (event.target === event.currentTarget && !dispatchLoading) closeReview() }}
        >
          <div
            className="relative z-[1001] isolate my-2 w-full max-w-3xl max-h-[calc(100dvh-1.5rem)] overflow-y-auto border border-slate-700 bg-slate-900 p-4 shadow-2xl sm:p-6 space-y-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="notice-review-title"
          >
            <div>
              <h2 id="notice-review-title" className="text-lg font-semibold text-white">Review before dispatch</h2>
              <p className="text-sm text-slate-300 mt-1">
                Check the discovered contact, edit the recipient if needed, and review the exact draft. A real email is sent only when Resend mode is enabled and you confirm.
              </p>
            </div>

            <div className="border border-slate-700 bg-slate-900 p-3 space-y-1">
              <p className="text-xs text-slate-100 font-medium">{targetDomain} · {selectedMatches[0] ? (selectedMatches[0].similarity * 100).toFixed(1) : '0'}% similarity candidate</p>
              <a href={targetUrl} target="_blank" rel="noopener noreferrer" className="block text-[11px] text-blue-300 underline break-all">{targetUrl}</a>
              <p className="text-[10px] text-slate-400 break-all">Evidence signature: {selectedMatches[0]?.hash_signature || 'Missing signature'}</p>
            </div>

            <div className="space-y-1">
              <label htmlFor="complainant-name" className="block text-xs text-slate-200">Complainant name</label>
              <input
                id="complainant-name"
                value={victimName}
                onChange={event => { setVictimName(event.target.value); setPreview(null) }}
                maxLength={120}
                placeholder="Aggrieved Individual"
                className="w-full border border-slate-600 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-blue-500"
              />
            </div>

            <div className="space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <label htmlFor="notice-recipient" className="block text-xs text-slate-200">Recipient email — editable</label>
                <button
                  type="button"
                  onClick={() => { void findContacts(targetUrl) }}
                  disabled={contactSearchLoading || dispatchLoading}
                  className="border border-slate-600 px-3 py-1.5 text-xs text-slate-100 hover:bg-slate-800 disabled:opacity-50"
                >
                  {contactSearchLoading ? 'Searching website…' : 'Search public contacts again'}
                </button>
              </div>
              <input
                id="notice-recipient"
                type="email"
                autoComplete="email"
                value={recipient}
                onChange={event => {
                  recipientEdited.current = true
                  setRecipient(event.target.value)
                  setPreview(null)
                }}
                maxLength={254}
                placeholder="contact@example.com"
                className="w-full border border-slate-600 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-blue-500"
              />
              {contactMessage && <p role="status" className="text-[11px] text-slate-300 break-words">{contactMessage}</p>}
              {contactSuggestions.length > 0 && (
                <div className="border border-slate-700 bg-slate-950 p-3 space-y-2">
                  <p className="text-xs font-medium text-slate-200">Public email addresses found on this website</p>
                  <div className="space-y-2">
                    {contactSuggestions.map(contact => (
                      <div key={contact.email} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 border-b border-slate-800 pb-2 last:border-b-0 last:pb-0">
                        <button
                          type="button"
                          onClick={() => {
                            recipientEdited.current = true
                            setRecipient(contact.email)
                            setPreview(null)
                          }}
                          className="text-left text-xs text-blue-200 hover:text-white break-all underline"
                        >
                          {contact.email}
                        </button>
                        <a
                          href={contact.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] text-slate-400 underline shrink-0"
                        >
                          View source page
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {missingEvidence && <p role="alert" className="text-xs text-red-300">This candidate has no evidence signature. Run a fresh search before dispatching.</p>}
            {dispatchError && <p role="alert" className="text-xs text-red-300 break-words">{dispatchError}</p>}

            <button
              type="button"
              onClick={requestPreview}
              disabled={!recipient.trim() || missingEvidence || previewLoading || dispatchLoading}
              className="border border-slate-600 px-4 py-2 text-sm text-slate-100 hover:bg-slate-800 disabled:opacity-50"
            >
              {previewLoading ? 'Preparing preview…' : 'Load recipient and notice preview'}
            </button>

            {preview && (
              <section className="border border-slate-700 bg-slate-950 p-3 space-y-2">
                <p className="text-sm font-semibold text-white">
                  Website: <span className="font-normal">{preview.target_domain}</span>
                </p>
                <p className="text-sm font-semibold text-white break-all">
                  Recipient: <span className="font-normal">{preview.recipient}</span>
                </p>
                {preview.delivery_mode === 'mock' ? (
                  <p className="text-[11px] text-amber-200">
                    Local test mode is active. Confirming exercises the workflow only; no email will be sent.
                  </p>
                ) : (
                  <p className="text-[11px] text-amber-200">
                    Verify the address and draft. Resend must have a verified sender domain and valid API key. Provider acceptance does not guarantee delivery or content removal.
                  </p>
                )}
                <label htmlFor="notice-text" className="block text-xs text-slate-200">Exact notice text to be sent</label>
                <textarea
                  id="notice-text"
                  readOnly
                  value={preview.notice_text}
                  rows={10}
                  className="w-full resize-y border border-slate-700 bg-slate-950 p-3 text-xs leading-relaxed text-slate-200 outline-none"
                />
              </section>
            )}

            <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 border-t border-slate-800 pt-3">
              <button
                type="button"
                onClick={closeReview}
                disabled={dispatchLoading || previewLoading}
                className="border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={confirmDispatch}
                disabled={!preview || dispatchLoading || previewLoading}
                className="border border-blue-500 bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
              >
                {dispatchLoading ? 'Submitting to Resend…' : preview?.delivery_mode === 'mock' ? 'Confirm test run — no email sent' : 'I reviewed the draft — send email'}
              </button>
            </div>
          </div>
        </div>,
        document.body,
      )}
    </aside>
  )
}
