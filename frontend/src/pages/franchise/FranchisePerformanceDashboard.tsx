import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../lib/api'

type BranchStatus = 'healthy' | 'at_risk' | 'critical'

interface Branch {
  location_id: string
  name: string
  city: string
  state: string
  revenue_this_week: number
  revenue_wow_pct: number
  aurascore_avg: number
  attrition_risk_staff: number
  inventory_alerts: number
  retention_rate_pct: number
  status: BranchStatus
}

interface Anomaly {
  location_id: string
  name: string
  city: string
  revenue_drop_pct: number
  root_cause: string
  recommended_action: string
}

const STATUS_STYLE: Record<BranchStatus, { dot: string; badge: string; label: string }> = {
  healthy:  { dot: 'bg-emerald-400', badge: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20', label: 'Healthy' },
  at_risk:  { dot: 'bg-amber-400',   badge: 'bg-amber-400/10 text-amber-400 border-amber-400/20',     label: 'At Risk' },
  critical: { dot: 'bg-red-400',     badge: 'bg-red-400/10 text-red-400 border-red-400/20',           label: 'Critical' },
}

const ROOT_CAUSE_LABEL: Record<string, string> = {
  staff_risk:       '👥 Staff Risk',
  inventory:        '📦 Inventory',
  quality:          '⭐ Quality Drop',
  low_demand:       '📉 Low Demand',
  multiple_factors: '⚠ Multiple',
}

type SortKey = 'revenue' | 'quality' | 'retention'

function StatCard({ label, value, sub, accent }: { label: string; value: string | number; sub?: string; accent?: string }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className="text-2xl font-bold" style={{ color: accent ?? '#C9A96E' }}>{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
    </div>
  )
}

function BranchRow({ branch, rank, onClick }: { branch: Branch; rank?: number; onClick: () => void }) {
  const s = STATUS_STYLE[branch.status]
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onClick}
      className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10 hover:border-[#C9A96E]/30 hover:bg-white/8 cursor-pointer transition-all"
    >
      {rank !== undefined && (
        <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0
          ${rank === 0 ? 'bg-yellow-400 text-black' : rank === 1 ? 'bg-gray-300 text-black' : rank === 2 ? 'bg-amber-600 text-white' : 'bg-white/10 text-gray-400'}`}>
          {rank + 1}
        </span>
      )}
      <div className={`w-2 h-2 rounded-full shrink-0 ${s.dot}`} />
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm text-white truncate">{branch.name}</div>
        <div className="text-xs text-gray-500">{branch.city}</div>
      </div>
      <div className="text-right shrink-0">
        <div className="text-sm font-semibold text-white">₹{(branch.revenue_this_week / 1000).toFixed(0)}K</div>
        <div className={`text-xs ${branch.revenue_wow_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
          {branch.revenue_wow_pct >= 0 ? '+' : ''}{branch.revenue_wow_pct.toFixed(1)}%
        </div>
      </div>
      <div className="text-right shrink-0 hidden sm:block">
        <div className="text-sm text-white">{branch.aurascore_avg}</div>
        <div className="text-xs text-gray-500">AuraScore</div>
      </div>
      <div className="text-right shrink-0 hidden md:block">
        <div className="text-sm text-white">{branch.retention_rate_pct}%</div>
        <div className="text-xs text-gray-500">Retention</div>
      </div>
      <span className={`text-xs px-2 py-0.5 rounded-full border shrink-0 ${s.badge}`}>{s.label}</span>
    </motion.div>
  )
}

export default function FranchisePerformanceDashboard() {
  const navigate = useNavigate()
  const [view, setView] = useState<'overview' | 'anomalies' | 'top10' | 'bottom10' | 'all'>('overview')
  const [sortKey, setSortKey] = useState<SortKey>('revenue')
  const [digest, setDigest] = useState<string | null>(null)
  const [loadingDigest, setLoadingDigest] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['franchise-dashboard', 'overview'],
    queryFn: () => api.get('/franchise-dashboard/overview').then(r => r.data.data),
    staleTime: 60_000,
  })

  const fetchDigest = async () => {
    setLoadingDigest(true)
    try {
      const res = await api.get('/franchise-dashboard/weekly-digest')
      setDigest(res.data.data.digest)
    } finally {
      setLoadingDigest(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 rounded-full border-2 border-[#C9A96E]/30 border-t-[#C9A96E] animate-spin mx-auto" />
          <p className="text-gray-400 text-sm">Loading network data…</p>
        </div>
      </div>
    )
  }

  const branches: Branch[] = data?.branches ?? []
  const anomalies: Anomaly[] = data?.anomalies ?? []
  const sortedBranches = [...branches].sort((a, b) => {
    if (sortKey === 'revenue') return b.revenue_this_week - a.revenue_this_week
    if (sortKey === 'quality') return b.aurascore_avg - a.aurascore_avg
    return b.retention_rate_pct - a.retention_rate_pct
  })
  const top10 = data?.top_10_by_retention ?? []
  const bottom10 = data?.bottom_10_by_retention ?? []

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white p-6">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#C9A96E]">Franchise Performance Dashboard</h1>
            <p className="text-gray-400 text-sm mt-1">{data?.total_branches ?? 0} branches · Live network overview</p>
          </div>
          <button
            onClick={fetchDigest}
            disabled={loadingDigest}
            className="text-sm bg-white/5 border border-white/10 px-4 py-2 rounded-xl hover:border-[#C9A96E]/40 transition-colors disabled:opacity-50"
          >
            {loadingDigest ? 'Generating…' : '📋 Weekly Digest'}
          </button>
        </div>

        {/* AI Digest */}
        {digest && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-[#C9A96E]/5 border border-[#C9A96E]/20 rounded-2xl p-5 whitespace-pre-line text-sm text-gray-300 leading-relaxed"
          >
            <div className="text-xs text-[#C9A96E] font-semibold mb-2">AI Weekly Digest</div>
            {digest}
          </motion.div>
        )}

        {/* Network KPI cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard
            label="Network Revenue (7d)"
            value={`₹${((data?.network_revenue_this_week ?? 0) / 100000).toFixed(1)}L`}
            sub={`${data?.network_revenue_wow_pct >= 0 ? '+' : ''}${(data?.network_revenue_wow_pct ?? 0).toFixed(1)}% WoW`}
          />
          <StatCard label="Total Branches" value={data?.total_branches ?? 0} />
          <StatCard
            label="Critical Branches"
            value={data?.critical_branches ?? 0}
            accent={data?.critical_branches > 0 ? '#f87171' : '#34d399'}
            sub="Revenue drop > 20%"
          />
          <StatCard
            label="At-Risk Branches"
            value={data?.at_risk_branches ?? 0}
            accent={data?.at_risk_branches > 3 ? '#fb923c' : '#C9A96E'}
            sub="Staff / inventory alerts"
          />
        </div>

        {/* Anomaly alerts */}
        {anomalies.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-red-400 uppercase tracking-wide">
              🚨 Revenue Anomalies — Branches Need Attention
            </h2>
            {anomalies.map(a => (
              <motion.div
                key={a.location_id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-red-500/5 border border-red-500/20 rounded-xl p-4 flex gap-4 items-start cursor-pointer hover:border-red-500/40 transition-colors"
                onClick={() => navigate(`/admin/locations/${a.location_id}`)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-sm text-white">{a.name}</span>
                    <span className="text-xs text-gray-400">{a.city}</span>
                    <span className="text-xs px-2 py-0.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-full">
                      -{a.revenue_drop_pct}% WoW
                    </span>
                    <span className="text-xs px-2 py-0.5 bg-white/5 border border-white/10 rounded-full">
                      {ROOT_CAUSE_LABEL[a.root_cause] ?? a.root_cause}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{a.recommended_action}</p>
                </div>
                <span className="text-gray-600 text-sm shrink-0">→</span>
              </motion.div>
            ))}
          </div>
        )}

        {/* View switcher */}
        <div className="flex gap-2 flex-wrap">
          {([
            ['overview', 'Overview'],
            ['top10', 'Top 10'],
            ['bottom10', 'Bottom 10'],
            ['all', 'All Branches'],
          ] as [string, string][]).map(([v, label]) => (
            <button
              key={v}
              onClick={() => setView(v as typeof view)}
              className={`text-sm px-4 py-2 rounded-xl border transition-colors
                ${view === v ? 'border-[#C9A96E] bg-[#C9A96E]/10 text-[#C9A96E]' : 'border-white/10 text-gray-400 hover:border-white/30'}`}
            >
              {label}
            </button>
          ))}
          {view === 'all' && (
            <div className="flex gap-2 ml-auto">
              {(['revenue', 'quality', 'retention'] as SortKey[]).map(k => (
                <button
                  key={k}
                  onClick={() => setSortKey(k)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-colors
                    ${sortKey === k ? 'border-[#C9A96E]/50 bg-[#C9A96E]/10 text-[#C9A96E]' : 'border-white/10 text-gray-500'}`}
                >
                  {k}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Branch list */}
        <div className="space-y-2">
          {view === 'overview' && branches.slice(0, 15).map((b, i) => (
            <BranchRow key={b.location_id} branch={b} onClick={() => navigate(`/admin/locations/${b.location_id}`)} />
          ))}
          {view === 'top10' && top10.map((b: Branch, i: number) => (
            <BranchRow key={b.location_id} branch={b} rank={i} onClick={() => navigate(`/admin/locations/${b.location_id}`)} />
          ))}
          {view === 'bottom10' && bottom10.map((b: Branch, i: number) => (
            <BranchRow key={b.location_id} branch={b} onClick={() => navigate(`/admin/locations/${b.location_id}`)} />
          ))}
          {view === 'all' && sortedBranches.map((b, i) => (
            <BranchRow key={b.location_id} branch={b} rank={i} onClick={() => navigate(`/admin/locations/${b.location_id}`)} />
          ))}
        </div>
      </div>
    </div>
  )
}
