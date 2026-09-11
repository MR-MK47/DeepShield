import type { Metadata } from 'next'
import { Inter, Space_Grotesk } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
})

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
})

export const metadata: Metadata = {
  title: {
    template: '%s | DeepShield',
    default: 'DeepShield | Autonomous Deepfake Eradication',
  },
  description: 'AI-Powered Deepfake Detection & Legal Takedown Platform — DPDP Act Compliant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`dark ${inter.variable} ${spaceGrotesk.variable}`}>
      <body className="font-sans bg-[#080c14] text-slate-100 min-h-screen selection:bg-blue-600/30 selection:text-blue-200">
        {children}
      </body>
    </html>
  )
}
