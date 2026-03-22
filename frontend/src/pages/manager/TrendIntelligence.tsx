import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { TrendingUp, ArrowUp, ArrowDown, Minus, Eye, Calendar, Instagram } from 'lucide-react';
import api from '../../config/api';

const TRAJECTORY_MAP: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  emerging: { color: 'var(--teal)', icon: <ArrowUp size={14} />, label: 'Emerging' },
  growing: { color: 'var(--success)', icon: <ArrowUp size={14} />, label: 'Growing' },
  peak: { color: 'var(--gold)', icon: <Minus size={14} />, label: 'Peak' },
  declining: { color: 'var(--rose)', icon: <ArrowDown size={14} />, label: 'Declining' },
};

const LONGEVITY_MAP: Record<string, { color: string; label: string }> = {
  fad: { color: 'var(--rose)', label: 'Fad' },
  trend: { color: 'var(--teal)', label: 'Trend' },
  movement: { color: 'var(--gold)', label: 'Movement' },
};

export default function TrendIntelligence() {
  const { data: trendsData, isLoading } = useQuery({
    queryKey: ['trends'],
    queryFn: () => api.get('/trends/').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.trends || [];
    }),
  });

  const trends = trendsData || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <TrendingUp size={28} style={{ color: 'var(--teal)' }} /> Trend Intelligence
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          AI-powered demand forecasting from social listening, search trends, and booking data
          {trends.length > 0 && ` · ${trends.length} active trends`}
        </p>
      </div>

      {/* Trend cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        {isLoading ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>Loading trends...</div>
        ) : trends.length === 0 ? (
          <div className="card" style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No trend data available yet. Trends will appear as booking and social data accumulates.
          </div>
        ) : trends.map((trend: any, i: number) => {
          const trajectory = trend.trajectory || 'emerging';
          const longevity = trend.longevity_label || 'trend';
          const traj = TRAJECTORY_MAP[trajectory] || TRAJECTORY_MAP.emerging;
          const lon = LONGEVITY_MAP[longevity] || LONGEVITY_MAP.trend;
          const signal = Number(trend.overall_signal_strength) || 0;
          const socialScore = Number(trend.social_media_score) || signal * 0.9;
          const searchScore = Number(trend.search_trend_score) || signal * 0.8;
          const bookingScore = Number(trend.booking_demand_score) || signal * 0.7;
          const category = trend.service_category || trend.category || 'General';
          const cities = trend.top_cities || [];
          const action = trend.ai_recommendation || trend.action || 'Monitor and prepare';

          return (
            <motion.div key={trend.id || i} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
              className="card" style={{ padding: 0 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', minHeight: 160 }}>
                {/* Left: trend info */}
                <div style={{ padding: 'var(--space-lg)', borderRight: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                    <h3 style={{ fontSize: '1.1rem' }}>{trend.trend_name || trend.name}</h3>
                    <span className="badge" style={{ background: traj.color + '22', color: traj.color, border: `1px solid ${traj.color}40` }}>
                      {traj.icon} {traj.label}
                    </span>
                    <span className="badge" style={{ background: lon.color + '22', color: lon.color, border: `1px solid ${lon.color}40` }}>
                      {lon.label}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'var(--bg-surface)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>{category}</span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 12 }}>{trend.description || 'No description available'}</p>
                  {trend.celebrity_trigger && (
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                      <Instagram size={12} /> Triggered by: <strong style={{ color: 'var(--text-secondary)' }}>{trend.celebrity_trigger}</strong>
                    </p>
                  )}
                  {cities.length > 0 && (
                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
                      {cities.map((c: string) => <span key={c} style={{ fontSize: '0.7rem', background: 'var(--bg-surface)', padding: '2px 8px', borderRadius: 'var(--radius-full)', color: 'var(--text-muted)' }}>{c}</span>)}
                    </div>
                  )}
                  <div style={{ padding: '8px 12px', background: 'rgba(42,157,143,0.06)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--teal)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--teal)', fontWeight: 600, marginBottom: 2 }}>AI Recommendation</div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{action}</p>
                  </div>
                </div>

                {/* Right: signal scores */}
                <div style={{ padding: 'var(--space-lg)', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 14 }}>
                  <div style={{ textAlign: 'center', marginBottom: 8 }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '2rem', fontWeight: 800, color: traj.color }}>{signal.toFixed(1)}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>SIGNAL STRENGTH</div>
                  </div>
                  {[
                    { label: 'Social Media', value: socialScore, icon: <Instagram size={12} /> },
                    { label: 'Search Trend', value: searchScore, icon: <Eye size={12} /> },
                    { label: 'Booking Demand', value: bookingScore, icon: <Calendar size={12} /> },
                  ].map((s, j) => (
                    <div key={j}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 3 }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>{s.icon} {s.label}</span>
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--text-secondary)' }}>{s.value.toFixed(1)}</span>
                      </div>
                      <div style={{ height: 4, background: 'var(--border-subtle)', borderRadius: 2 }}>
                        <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min(s.value * 10, 100)}%` }} transition={{ duration: 0.6, delay: 0.3 + j * 0.1 }}
                          style={{ height: '100%', background: traj.color, borderRadius: 2 }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
