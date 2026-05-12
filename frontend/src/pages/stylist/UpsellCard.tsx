import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import api from '../../config/api'

interface Suggestion {
  service: string
  reason: string
  acceptance_rate_pct: number
  revenue_uplift: number
  source: 'service_pairing' | 'beauty_passport' | 'milestone'
  free_offer?: string
}

function SourceBadge({ source }: { source: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    service_pairing:  { label: 'Popular pairing', cls: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
    beauty_passport:  { label: 'Beauty Passport', cls: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
    milestone:        { label: 'Milestone reward', cls: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' },
  }
  const { label, cls } = map[source] ?? { label: source, cls: 'bg-white/10 text-gray-300' }
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${cls}`}>{label}</span>
  )
}

export default function UpsellCard({ bookingId }: { bookingId: string }) {
  const qc = useQueryClient()
  const [accepted, setAccepted] = useState<string | null>(null)
  const [dismissed, setDismissed] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['upsell', bookingId],
    queryFn: () => api.get(`/upsell/booking/${bookingId}`).then(r => r.data.data),
    enabled: !!bookingId,
  })

  const acceptMut = useMutation({
    mutationFn: (service: string) =>
      api.post(`/upsell/booking/${bookingId}/accepted`, { service }),
    onSuccess: (_, service) => {
      setAccepted(service)
      qc.invalidateQueries({ queryKey: ['upsell', bookingId] })
    },
  })

  if (dismissed || !bookingId) return null
  if (isLoading) return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 animate-pulse h-24" />
  )

  const suggestions: Suggestion[] = data?.suggestions ?? []
  const totalUplift: number = data?.total_potential_uplift ?? 0

  if (!suggestions.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-[#1a1a2e] to-[#0A0A0F] border border-[#C9A96E]/30 rounded-2xl p-5 space-y-4"
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-[#C9A96E] font-semibold">Smart Upsell Suggestions</h3>
          <p className="text-xs text-gray-400 mt-0.5">
            Potential uplift: <span className="text-emerald-400 font-medium">₹{totalUplift.toLocaleString()}</span>
          </p>
        </div>
        <button onClick={() => setDismissed(true)} className="text-gray-600 hover:text-gray-400 text-sm">✕</button>
      </div>

      {/* Milestone offer (if any) */}
      {suggestions[0]?.free_offer && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-3 text-sm text-yellow-300">
          🎉 Milestone: Offer <strong>{suggestions[0].free_offer}</strong> — then mention the upgrade below!
        </div>
      )}

      {/* Suggestion cards */}
      <AnimatePresence>
        {suggestions.map((s, i) => (
          <motion.div
            key={s.service}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 8 }}
            transition={{ delay: i * 0.07 }}
            className={`border rounded-xl p-3 transition-all
              ${accepted === s.service
                ? 'border-emerald-500/50 bg-emerald-500/10'
                : 'border-white/10 bg-white/5 hover:border-[#C9A96E]/30'}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium text-sm text-white">{s.service}</span>
                  <SourceBadge source={s.source} />
                </div>
                <p className="text-xs text-gray-400">{s.reason}</p>
                <div className="flex gap-3 text-xs">
                  <span className="text-emerald-400">+₹{s.revenue_uplift}</span>
                  <span className="text-gray-500">{s.acceptance_rate_pct}% accept rate</span>
                </div>
              </div>
              <div>
                {accepted === s.service ? (
                  <span className="text-emerald-400 text-xs font-medium">✓ Added</span>
                ) : (
                  <button
                    onClick={() => acceptMut.mutate(s.service)}
                    disabled={acceptMut.isPending}
                    className="text-xs bg-[#C9A96E] text-black px-3 py-1.5 rounded-lg font-medium hover:bg-[#b8935a] transition-colors disabled:opacity-50"
                  >
                    Add
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </motion.div>
  )
}
