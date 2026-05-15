import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useAuthStore } from '../../stores/authStore'
import api from '../../config/api'

const GRADE_CONFIG = {
  Excellent:       { color: '#C9A96E', bg: 'bg-yellow-400/10 border-yellow-400/20' },
  Good:            { color: '#34d399', bg: 'bg-emerald-400/10 border-emerald-400/20' },
  Fair:            { color: '#60a5fa', bg: 'bg-blue-400/10 border-blue-400/20' },
  'Needs Attention': { color: '#f87171', bg: 'bg-red-400/10 border-red-400/20' },
}

function HealthGauge({ score, grade }: { score: number; grade: string }) {
  const config = GRADE_CONFIG[grade as keyof typeof GRADE_CONFIG] ?? GRADE_CONFIG['Good']
  const r = 70
  const circ = 2 * Math.PI * r
  const filled = (score / 100) * circ

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-44 h-44">
        <svg className="absolute inset-0 -rotate-90" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r={r} fill="none" stroke="#1a1a2e" strokeWidth="12" />
          <motion.circle
            cx="80" cy="80" r={r} fill="none"
            stroke={config.color}
            strokeWidth="12" strokeLinecap="round"
            strokeDasharray={circ}
            initial={{ strokeDashoffset: circ }}
            animate={{ strokeDashoffset: circ - filled }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            className="text-5xl font-bold text-white"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {Math.round(score)}
          </motion.div>
          <div className="text-xs text-gray-400">/ 100</div>
        </div>
      </div>
      <div className={`text-sm font-semibold px-4 py-1 rounded-full border ${config.bg}`} style={{ color: config.color }}>
        {grade}
      </div>
    </div>
  )
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="text-white">{value.toFixed(0)}</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: `linear-gradient(90deg, #C9A96E, #f0c080)` }}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

function TimelineEntry({ entry, index }: { entry: any; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className="flex gap-4"
    >
      {/* Date spine */}
      <div className="flex flex-col items-center">
        <div className="w-3 h-3 rounded-full bg-[#C9A96E] shrink-0 mt-1" />
        {index < 9 && <div className="w-px flex-1 bg-white/10 mt-1" />}
      </div>
      <div className="flex-1 pb-5">
        <div className="text-xs text-gray-500 mb-1">{entry.date}</div>
        <div className="bg-white/5 border border-white/10 rounded-xl p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-white">{entry.service}</span>
            {entry.photo_url && (
              <img src={entry.photo_url} alt="before/after" className="w-10 h-10 rounded-lg object-cover border border-white/10" />
            )}
          </div>
          {(entry.skin_score !== undefined || entry.hair_score !== undefined) && (
            <div className="flex gap-4 text-xs text-gray-400">
              {entry.skin_score !== undefined && <span>Skin: <span className="text-[#C9A96E]">{entry.skin_score}</span></span>}
              {entry.hair_score !== undefined && <span>Hair: <span className="text-[#C9A96E]">{entry.hair_score}</span></span>}
              {entry.hydration_score !== undefined && <span>Hydration: <span className="text-[#C9A96E]">{entry.hydration_score}</span></span>}
            </div>
          )}
          {entry.notes && <p className="text-xs text-gray-500">{entry.notes}</p>}
        </div>
      </div>
    </motion.div>
  )
}

export default function BeautyTwinTimeline() {
  const { user } = useAuthStore()
  const customerId = (user as any)?.customer_profile_id ?? user?.id

  const { data, isLoading } = useQuery({
    queryKey: ['twin', 'timeline', customerId],
    queryFn: () => api.get(`/twin/timeline/${customerId}`).then(r => r.data.data),
    enabled: !!customerId,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
        <div className="space-y-3 text-center">
          <div className="w-24 h-24 rounded-full border-4 border-[#C9A96E]/30 border-t-[#C9A96E] animate-spin mx-auto" />
          <p className="text-gray-400 text-sm">Loading your beauty journey…</p>
        </div>
      </div>
    )
  }

  const score = data?.health_score ?? 0
  const grade = data?.grade ?? 'Good'
  const breakdown = data?.breakdown ?? {}
  const narrative = data?.ai_narrative ?? ''
  const timeline: any[] = data?.timeline ?? []

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white">
      {/* Header gradient */}
      <div className="bg-gradient-to-b from-[#1a1a2e] to-[#0A0A0F] px-6 py-8 text-center space-y-2">
        <p className="text-gray-400 text-sm">Your Digital Beauty Twin</p>
        <h1 className="text-2xl font-bold text-[#C9A96E]">Beauty Health Journey</h1>
      </div>

      <div className="max-w-lg mx-auto px-4 pb-10 space-y-8">
        {/* Health score */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center gap-6"
        >
          <HealthGauge score={score} grade={grade} />

          {/* Breakdown */}
          <div className="w-full bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
            <h3 className="text-xs text-gray-400 font-medium uppercase tracking-wide">Score Breakdown</h3>
            <ScoreBar label="Skin Health" value={breakdown.skin_score ?? 0} />
            <ScoreBar label="Hair Vitality" value={breakdown.hair_score ?? 0} />
            <ScoreBar label="Hydration" value={breakdown.hydration_score ?? 0} />
            <ScoreBar label="Visit Consistency" value={breakdown.consistency_score ?? 0} />
            <ScoreBar label="Progression" value={breakdown.progression_score ?? 0} />
          </div>
        </motion.div>

        {/* AI Narrative */}
        {narrative && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="bg-[#C9A96E]/5 border border-[#C9A96E]/20 rounded-2xl p-5"
          >
            <div className="flex gap-2 items-start">
              <span className="text-[#C9A96E] text-xl shrink-0">✨</span>
              <p className="text-gray-300 text-sm leading-relaxed">{narrative}</p>
            </div>
          </motion.div>
        )}

        {/* Stats strip */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Sessions', value: data?.total_sessions_analysed ?? 0 },
            { label: 'Top Service', value: data?.top_service ?? '—', small: true },
            { label: 'Score', value: `${Math.round(score)}/100` },
          ].map(stat => (
            <div key={stat.label} className="bg-white/5 border border-white/10 rounded-xl p-3 text-center">
              <div className={`font-bold text-[#C9A96E] ${stat.small ? 'text-xs' : 'text-xl'}`}>{stat.value}</div>
              <div className="text-xs text-gray-500 mt-0.5">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Timeline */}
        {timeline.length > 0 ? (
          <div>
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">Visit Timeline</h2>
            {timeline.slice().reverse().map((entry, i) => (
              <TimelineEntry key={i} entry={entry} index={i} />
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-600 text-sm py-8">
            No visits recorded yet. Your timeline will appear here after your first session.
          </div>
        )}
      </div>
    </div>
  )
}
