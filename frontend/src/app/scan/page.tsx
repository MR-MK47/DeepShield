import type { Metadata } from 'next'
import ScanClient from './ScanClient'

export const metadata: Metadata = {
  title: 'Scan',
}

export default function ScanPage() {
  return <ScanClient />
}
