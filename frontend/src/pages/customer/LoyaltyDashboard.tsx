import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import api from '../../config/api'

interface Transaction {
  id: string
  type: string
  points: number
  description: string
  created_at: string
}

interface Reward {
  id: string
  name: string
  points: number
  category: 'service' | 'discount'
}

interface LoyaltyData {
  tier: string
  tier_multiplier: number
  total_points: number
  redeemable_points: number
  lifetime_points_earned: number
  next_tier: string | null
  points_to_next_tier: number
  referral_code: string
  transactions: Transaction[]
  rewards_catalogue: Reward[]
  redeemable_rewards: Reward[]
}

const TIER_COLORS: Record<string, { ring: string; badge: string; text: string }> = {
  bronze:   { ring: '#CD7F32', badge: 'bg-amber-700/20 text-amber-600 border-amber-700/30', text: 'text-amber-600' },
  silver:   { ring: '#C0C0C0', badge: 'bg-gray-400/20 text-gray-300 border-gray-400/30',   text: 'text-gray-300' },
  gold:     { ring: '#C9A96E', badge: 'bg-[#C9A96E]/20 text-[#C9A96E] border-[#C9A96E]/30', text: 'text-[#C9A96E]' },
  platinum: { ring: '#E5E4E2', badge: 'bg-white/20 text-white border-white/30',             text: 'text-white' },
}

function TierRing({ tier, points, lifetime }: { tier: string; points: number; lifetime: number }) {
  const colors = TIER_COLORS[tier] ?? TIER_COLORS.bronze
  const TIER_MAX: Record<string, number> = { bronze: 1000, silver: 3000, gold: 8000, platinum: 8000 }
  const max = TIER_MAX[tier] ?? 1000
  const pct = Math.min(100, (lifetime / max) * 100)
  const r = 54, c = 339.29
  const dash = (pct / 100) * c

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-40 h-40">
        <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
          <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
          <circle
            cx="60" cy="60" r={r} fill="none"
            stroke={colors.ring} strokeWidth="10"
            strokeDasharray={`${dash} ${c}`}
            strokeLinecap="round"
            style={{ transition: 'stroke-dasharray 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{points.toLocaleString()}</span>
          <span className="text-xs text-gray-400">AURA pts</span>
        </div>
      </div>
      <span className={`text-xs px-3 py-1 rounded-full border font-semibold uppercase tracking-wider ${colors.badge}`}>
        {tier}
      </span>
    </div>
  )
}

export default function LoyaltyDashboard() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'rewards' | 'history'>('rewards')
  const [redeemedCoupon, setRedeemedCoupon] = useState<{ code: string; name: string } | null>(null)

  const { data, isLoading } = useQuery<LoyaltyData>({
    queryKey: ['loyalty'],
    queryFn: () => api.get('/loyalty/me').then(r => r.data.data),
    staleTime: 30_000,
  })

  const redeemMut = useMutation({
    mutationFn: (rewardId: string) => api.post(`/loyalty/redeem/${rewardId}`).then(r => r.data.data),
    onSuccess: (res, rewardId) => {
      const reward = data?.rewards_catalogue.find(r => r.id === rewardId)
      setRedeemedCoupon({ code: res.coupon_code, name: reward?.name ?? 'Reward' })
      qc.invalidateQueries({ queryKey: ['loyalty'] })
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
        <div className="w-10 h-10 rounded-full border-2 border-[#C9A96E]/30 border-t-[#C9A96E] animate-spin" />
      </div>
    )
  }

  if (!data) return null

  const colors = TIER_COLORS[data.tier] ?? TIER_COLORS.bronze

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white p-6">
      <div className="max-w-2xl mx-auto space-y-8">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-[#C9A96E]">AURA Points</h1>
          <p className="text-gray-400 text-sm mt-1">Earn points on every visit · Redeem for rewards</p>
        </div>

        {/* Tier ring + stats */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col sm:flex-row gap-6 items-center">
          <TierRing tier={data.tier} points={data.total_points} lifetime={data.lifetime_points_earned} />

          <div className="flex-1 space-y-4 w-full">
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/5 rounded-xl p-3 text-center">
                <div className={`text-xl font-bold ${colors.text}`}>{data.redeemable_points.toLocaleString()}</div>
                <div className="text-xs text-gray-500 mt-0.5">Redeemable</div>
              </div>
              <div className="bg-white/5 rounded-xl p-3 text-center">
                <div className="text-xl font-bold text-white">{data.lifetime_points_earned.toLocaleString()}</div>
                <div className="text-xs text-gray-500 mt-0.5">Lifetime earned</div>
              </div>
            </div>

            {data.next_tier && (
              <div>
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>{data.points_to_next_tier.toLocaleString()} pts to {data.next_tier}</span>
                  <span>{data.tier_multiplier}× multiplier</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ background: colors.ring }}
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, 100 - (data.points_to_next_tier / (data.lifetime_points_earned + data.points_to_next_tier)) * 100)}%` }}
                    transition={{ duration: 1 }}
                  />
                </div>
              </div>
            )}

            <div className="bg-white/5 rounded-xl p-3">
              <div className="text-xs text-gray-400 mb-1">Your referral code</div>
              <div className="font-mono text-[#C9A96E] font-bold tracking-widest">{data.referral_code}</div>
              <div className="text-xs text-gray-500 mt-0.5">Share to earn 100 pts per referral</div>
            </div>
          </div>
        </div>

        {/* Coupon popup */}
        <AnimatePresence>
          {redeemedCoupon && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-5 text-center space-y-2"
            >
              <div className="text-2xl">🎉</div>
              <div className="font-semibold text-emerald-400">{redeemedCoupon.name} Redeemed!</div>
              <div className="font-mono text-xl text-white bg-white/10 rounded-xl py-2 px-4 inline-block tracking-widest">
                {redeemedCoupon.code}
              </div>
              <p className="text-xs text-gray-400">Show this code to your stylist at the salon</p>
              <button onClick={() => setRedeemedCoupon(null)} className="text-xs text-gray-500 hover:text-gray-300">Dismiss</button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tabs */}
        <div className="flex gap-2">
          {(['rewards', 'history'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`text-sm px-4 py-2 rounded-xl border transition-colors capitalize
                ${tab === t ? 'border-[#C9A96E] bg-[#C9A96E]/10 text-[#C9A96E]' : 'border-white/10 text-gray-400 hover:border-white/30'}`}
            >
              {t === 'rewards' ? '🎁 Rewards' : '📋 History'}
            </button>
          ))}
        </div>

        {/* Rewards catalogue */}
        {tab === 'rewards' && (
          <div className="space-y-3">
            {data.rewards_catalogue.map(reward => {
              const canRedeem = data.redeemable_points >= reward.points
              return (
                <div
                  key={reward.id}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition-all
                    ${canRedeem ? 'border-[#C9A96E]/30 bg-white/5' : 'border-white/5 bg-white/2 opacity-60'}`}
                >
                  <div className="text-2xl">{reward.category === 'service' ? '💆' : '🏷️'}</div>
                  <div className="flex-1">
                    <div className="font-medium text-sm text-white">{reward.name}</div>
                    <div className={`text-xs mt-0.5 ${canRedeem ? colors.text : 'text-gray-500'}`}>
                      {reward.points.toLocaleString()} pts
                    </div>
                  </div>
                  <button
                    onClick={() => redeemMut.mutate(reward.id)}
                    disabled={!canRedeem || redeemMut.isPending}
                    className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors
                      ${canRedeem
                        ? 'bg-[#C9A96E] text-black hover:bg-[#b8935a]'
                        : 'bg-white/5 text-gray-600 cursor-not-allowed'}`}
                  >
                    {redeemMut.isPending ? '…' : canRedeem ? 'Redeem' : `Need ${(reward.points - data.redeemable_points).toLocaleString()} more`}
                  </button>
                </div>
              )
            })}
          </div>
        )}

        {/* Transaction history */}
        {tab === 'history' && (
          <div className="space-y-2">
            {data.transactions.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-8">No transactions yet. Visit a salon to start earning!</p>
            )}
            {data.transactions.map(t => (
              <div key={t.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0
                  ${t.points > 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                  {t.points > 0 ? '+' : '−'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-white truncate">{t.description}</div>
                  <div className="text-xs text-gray-500">{new Date(t.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</div>
                </div>
                <div className={`text-sm font-semibold shrink-0 ${t.points > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {t.points > 0 ? '+' : ''}{t.points} pts
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
