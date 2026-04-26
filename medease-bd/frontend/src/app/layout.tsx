import type { Metadata } from 'next'
import { Hind_Siliguri } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const hindSiliguri = Hind_Siliguri({
  subsets: ['latin', 'bengali'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-hind',
})

export const metadata: Metadata = {
  title: 'MedEase BD — Medicine Information Chatbot',
  description: 'AI-powered medicine information assistant for Bangladesh. Search 21,000+ Bangladeshi medicines in English and Bangla.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${hindSiliguri.variable} font-sans`}>
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  )
}
