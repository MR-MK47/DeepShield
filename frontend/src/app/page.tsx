'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(0)

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index)
  }

  const faqs = [
    {
      q: 'How does DeepShield comply with the DPDP Act 2023 zero-biometric mandate?',
      a: 'All reference photographs are vectorized in volatile RAM using InsightFace ArcFace (512-D float32 embeddings). The original image bytes and vector embeddings are discarded immediately after memory processing. Zero face vectors or reference images are persisted to disk or external databases.',
    },
    {
      q: 'What is the statutory timeline under Rule 3(1)(b) of the IT Rules 2021?',
      a: 'Rule 3(1)(b) of the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules 2021 requires social media intermediaries to acknowledge takedown notices within 24 hours and remove non-consensual synthetic or impersonation content within 36 hours of receipt.',
    },
    {
      q: 'How does cosine similarity scoring prevent false positives?',
      a: 'Candidates isolated by OSINT web crawling are evaluated against the 512-D reference vector using normalized cosine distance. The system defaults to a conservative 55% similarity threshold, allowing operators to manually adjust precision while inspecting natural aspect ratio thumbnails.',
    },
    {
      q: 'What happens when I click "Dispatch Rule 3(1)(b) Notice"?',
      a: 'DeepShield formats a legal takedown notice containing the target URL, platform grievance officer contact, timestamp, and non-consensual content declaration. Under strict Human-in-the-Loop design, notices are dispatched via SMTP only upon explicit operator confirmation.',
    },
    {
      q: 'Can DeepShield be deployed locally for complete data sovereignty?',
      a: 'Yes. DeepShield is built entirely on free, open-source technologies (FastAPI, InsightFace, DuckDuckGo Search, ReportLab, Next.js 14). The entire stack can be run locally or within private cloud infrastructure with zero operational SaaS costs.',
    },
  ]

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans selection:bg-blue-600/30 selection:text-blue-200">
      {/* 2. Company Logo & Sticky Navigation */}
      <header className="border-b border-slate-800 bg-[#080c14]/90 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-sm">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="text-lg font-bold text-slate-100 font-display tracking-tight">DeepShield</span>
          </Link>

          <div className="hidden md:flex items-center gap-8 text-xs text-slate-300 font-medium">
            <a href="#dashboard" className="hover:text-white transition-colors">Inspection Dashboard</a>
            <a href="#pipeline" className="hover:text-white transition-colors">Pipeline</a>
            <a href="#coverage" className="hover:text-white transition-colors">Grievance Conduits</a>
            <a href="#faq" className="hover:text-white transition-colors">Legal FAQ</a>
          </div>

          <div className="flex items-center gap-4 text-xs font-medium">
            <Link href="/login" className="text-slate-300 hover:text-white transition-colors hidden sm:block">
              Sign In
            </Link>
            <Link
              href="/scan"
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-4 py-2.5 rounded-lg transition-all shadow-sm hover:scale-105"
            >
              Launch Scan Console
            </Link>
          </div>
        </div>
      </header>

      {/* 3, 4, 5. Hero Section (MASSIVE Display Title, Subtitle, Primary CTA, Social Proof) */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-16 space-y-10 text-left">
        {/* MASSIVE H1 Display Typography with Staggered Reveal */}
        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-bold font-display text-slate-100 tracking-tight leading-[1.08]">
          <span className="block animate-fade-in-up" style={{ animationDelay: '0ms' }}>
            Autonomous Deepfake
          </span>
          <span className="block text-slate-200 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            Eradication and Rule 3(1)(b)
          </span>
          <span className="block text-blue-500 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            Legal Notice Dispatch
          </span>
        </h1>

        {/* Subtitle - 50% size of title, clear line height */}
        <p className="text-lg sm:text-xl md:text-2xl text-slate-400 max-w-3xl leading-[1.7] font-normal animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          An open-source OSINT crawling platform that scans public web endpoints for non-consensual visual impersonations, extracts 512-D ArcFace vectors in RAM, and dispatches statutory IT Rules 2021 grievance notices.
        </p>

        {/* Primary CTA Buttons */}
        <div className="flex flex-wrap items-center gap-4 pt-2 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
          <Link
            href="/scan"
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-base sm:text-lg px-8 py-4 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-blue-500/25 cursor-pointer shadow-md flex items-center gap-3"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Start Free Scan</span>
          </Link>

          <a
            href="#dashboard"
            className="bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 font-medium px-6 py-4 rounded-xl transition-all text-base hover:text-white"
          >
            Inspect System Dashboard
          </a>
        </div>

        {/* 5. Credibility Metrics & Social Proof */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-12 border-t border-slate-800/80">
          <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-1">
            <div className="text-3xl font-bold font-mono text-slate-100">512-D</div>
            <div className="text-xs text-slate-400 leading-normal">InsightFace ArcFace Embeddings</div>
          </div>
          <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-1">
            <div className="text-3xl font-bold font-mono text-slate-100">0 Bytes</div>
            <div className="text-xs text-slate-400 leading-normal">Persistent Biometric Storage</div>
          </div>
          <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-1">
            <div className="text-3xl font-bold font-mono text-slate-100">36 Hours</div>
            <div className="text-xs text-slate-400 leading-normal">Statutory IT Rules Window</div>
          </div>
          <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-1">
            <div className="text-3xl font-bold font-mono text-slate-100">100% Free</div>
            <div className="text-xs text-slate-400 leading-normal">Open-Source Python Stack</div>
          </div>
        </div>
      </section>

      {/* 6. Media Section: Mock Forensic Dashboard Frame with Depth */}
      <section id="dashboard" className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800 w-full space-y-6">
        <div className="space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold font-display text-slate-100 tracking-tight leading-[1.2]">
            Forensic Inspection Dashboard &amp; Analysis Terminal
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl leading-[1.6]">
            Real-time visual demonstration of in-memory vector extraction, OSINT web endpoint discovery, and cosine similarity metric scoring.
          </p>
        </div>

        {/* Dashboard Mock Container with Depth */}
        <div className="relative rounded-2xl border border-slate-800 bg-[#0f172a]/95 shadow-2xl p-6 sm:p-8 space-y-6 overflow-hidden">
          {/* Top Mock Window Bar */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-slate-800 border border-slate-700" />
              <span className="w-3 h-3 rounded-full bg-slate-800 border border-slate-700" />
              <span className="w-3 h-3 rounded-full bg-slate-800 border border-slate-700" />
              <span className="font-mono text-slate-400 ml-2 font-semibold">DeepShield OSINT Console — Active Search Session</span>
            </div>
            <span className="px-2.5 py-0.5 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-400 font-mono text-[11px]">
              DPDP Act Compliant (RAM Vector Purge Active)
            </span>
          </div>

          {/* Inner Dashboard Layout Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-mono text-xs">
            {/* Column 1: Reference Target Vector */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="text-slate-300 font-bold uppercase tracking-wider text-[11px] font-sans">
                Target Reference Vector
              </div>
              <div className="space-y-1.5 text-slate-400 text-[11px]">
                <p><span className="text-slate-500">Extraction Engine:</span> InsightFace ArcFace</p>
                <p><span className="text-slate-500">Dimension:</span> 512-float32 array</p>
                <p><span className="text-slate-500">PDQ Hash:</span> <span className="text-blue-400">pdq:e3f89a20b17492c1</span></p>
                <p><span className="text-slate-500">Status:</span> Ephemeral memory lock</p>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800 text-[10px] text-slate-400 overflow-x-auto">
                [0.0412, -0.1983, 0.5124, 0.0891, -0.3210, ...]
              </div>
            </div>

            {/* Column 2: Isolated Candidates List */}
            <div className="lg:col-span-2 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-slate-300 font-bold uppercase tracking-wider text-[11px] font-sans">
                <span>Isolated Candidate Endpoints</span>
                <span className="text-emerald-400 font-mono">2 Candidates Exceeding Threshold (55%)</span>
              </div>

              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between gap-4">
                  <div className="space-y-0.5 truncate">
                    <span className="px-2 py-0.5 rounded bg-red-950/60 border border-red-800 text-red-300 font-mono text-[10px] font-bold">
                      84.2% Match
                    </span>
                    <p className="text-slate-300 font-sans font-medium text-xs truncate">https://example-social.com/public/post/deepfake_img_89.jpg</p>
                    <p className="text-[10px] text-slate-500">Host Domain: example-social.com &middot; Notice Target: Meta Grievance Conduit</p>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-blue-600 text-white font-sans text-xs font-semibold shrink-0">
                    Dispatch Notice
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between gap-4">
                  <div className="space-y-0.5 truncate">
                    <span className="px-2 py-0.5 rounded bg-blue-950/60 border border-blue-800 text-blue-300 font-mono text-[10px] font-bold">
                      63.5% Match
                    </span>
                    <p className="text-slate-300 font-sans font-medium text-xs truncate">https://candidate-video-host.net/v/synthetic_media_01.webp</p>
                    <p className="text-[10px] text-slate-500">Host Domain: candidate-video-host.net &middot; Notice Target: Intermediary Legal</p>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-blue-600 text-white font-sans text-xs font-semibold shrink-0">
                    Dispatch Notice
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Core Benefits: Asymmetric Pipeline Layout */}
      <section id="pipeline" className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800 w-full space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start">
          {/* Left Column (2/5): Section Title & Thesis */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-2xl sm:text-4xl font-bold font-display text-slate-100 tracking-tight leading-[1.15]">
              Asymmetric Forensic &amp; Legal Infrastructure
            </h2>
            <p className="text-sm text-slate-400 leading-[1.7]">
              DeepShield decouples visual feature extraction from permanent storage. By combining InsightFace ArcFace vectors with OSINT crawling and statutory grievance templates, operators execute end-to-end takedowns without privacy liability.
            </p>
            <div className="pt-2">
              <Link
                href="/scan"
                className="inline-flex items-center gap-2 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
              >
                <span>Execute reference scan console</span>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </Link>
            </div>
          </div>

          {/* Right Column (3/5): Asymmetric Feature Stack */}
          <div className="lg:col-span-3 space-y-4">
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-100 font-display">In-Memory Biometric Isolation</h3>
                <span className="text-xs font-mono text-blue-400">DPDP Act 2023</span>
              </div>
              <p className="text-xs text-slate-400 leading-[1.7]">
                Reference photos uploaded to `/api/analyze` are processed in RAM to extract 512-D ArcFace vectors. Both reference images and vector arrays are purged immediately post-scan.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-100 font-display">OSINT Web Endpoint Discovery</h3>
                <span className="text-xs font-mono text-blue-400">DuckDuckGo Engine</span>
              </div>
              <p className="text-xs text-slate-400 leading-[1.7]">
                The backend queries public image search indexes using combined target names and synthetic media terms, retrieving candidate thumbnails into ephemeral RAM for vector comparison.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-100 font-display">Statutory Grievance Generation</h3>
                <span className="text-xs font-mono text-blue-400">IT Rules 2021</span>
              </div>
              <p className="text-xs text-slate-400 leading-[1.7]">
                Selected candidate matches trigger automated formatting of statutory Rule 3(1)(b) legal takedown notices, mapped directly to designated host platform Grievance Officers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Intermediary Platform Grievance Coverage */}
      <section id="coverage" className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800 w-full space-y-8">
        <div className="space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold font-display text-slate-100 tracking-tight leading-[1.2]">
            Intermediary Platform Grievance Conduits
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl leading-[1.6]">
            Pre-configured legal notice dispatch routing targeting major host platforms under Section 3(1)(b) of the IT Rules 2021.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="text-xs font-bold font-mono text-slate-200">Meta / Facebook</div>
            <p className="text-xs font-mono text-slate-400 truncate">fbgoindia@support.facebook.com</p>
            <span className="inline-block text-[10px] font-mono text-blue-400 bg-blue-950/50 px-2 py-0.5 rounded border border-blue-800">
              Statutory 36h Takedown
            </span>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="text-xs font-bold font-mono text-slate-200">Google / YouTube</div>
            <p className="text-xs font-mono text-slate-400 truncate">abuse@google.com</p>
            <span className="inline-block text-[10px] font-mono text-blue-400 bg-blue-950/50 px-2 py-0.5 rounded border border-blue-800">
              Statutory 36h Takedown
            </span>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="text-xs font-bold font-mono text-slate-200">X (Twitter)</div>
            <p className="text-xs font-mono text-slate-400 truncate">abuse@x.com</p>
            <span className="inline-block text-[10px] font-mono text-blue-400 bg-blue-950/50 px-2 py-0.5 rounded border border-blue-800">
              Statutory 36h Takedown
            </span>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="text-xs font-bold font-mono text-slate-200">TikTok / ByteDance</div>
            <p className="text-xs font-mono text-slate-400 truncate">legal@tiktok.com</p>
            <span className="inline-block text-[10px] font-mono text-blue-400 bg-blue-950/50 px-2 py-0.5 rounded border border-blue-800">
              Statutory 36h Takedown
            </span>
          </div>
        </div>
      </section>

      {/* 9. Interactive Legal & Technical FAQ Section */}
      <section id="faq" className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800 w-full space-y-8">
        <div className="space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold font-display text-slate-100 tracking-tight leading-[1.2]">
            Legal &amp; Technical Accordion FAQ
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 leading-[1.6]">
            Verification of DPDP Act compliance, cosine similarity thresholds, and human-in-the-loop controls.
          </p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <div key={index} className="border border-slate-800 rounded-xl bg-slate-900/60 overflow-hidden">
              <button
                type="button"
                onClick={() => toggleFaq(index)}
                className="w-full p-4 text-left font-semibold text-xs sm:text-sm text-slate-200 flex items-center justify-between gap-4 hover:bg-slate-800/50 transition-colors font-display"
              >
                <span>{faq.q}</span>
                <svg
                  className={`w-4 h-4 text-slate-400 transition-transform duration-200 shrink-0 ${openFaq === index ? 'rotate-180 text-blue-400' : ''}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {openFaq === index && (
                <div className="p-4 pt-0 text-xs sm:text-sm text-slate-400 border-t border-slate-800/60 leading-[1.7] font-sans">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 10. Dramatic Final Conversion CTA Section */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800 w-full">
        <div className="p-10 sm:p-14 rounded-3xl bg-slate-900 border border-slate-800 text-center shadow-2xl space-y-6">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-slate-100 tracking-tight leading-[1.15]">
            Execute Forensic Search &amp; Eradicate Deepfakes
          </h2>
          <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto leading-[1.7]">
            Upload reference media, extract 512-D ArcFace vectors in RAM, and dispatch statutory Rule 3(1)(b) IT Rules legal notices.
          </p>
          <div>
            <Link
              href="/scan"
              className="inline-flex items-center gap-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-10 py-5 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/30 text-base sm:text-lg cursor-pointer"
            >
              <span>Launch Free Scan Console</span>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* 11. Refined Multi-Column Legal Footer */}
      <footer className="border-t border-slate-800 py-12 text-xs text-slate-400 bg-[#080c14] mt-auto">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-slate-800/80">
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded bg-blue-600 flex items-center justify-center font-bold text-white text-xs">
                DS
              </div>
              <span className="font-bold text-slate-200 font-display text-base">DeepShield</span>
            </div>
            <p className="text-xs text-slate-400 leading-[1.7] max-w-md">
              AI-Powered Deepfake Search &amp; Eradication Engine. Extracts zero-biometric ArcFace vectors in RAM and automates Rule 3(1)(b) IT Rules 2021 statutory takedown notices.
            </p>
          </div>

          <div className="space-y-2.5">
            <h4 className="font-bold text-slate-200 font-display text-xs uppercase tracking-wider">Statutory Framework</h4>
            <ul className="space-y-2 font-mono text-[11px] text-slate-400">
              <li>Section 3(1)(b) IT Rules 2021</li>
              <li>DPDP Act 2023 Compliance</li>
              <li>PDQ &amp; pHash NCII Standards</li>
            </ul>
          </div>

          <div className="space-y-2.5">
            <h4 className="font-bold text-slate-200 font-display text-xs uppercase tracking-wider">Open Architecture</h4>
            <ul className="space-y-2 font-mono text-[11px] text-slate-400">
              <li>Python FastAPI &amp; InsightFace</li>
              <li>Next.js 14 &amp; Tailwind CSS</li>
              <li>100% Free Open Stack</li>
            </ul>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-6 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-[11px] text-slate-500">
          <p>&copy; {new Date().getFullYear()} DeepShield Project. All rights reserved.</p>
          <p>Zero Biometric Persistence Guarantee</p>
        </div>
      </footer>
    </div>
  )
}
