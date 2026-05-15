import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../../config/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  language_name?: string
  needs_escalation?: boolean
}

const QUICK_REPLIES = [
  'What are your hours?',
  'Book an appointment',
  'Hair colour prices',
  'Cancel my booking',
]

export default function ChatbotWidget({ locationId }: { locationId?: string }) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi! I\'m AURA Chat. How can I help you today? 💆' }
  ])
  const [input, setInput] = useState('')
  const [sessionId] = useState(() => crypto.randomUUID())
  const bottomRef = useRef<HTMLDivElement>(null)

  const mutation = useMutation({
    mutationFn: (message: string) => api.post('/chatbot/message', {
      message,
      session_id: sessionId,
      location_id: locationId,
      history: messages.map(m => ({ role: m.role, content: m.content })),
    }).then(r => r.data.data),
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.reply,
        language_name: data.language_name,
        needs_escalation: data.needs_escalation,
      }])
    },
    onError: () => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I\'m having trouble connecting. Please try again.',
      }])
    },
  })

  const send = (text: string) => {
    if (!text.trim()) return
    const msg = text.trim()
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setInput('')
    mutation.mutate(msg)
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(o => !o)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-[#C9A96E] shadow-lg flex items-center justify-center text-2xl hover:bg-[#b8935a] transition-colors"
        aria-label="Open chat"
      >
        {open ? '✕' : '💬'}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-[360px] max-h-[520px] flex flex-col bg-[#0F0F1A] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="px-4 py-3 bg-[#C9A96E]/10 border-b border-white/10 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#C9A96E] flex items-center justify-center text-black text-sm font-bold">A</div>
              <div>
                <div className="text-sm font-semibold text-white">AURA Chat</div>
                <div className="text-xs text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full inline-block" />
                  Online · 6 languages
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed
                    ${m.role === 'user'
                      ? 'bg-[#C9A96E] text-black rounded-br-sm'
                      : 'bg-white/10 text-gray-100 rounded-bl-sm'}`}
                  >
                    {m.content}
                    {m.needs_escalation && (
                      <div className="mt-1 text-xs text-orange-300 border-t border-orange-500/20 pt-1">
                        🤝 Connecting you to a team member…
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {mutation.isPending && (
                <div className="flex justify-start">
                  <div className="bg-white/10 rounded-2xl rounded-bl-sm px-4 py-3">
                    <div className="flex gap-1">
                      {[0, 1, 2].map(i => (
                        <motion.div key={i} className="w-1.5 h-1.5 bg-gray-400 rounded-full"
                          animate={{ y: [0, -4, 0] }} transition={{ delay: i * 0.15, repeat: Infinity, duration: 0.8 }} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Quick replies */}
            {messages.length <= 1 && (
              <div className="px-4 pb-2 flex gap-2 overflow-x-auto scrollbar-none">
                {QUICK_REPLIES.map(r => (
                  <button
                    key={r}
                    onClick={() => send(r)}
                    className="shrink-0 text-xs border border-white/10 bg-white/5 rounded-full px-3 py-1.5 text-gray-300 hover:border-[#C9A96E]/50 hover:text-[#C9A96E] transition-colors"
                  >
                    {r}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="p-3 border-t border-white/10 flex gap-2">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send(input)}
                placeholder="Type in any language…"
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white placeholder-gray-600 outline-none focus:border-[#C9A96E]/50"
              />
              <button
                onClick={() => send(input)}
                disabled={!input.trim() || mutation.isPending}
                className="w-9 h-9 rounded-xl bg-[#C9A96E] text-black flex items-center justify-center hover:bg-[#b8935a] disabled:opacity-40 transition-colors"
              >
                ➤
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
