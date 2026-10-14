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
      q: 'How does DeepShield handle reference images?',
      a: 'Application code does not intentionally save reference image uploads or extracted vectors to its own database. Multipart handling, model caches, logs, server hosting and temporary files still need to be reviewed in the actual runtime before making formal compliance claims.',
    },
    {
      q: 'Does every report have the same legal deadline?',
      a: 'Deadlines and obligations depend on the applicable law, content category, facts and platform process. Review current official guidance or consult a qualified adviser before sending a legal notice; DeepShield does not determine legal eligibility or guarantee a removal deadline.',
    },
    {
      q: 'Does similarity scoring prove that an image is a deepfake?',
      a: 'No. Similarity scoring finds images that may resemble a reference; it does not establish that content is synthetic, non-consensual, illegal or an impersonation. Thresholds trade off candidate recall and false positives, so each result needs human verification.',
    },
    {
      q: 'What happens when I click "Dispatch Rule 3(1)(b) Notice"?',
      a: 'The operator must sign in, choose a destination, inspect the configured recipient and read the exact notice preview, then confirm. Actual sending requires a valid Resend API key and configured recipient. Provider acceptance does not mean a platform has removed the content.',
    },
    {
      q: 'Can DeepShield be deployed locally for complete data sovereignty?',
      a: 'The source can run locally, but public search providers, model downloads, hosting and email delivery have external requirements or limits. A local deployment does not itself establish compliance or guarantee operational cost is zero.',
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
            Image Similarity Search
          </span>
          <span className="block text-slate-200 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            and Candidate Review
          </span>
          <span className="block text-blue-500 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            Evidence Reporting
          </span>
        </h1>

        {/* Subtitle - 50% size of title, clear line height */}
        <p className="text-lg sm:text-xl md:text-2xl text-slate-400 max-w-3xl leading-[1.7] font-normal animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          A research prototype that searches public image results for similarity candidates, lets operators inspect source URLs, and prepares evidence reports or reviewed notice drafts. Similarity results are not proof of synthetic media.
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
            <div className="text-3xl font-bold font-mono text-slate-100">Not saved</div>
            <div className="text-xs text-slate-400 leading-normal">Persistent Biometric Storage</div>
          </div>
          <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-1">
            <div className="text-3xl font-bold font-mono text-slate-100">Review first</div>
            <div className="text-xs text-slate-400 leading-normal">Legal deadlines depend on the case</div>
          </div>
          <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-1">
            <div className="text-3xl font-bold font-mono text-slate-100">Open tools</div>
            <div className="text-xs text-slate-400 leading-normal">External providers may have limits or costs</div>
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
            Illustrative dashboard mock-up. Candidate figures and sample vectors below are examples, not live results from a scan.
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
              Example data only
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
              DeepShield combines image similarity analysis with public image search and operator-reviewed reporting. It helps organize candidate URLs for human review; it does not independently prove that an image is synthetic, determine legal liability or guarantee a takedown.
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
                <h3 className="text-base font-bold text-slate-100 font-display">In-memory image processing</h3>
                <span className="text-xs font-mono text-blue-400">Application behavior</span>
              </div>
              <p className="text-xs text-slate-400 leading-[1.7]">
                Reference uploads are processed in memory by the application and are not intentionally written to the account database. Model caches, server logs and the hosting environment require separate review before making any formal privacy-compliance claim.
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
                For a selected candidate, a signed-in operator can inspect a draft notice and configured recipient before confirming. Real sending requires live email mode, a valid provider key and independently verified contact details.
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
            Search image results and review candidates
          </h2>
          <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto leading-[1.7]">
            Upload a reference image, search public image results for similarity candidates, inspect the source URLs and optionally prepare an evidence report. Any notice must be reviewed before use.
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
              Public image similarity candidates, operator-reviewed evidence reports and a notice-preview workflow. Similarity does not establish that media is synthetic or unlawful.
            </p>
          </div>

          <div className="space-y-2.5">
            <h4 className="font-bold text-slate-200 font-display text-xs uppercase tracking-wider">Statutory Framework</h4>
            <ul className="space-y-2 font-mono text-[11px] text-slate-400">
              <li>Section 3(1)(b) IT Rules 2021</li>
              <li>Privacy claims depend on runtime and deployment</li>
              <li>pHash / optional PDQ candidate signatures</li>
            </ul>
          </div>

          <div className="space-y-2.5">
            <h4 className="font-bold text-slate-200 font-display text-xs uppercase tracking-wider">Open Architecture</h4>
            <ul className="space-y-2 font-mono text-[11px] text-slate-400">
              <li>Python FastAPI &amp; InsightFace</li>
              <li>Next.js 14 &amp; Tailwind CSS</li>
              <li>Open-source core; external services may have limits or costs</li>
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
