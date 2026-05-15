import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { AlertTriangle, Star, Heart, Zap, TrendingUp, FileText } from 'lucide-react'
import api from '../../config/api'

interface BriefData {
  customer_name: string
  skin_profile?: { type?: string; concerns?: string[] }
  hair_profile?: { type?: string; texture?: string; color?: string; damage_level?: number }
  known_allergies?: string[]
  allergy_risk?: { risk_level: string; reason?: string; safe_alternative?: string }
  last_3_services?: Array<{ service: string; date: string; rating?: number }>
  visit_goal?: string
  visit_intent?: string
  soulskin_mood?: string
  upsell_tip?: string
  ai_briefing?: string
  consultation?: {
    hair_type?: string
    skin_type?: string
    visit_goal?: string
    health_conditions?: string[]
    is_pregnant?: boolean
  }
}

const RISK_STYLE: Record<string, { bg: string; text: string; border: string }> = {
  BLOCK:   { bg: 'bg-red-500/10',    text: 'text-red-400',    border: 'border-red-500/30' },
  HIGH:    { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30' },
  CAUTION: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  LOW:     { bg: 'bg-emerald-500/10',text: 'text-emerald-400',border: 'border-emerald-500/30' },
}

export default function CustomerBriefCard({ bookingId }: { bookingId: string }) {
  const { data, isLoading } = useQuery<BriefData>({
    queryKey: ['customer-brief', bookingId],
    queryFn: () => api.get(`/consultation/booking/${bookingId}/briefing`).then(r => r.data.data),
    enabled: !!bookingId,
    staleTime: 300_000,
  })

  if (isLoading) {
    return <div className="bg-white/5 border border-white/10 rounded-2xl p-4 animate-pulse h-32" />
  }
  if (!data) return null

  const allergies = data.known_allergies ?? []
  const risk = data.allergy_risk
  const riskStyle = RISK_STYLE[risk?.risk_level ?? 'LOW']
  const lastServices = data.last_3_services ?? []
  const consultation = data.consultation

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-[#0F0F1A] to-[#1a1a2e] border border-white/10 rounded-2xl p-5 space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText size={16} className="text-[#C9A96E]" />
          <span className="text-sm font-bold text-[#C9A96E]">Customer Brief</span>
        </div>
        <span className="text-xs text-gray-500">{data.customer_name}</span>
      </div>

      {/* Allergy risk banner */}
      {risk && risk.risk_level !== 'LOW' && (
        <div className={`rounded-xl p-3 border ${riskStyle.bg} ${riskStyle.border}`}>
          <div className={`flex items-center gap-2 font-bold text-sm ${riskStyle.text}`}>
            <AlertTriangle size={14} />
            {risk.risk_level} ALLERGY RISK
          </div>
          {risk.reason && <p className="text-xs text-gray-400 mt-1">{risk.reason}</p>}
          {risk.safe_alternative && (
            <p className="text-xs text-emerald-400 mt-1">✓ Safe: {risk.safe_alternative}</p>
          )}
        </div>
      )}

      {/* Known allergies */}
      {allergies.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1.5 font-medium uppercase tracking-wide">Known Allergies</div>
          <div className="flex flex-wrap gap-1.5">
            {allergies.map(a => (
              <span key={a} className="text-xs px-2 py-0.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-full">{a}</span>
            ))}
          </div>
        </div>
      )}

      {/* Consultation answers */}
      {consultation && (
        <div className="grid grid-cols-2 gap-2 text-xs">
          {consultation.hair_type && (
            <div className="bg-white/5 rounded-lg p-2">
              <div className="text-gray-500">Hair Type</div>
              <div className="text-white font-medium">{consultation.hair_type}</div>
            </div>
          )}
          {consultation.skin_type && (
            <div className="bg-white/5 rounded-lg p-2">
              <div className="text-gray-500">Skin Type</div>
              <div className="text-white font-medium">{consultation.skin_type}</div>
            </div>
          )}
          {consultation.visit_goal && (
            <div className="bg-white/5 rounded-lg p-2 col-span-2">
              <div className="text-gray-500">Visit Goal</div>
              <div className="text-white font-medium">{consultation.visit_goal}</div>
            </div>
          )}
          {consultation.is_pregnant && (
            <div className="col-span-2 bg-orange-500/10 border border-orange-500/20 rounded-lg p-2 text-orange-300 font-semibold">
              ⚠️ Pregnant — avoid chemical services
            </div>
          )}
          {(consultation.health_conditions ?? []).length > 0 && (
            <div className="col-span-2 bg-white/5 rounded-lg p-2">
              <div className="text-gray-500">Health Conditions</div>
              <div className="text-white font-medium">{consultation.health_conditions!.join(', ')}</div>
            </div>
          )}
        </div>
      )}

      {/* Visit goal / mood */}
      <div className="flex gap-2 flex-wrap">
        {data.visit_goal && (
          <span className="text-xs px-2 py-1 bg-purple-500/10 border border-purple-500/20 text-purple-300 rounded-full flex items-center gap-1">
            <TrendingUp size={10} /> {data.visit_goal}
          </span>
        )}
        {data.soulskin_mood && (
          <span className="text-xs px-2 py-1 bg-pink-500/10 border border-pink-500/20 text-pink-300 rounded-full flex items-center gap-1">
            <Heart size={10} /> {data.soulskin_mood}
          </span>
        )}
      </div>

      {/* Last 3 services */}
      {lastServices.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1.5 font-medium uppercase tracking-wide">Last Visits</div>
          <div className="space-y-1">
            {lastServices.map((s, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="text-gray-300">{s.service}</span>
                <div className="flex items-center gap-2">
                  <span className="text-gray-600">{s.date ? new Date(s.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}</span>
                  {s.rating && (
                    <span className="text-yellow-400 flex items-center gap-0.5">
                      <Star size={9} fill="currentColor" /> {s.rating}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI upsell tip */}
      {data.upsell_tip && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3">
          <div className="text-xs font-bold text-emerald-400 flex items-center gap-1 mb-1">
            <Zap size={10} /> UPSELL TIP
          </div>
          <p className="text-xs text-gray-300">{data.upsell_tip}</p>
        </div>
      )}

      {/* AI stylist briefing */}
      {data.ai_briefing && (
        <div className="bg-[#C9A96E]/5 border border-[#C9A96E]/15 rounded-xl p-3">
          <div className="text-xs font-bold text-[#C9A96E] mb-1">AI Briefing</div>
          <p className="text-xs text-gray-300 leading-relaxed">{data.ai_briefing}</p>
        </div>
      )}
    </motion.div>
  )
}
