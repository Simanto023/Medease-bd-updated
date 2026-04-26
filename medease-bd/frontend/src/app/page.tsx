'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface Message {
  role: 'user' | 'assistant'
  content: string
  medicines?: any[]
  disclaimer?: string
}

const COMPANIES = ['All', 'Square', 'Beximco', 'Incepta', 'ACI', 'Opsonin', 'ACME']

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        '👋 Welcome to MedEase BD! I can help you find information about Bangladeshi medicines.\n\nআমি MedEase BD-এ আপনাকে স্বাগত জানাই! আমি বাংলাদেশী ওষুধ সম্পর্কে তথ্য দিতে পারি।',
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [companyFilter, setCompanyFilter] = useState('')
  const [activeCompany, setActiveCompany] = useState('All')
  const [language, setLanguage] = useState<'en' | 'bn'>('en')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const selectCompany = (name: string) => {
    setActiveCompany(name)
    setCompanyFilter(name === 'All' ? '' : name)
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post('/api/v1/chat', {
        query: input,
        company: companyFilter || null,
        language,
      })

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.data.response,
          medicines: response.data.medicines,
          disclaimer: response.data.disclaimer,
        },
      ])
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to get response')
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Sorry, I encountered an error. Please try again.\nদুঃখিত, একটি ত্রুটি ঘটেছে। অনুগ্রহ করে আবার চেষ্টা করুন।',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center shadow-sm">
              <span className="text-lg">💊</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 leading-tight">MedEase BD</h1>
              <p className="text-xs text-slate-500">21,208 Bangladeshi medicines</p>
            </div>
          </div>
          <button
            onClick={() => setLanguage(l => (l === 'en' ? 'bn' : 'en'))}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm font-medium text-slate-700 transition-colors"
          >
            {language === 'en' ? '🇧🇩 বাংলা' : '🇬🇧 English'}
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col px-4 py-4 gap-3">
        {/* Company filter pills */}
        <div className="flex gap-2 flex-wrap">
          {COMPANIES.map(c => (
            <button
              key={c}
              onClick={() => selectCompany(c)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                activeCompany === c
                  ? 'bg-primary-600 text-white border-primary-600 shadow-sm'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-primary-400 hover:text-primary-600'
              }`}
            >
              {c}
            </button>
          ))}
          {activeCompany !== 'All' && (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
              Filtering: {activeCompany}
            </span>
          )}
        </div>

        {/* Chat window */}
        <div className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col overflow-hidden" style={{ minHeight: '520px' }}>
          <div className="flex-1 overflow-y-auto p-5 space-y-4" style={{ maxHeight: '520px' }}>
            {messages.map((msg, idx) => (
              <div key={idx} className="space-y-2">
                <div className={`message-bubble ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>

                {msg.medicines && msg.medicines.length > 0 && (
                  <div className="ml-2 space-y-1.5">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      Related Medicines
                    </p>
                    <div className="grid gap-2">
                      {msg.medicines.map((med: any, i: number) => (
                        <div
                          key={i}
                          className="bg-slate-50 border border-slate-100 rounded-xl p-3 text-xs text-slate-700"
                        >
                          <p className="font-semibold text-slate-900">{med.brand_name}</p>
                          <p className="text-slate-500">{med.generic_name}</p>
                          <div className="flex gap-3 mt-1 text-slate-400">
                            <span>{med.company}</span>
                            {med.price_bdt ? <span>৳{med.price_bdt.toFixed(2)}</span> : null}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {msg.disclaimer && (
                  <p className="ml-2 text-xs text-slate-400 italic">{msg.disclaimer}</p>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="bot-message message-bubble flex items-center gap-2 text-slate-400 text-sm w-fit">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </span>
                Thinking…
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-slate-100 bg-slate-50/60">
            <div className="flex items-end gap-3">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  language === 'bn'
                    ? 'ওষুধ সম্পর্কে জিজ্ঞাসা করুন… (যেমন: নাপা, প্যারাসিটামল)'
                    : 'Ask about medicines… (e.g. Napa, Paracetamol)'
                }
                className="flex-1 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                rows={2}
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="px-5 py-2.5 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md active:scale-95"
              >
                {isLoading ? '…' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <footer className="text-center py-3 text-xs text-slate-400 border-t border-slate-200 bg-white">
        ⚠️ MedEase BD provides information for educational purposes only. Always consult healthcare professionals.
      </footer>
    </div>
  )
}
