/**
 * Feature 14: Eco Tracker — Manager Dashboard
 * Waste anomaly detection, eco scores, Green Salon leaderboard.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Leaf, AlertTriangle, Trophy, TrendingDown, BarChart2 } from 'lucide-react';
import api from '../../config/api';

interface EcoDashboard {
  location_id: string;
  month: number;
  year: number;
  avg_eco_score: number;
  total_sessions_tracked: number;
  products_logged: number;
  anomalies_detected: number;
  total_waste_ml: number;
}

interface LeaderboardEntry {
  rank: number;
  location_id: string;
  location_name: string;
  city: string;
  avg_eco_score: number;
  sessions_tracked: number;
}

const ECO_SCORE_COLOR = (score: number) => {
  if (score >= 90) return '#22c55e';
  if (score >= 75) return '#84cc16';
  if (score >= 55) return '#eab308';
  if (score >= 35) return '#f97316';
  return '#ef4444';
};

const ECO_LABEL = (score: number) => {
  if (score >= 90) return 'Excellent';
  if (score >= 75) return 'Good';
  if (score >= 55) return 'Average';
  if (score >= 35) return 'Below Average';
  return 'Poor';
};

export default function EcoTracker() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());

  // Get location from auth store in real app
  const locationId = localStorage.getItem('aura_location_id') || '';

  const { data: dashboard } = useQuery<EcoDashboard>({
    queryKey: ['eco-dashboard', locationId, month, year],
    queryFn: async () => {
      const res = await api.get(`/eco/location/${locationId}/dashboard?month=${month}&year=${year}`);
      return res.data?.data;
    },
    enabled: !!locationId,
  });

  const { data: leaderboard } = useQuery<{ leaderboard: LeaderboardEntry[]; green_salon_of_the_month: LeaderboardEntry | null }>({
    queryKey: ['eco-leaderboard', month, year],
    queryFn: async () => {
      const res = await api.get(`/eco/green-salon-leaderboard?month=${month}&year=${year}&limit=10`);
      return res.data?.data;
    },
  });

  const score = dashboard?.avg_eco_score ?? 0;
  const MONTHS = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', color: '#fff', fontFamily: 'DM Sans, sans-serif', padding: '24px' }}>
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
          <div>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#C9A96E', fontFamily: 'Playfair Display, serif', display: 'flex', alignItems: 'center', gap: 10 }}>
              <Leaf size={24} /> Eco Tracker
            </div>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>Sustainable beauty — waste monitoring & green scores</div>
          </div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <select value={month} onChange={e => setMonth(+e.target.value)} style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', fontSize: 13, cursor: 'pointer' }}>
              {MONTHS.filter((_, i) => i > 0).map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
            </select>
            <select value={year} onChange={e => setYear(+e.target.value)} style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', fontSize: 13, cursor: 'pointer' }}>
              {[now.getFullYear() - 1, now.getFullYear()].map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        {/* Eco Score Card */}
        {dashboard && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 28 }}>
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={{ padding: 24, background: 'rgba(255,255,255,0.03)', borderRadius: 16, border: `1px solid ${ECO_SCORE_COLOR(score)}30`, textAlign: 'center' }}>
              <div style={{ fontSize: 48, fontWeight: 800, color: ECO_SCORE_COLOR(score), fontFamily: 'Playfair Display, serif' }}>{score.toFixed(0)}</div>
              <div style={{ fontSize: 14, color: ECO_SCORE_COLOR(score), fontWeight: 600 }}>{ECO_LABEL(score)}</div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>Avg Eco Score</div>
            </motion.div>

            {[
              { label: 'Sessions Tracked', value: dashboard.total_sessions_tracked, icon: BarChart2, color: '#C9A96E' },
              { label: 'Anomalies', value: dashboard.anomalies_detected, icon: AlertTriangle, color: dashboard.anomalies_detected > 0 ? '#ef4444' : '#22c55e' },
              { label: 'Total Waste (ml)', value: `${dashboard.total_waste_ml.toFixed(0)}ml`, icon: TrendingDown, color: '#f97316' },
            ].map(({ label, value, icon: Icon, color }) => (
              <motion.div key={label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={{ padding: 20, background: 'rgba(255,255,255,0.03)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.06)', textAlign: 'center' }}>
                <Icon size={24} style={{ color, marginBottom: 8 }} />
                <div style={{ fontSize: 28, fontWeight: 700, color }}>{value}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>{label}</div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Green Salon Winner */}
        {leaderboard?.green_salon_of_the_month && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: 20, background: 'linear-gradient(135deg, rgba(34,197,94,0.1), rgba(132,204,22,0.05))', border: '1px solid rgba(34,197,94,0.3)', borderRadius: 16, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
            <Trophy size={40} style={{ color: '#fbbf24', flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: 13, color: '#22c55e', fontWeight: 600, marginBottom: 4 }}>🌿 Green Salon of the Month — {MONTHS[month]} {year}</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>{leaderboard.green_salon_of_the_month.location_name}</div>
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)' }}>Eco Score: {leaderboard.green_salon_of_the_month.avg_eco_score}/100 · {leaderboard.green_salon_of_the_month.city}</div>
            </div>
          </motion.div>
        )}

        {/* Network Leaderboard */}
        <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.06)', overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', fontSize: 14, fontWeight: 600, color: '#C9A96E' }}>
            Network Eco Leaderboard — {MONTHS[month]} {year}
          </div>
          {leaderboard?.leaderboard?.length === 0 && (
            <div style={{ padding: 32, textAlign: 'center', color: 'rgba(255,255,255,0.3)', fontSize: 13 }}>No eco data for this month yet. Start logging product usage per session.</div>
          )}
          {leaderboard?.leaderboard?.map(entry => (
            <motion.div key={entry.location_id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: '14px 20px', borderBottom: '1px solid rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: entry.rank <= 3 ? 'rgba(251,191,36,0.15)' : 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, color: entry.rank <= 3 ? '#fbbf24' : 'rgba(255,255,255,0.4)', flexShrink: 0 }}>
                {entry.rank <= 3 ? ['🥇', '🥈', '🥉'][entry.rank - 1] : entry.rank}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#fff' }}>{entry.location_name}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>{entry.city} · {entry.sessions_tracked} sessions</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: ECO_SCORE_COLOR(entry.avg_eco_score) }}>{entry.avg_eco_score}</div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)' }}>{ECO_LABEL(entry.avg_eco_score)}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
