import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useAuthStore } from '../../stores/authStore'
import api from '../../config/api'

const GRADE_COLOR: Record<string, string> = {
  S: 'text-yellow-400',
  A: 'text-emerald-400',
  B: 'text-blue-400',
  C: 'text-orange-400',
  D: 'text-red-400',
}

const GRADE_BG: Record<string, string> = {
  S: 'bg-yellow-400/10 border-yellow-400/30',
  A: 'bg-emerald-400/10 border-emerald-400/30',
  B: 'bg-blue-400/10 border-blue-400/30',
  C: 'bg-orange-400/10 border-orange-400/30',
  D: 'bg-red-400/10 border-red-400/30',
}

function ScoreRing({ score, grade }: { score: number; grade: string }) {
  const r = 52
  const circ = 2 * Math.PI * r
  const dash = (score / 100) * circ
  return (
    <div className="relative flex items-center justify-center w-36 h-36">
      <svg className="absolute inset-0 -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={r} fill="none" stroke="#1a1a2e" strokeWidth="10" />
        <motion.circle
          cx="60" cy="60" r={r} fill="none"
          stroke={grade === 'S' ? '#f59e0b' : grade === 'A' ? '#34d399' : grade === 'B' ? '#60a5fa' : grade === 'C' ? '#fb923c' : '#f87171'}
          strokeWidth="10" strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - dash }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </svg>
      <div className="text-center">
        <div className={`text-3xl font-bold ${GRADE_COLOR[grade] ?? 'text-white'}`}>{score}</div>
        <div className={`text-xs font-semibold ${GRADE_COLOR[grade] ?? 'text-gray-400'}`}>Grade {grade}</div>
      </div>
    </div>
  )
}

function WeightBar({ label, value, max = 100 }: { label: string; value: number; max?: number }) {
  const pct = Math.min(100, (value / max) * 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span>{value.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-[#C9A96E] rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

export default function AuraScoreDashboard() {
  const { user } = useAuthStore()

  // For stylist: fetch own score. For manager: fetch branch leaderboard
  const stylistId = user?.staff_profile_id || user?.id
  const isManager = user?.role === 'salon_manager' || user?.role === 'super_admin' || user?.role === 'regional_manager'

  const { data: scoreData } = useQuery({
    queryKey: ['aurascore', 'stylist', stylistId],
    queryFn: () => api.get(`/aurascore/stylist/${stylistId}`).then(r => r.data.data),
    enabled: !!stylistId && !isManager,
  })

  const { data: leaderboard } = useQuery({
    queryKey: ['aurascore', 'network', 'leaderboard'],
    queryFn: () => api.get('/aurascore/network/leaderboard').then(r => r.data.data),
  })

  const score = scoreData?.current_score ?? 0
  const grade = scoreData?.grade ?? 'B'
  const breakdown = scoreData?.breakdown ?? {}
  const trend = scoreData?.trend_7d ?? 0

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-[#C9A96E]">AuraScore Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Your real-time performance intelligence</p>
        </div>

        {/* Score card */}
        {!isManager && scoreData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`border rounded-2xl p-6 flex gap-8 items-center ${GRADE_BG[grade] ?? 'bg-white/5 border-white/10'}`}
          >
            <ScoreRing score={Math.round(score)} grade={grade} />
            <div className="flex-1 space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-white font-semibold text-lg">
                  {scoreData.stylist_name ?? user?.first_name}
                </span>
                <span className={`text-sm font-bold px-2 py-0.5 rounded-full border ${GRADE_BG[grade]} ${GRADE_COLOR[grade]}`}>
                  {grade}
                </span>
                <span className={`text-xs ${trend >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {trend >= 0 ? '▲' : '▼'} {Math.abs(trend).toFixed(1)} pts this week
                </span>
              </div>
              <div className="space-y-2">
                <WeightBar label="Customer Rating (40%)" value={breakdown.customer_rating ?? 0} />
                <WeightBar label="SOP Compliance (25%)" value={breakdown.sop_compliance ?? 0} />
                <WeightBar label="Time Compliance (15%)" value={breakdown.time_compliance ?? 0} />
                <WeightBar label="Rebook Rate (10%)" value={breakdown.rebook_rate ?? 0} />
              </div>
              {breakdown.complaint_penalty > 0 && (
                <p className="text-xs text-red-400">
                  ⚠ Complaint penalty: -{breakdown.complaint_penalty?.toFixed(1)} pts
                </p>
              )}
            </div>
          </motion.div>
        )}

        {/* Network Leaderboard */}
        {leaderboard && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-[#C9A96E] mb-4">Network Leaderboard</h2>
            <div className="space-y-3">
              {(leaderboard.top_stylists ?? []).map((s: any, i: number) => (
                <motion.div
                  key={s.stylist_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex items-center gap-4 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                >
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                    ${i === 0 ? 'bg-yellow-400 text-black' : i === 1 ? 'bg-gray-300 text-black' : i === 2 ? 'bg-amber-600 text-white' : 'bg-white/10 text-gray-400'}`}>
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <div className="font-medium text-sm">{s.name}</div>
                    <div className="text-xs text-gray-500">{s.location}</div>
                  </div>
                  <span className={`text-sm font-bold ${GRADE_COLOR[s.grade] ?? 'text-white'}`}>
                    {s.score.toFixed(0)}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${GRADE_BG[s.grade] ?? ''} ${GRADE_COLOR[s.grade] ?? ''}`}>
                    {s.grade}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
