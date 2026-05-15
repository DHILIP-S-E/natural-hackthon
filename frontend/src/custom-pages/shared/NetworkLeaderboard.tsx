/**
 * Feature 11: Network-Wide Skill & Training Leaderboard
 * Stylists compete across all 750 salons. Skill scores, badges, attrition alerts.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Award, AlertTriangle, Star } from 'lucide-react';
import api from '../../config/api';

interface StaffEntry {
  id: string;
  name: string;
  location_name: string;
  city: string;
  skill_level: string;
  current_rating: number;
  total_services_done: number;
  attrition_risk_score: number;
  risk_label: string;
  badges: string[];
  specializations: string[];
}

const RISK_STYLES: Record<string, { color: string; bg: string }> = {
  low: { color: '#22c55e', bg: 'rgba(34,197,94,0.1)' },
  medium: { color: '#eab308', bg: 'rgba(234,179,8,0.1)' },
  high: { color: '#ef4444', bg: 'rgba(239,68,68,0.1)' },
};

const SKILL_BADGES: Record<string, string> = { L1: '🌱', L2: '⭐', L3: '💎' };

function riskLabel(score: number | null | undefined): string {
  if (!score) return 'low';
  if (score >= 0.5) return 'high';
  if (score >= 0.25) return 'medium';
  return 'low';
}

export default function NetworkLeaderboard() {
  const [filter, setFilter] = useState<'all' | 'L1' | 'L2' | 'L3'>('all');
  const [riskFilter, setRiskFilter] = useState<'all' | 'high'>('all');

  const { data: staffData, isLoading, isError } = useQuery<StaffEntry[]>({
    queryKey: ['network-leaderboard'],
    queryFn: async () => {
      const res = await api.get('/staff?per_page=50');
      const rawList: any[] = res.data?.data?.staff || [];
      return rawList.map((s, idx) => ({
        id: s.id,
        name: s.name || 'Unknown',
        location_name: s.location_name || '—',
        city: s.city || '—',
        skill_level: s.skill_level || 'L1',
        current_rating: s.current_rating ?? 0,
        total_services_done: s.total_services_done ?? 0,
        attrition_risk_score: s.attrition_risk_score ?? 0,
        risk_label: s.attrition_risk_label || riskLabel(s.attrition_risk_score),
        badges: s.badges || [],
        specializations: s.specializations || [],
      })).sort((a, b) => b.current_rating - a.current_rating);
    },
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.4)' }}>
      Loading leaderboard...
    </div>
  );

  if (isError || !staffData) return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ef4444' }}>
      Failed to load leaderboard data.
    </div>
  );

  const staff = staffData;
  const filtered = staff
    .filter(s => filter === 'all' || s.skill_level === filter)
    .filter(s => riskFilter === 'all' || s.risk_label === 'high');

  const highRisk = staff.filter(s => s.risk_label === 'high');

  return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', color: '#fff', fontFamily: 'DM Sans, sans-serif', padding: '24px' }}>
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#C9A96E', fontFamily: 'Playfair Display, serif', display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <Award size={24} /> Stylist Network Leaderboard
          </div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>Top performers across all Naturals locations · Skill-based ranking</div>
        </div>

        {/* Attrition Alert Banner */}
        {highRisk.length > 0 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: 16, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: 14, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 12 }}>
            <AlertTriangle size={20} style={{ color: '#ef4444', flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#ef4444' }}>{highRisk.length} stylists at high attrition risk</div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>Branch managers, regional managers, and HR have been alerted automatically.</div>
            </div>
            <button onClick={() => setRiskFilter(riskFilter === 'high' ? 'all' : 'high')} style={{ marginLeft: 'auto', padding: '6px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, color: '#ef4444', cursor: 'pointer', fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap' }}>
              {riskFilter === 'high' ? 'Show All' : 'View At-Risk'}
            </button>
          </motion.div>
        )}

        {/* Filters */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          {(['all', 'L1', 'L2', 'L3'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{ padding: '6px 18px', borderRadius: 20, border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600, background: filter === f ? '#C9A96E' : 'rgba(255,255,255,0.06)', color: filter === f ? '#0A0A0F' : 'rgba(255,255,255,0.55)' }}>
              {f === 'all' ? 'All Levels' : `${SKILL_BADGES[f]} ${f}`}
            </button>
          ))}
        </div>

        {/* Top 3 Podium */}
        {filter === 'all' && riskFilter === 'all' && filtered.length >= 3 && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr 1fr', gap: 12, marginBottom: 28, alignItems: 'end' }}>
            {[1, 0, 2].map(i => {
              const s = filtered[i];
              const isPrimary = i === 0;
              return (
                <motion.div key={s.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} style={{ padding: isPrimary ? 24 : 18, background: isPrimary ? 'rgba(201,169,110,0.08)' : 'rgba(255,255,255,0.03)', border: `1px solid ${isPrimary ? 'rgba(201,169,110,0.3)' : 'rgba(255,255,255,0.06)'}`, borderRadius: 16, textAlign: 'center' }}>
                  <div style={{ fontSize: isPrimary ? 32 : 24, marginBottom: 8 }}>{['🥇', '🥈', '🥉'][i === 0 ? 0 : i === 1 ? 1 : 2]}</div>
                  <div style={{ fontSize: isPrimary ? 16 : 14, fontWeight: 700, color: '#fff', marginBottom: 4 }}>{s.name}</div>
                  <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 8 }}>{s.location_name}</div>
                  <div style={{ fontSize: isPrimary ? 24 : 20, fontWeight: 800, color: '#C9A96E' }}>★ {s.current_rating.toFixed(1)}</div>
                  <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginTop: 4 }}>{s.total_services_done} services</div>
                  <div style={{ marginTop: 10, display: 'flex', gap: 4, flexWrap: 'wrap', justifyContent: 'center' }}>
                    {s.badges.slice(0, 2).map(b => <span key={b} style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(201,169,110,0.1)', color: '#C9A96E', borderRadius: 4 }}>{b}</span>)}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* Full Leaderboard */}
        <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.06)', overflow: 'hidden' }}>
          {filtered.map((s, idx) => {
            const risk = RISK_STYLES[s.risk_label] || RISK_STYLES.low;
            return (
              <motion.div key={s.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.03 }} style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 36, textAlign: 'center', fontSize: 14, fontWeight: 700, color: idx < 3 ? '#C9A96E' : 'rgba(255,255,255,0.3)', flexShrink: 0 }}>
                  {idx + 1}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                    <span style={{ fontSize: 14, fontWeight: 600, color: '#fff' }}>{s.name}</span>
                    <span style={{ fontSize: 12 }}>{SKILL_BADGES[s.skill_level]} {s.skill_level}</span>
                    {s.risk_label === 'high' && <AlertTriangle size={13} style={{ color: '#ef4444' }} />}
                  </div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>{s.location_name} · {s.city}</div>
                  <div style={{ display: 'flex', gap: 4, marginTop: 6, flexWrap: 'wrap' }}>
                    {s.badges.slice(0, 2).map(b => <span key={b} style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(201,169,110,0.08)', color: '#C9A96E', borderRadius: 4 }}>{b}</span>)}
                    {s.specializations.slice(0, 2).map(sp => <span key={sp} style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.4)', borderRadius: 4 }}>{sp}</span>)}
                  </div>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#C9A96E', marginBottom: 2 }}>★ {s.current_rating.toFixed(1)}</div>
                  <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginBottom: 6 }}>{s.total_services_done} services</div>
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 6, background: risk.bg, color: risk.color, fontWeight: 700 }}>
                    Risk: {s.risk_label.toUpperCase()}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
