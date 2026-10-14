import type { Metadata } from 'next'
import HistoryClient from './HistoryClient'

export const metadata: Metadata = {
  title: 'Scan history',
}

export default function HistoryPage() {
  return <HistoryClient />
}
