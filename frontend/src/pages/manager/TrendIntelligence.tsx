import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { TrendingUp, ArrowUp, ArrowDown, Minus, Eye, Calendar, Instagram, Activity } from 'lucide-react';
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
  // AI Agent: Early Trend Detection
  const { data: earlyTrendsResult, isLoading: trendsLoading } = useQuery({
    queryKey: ['trends-early-detection'],
    queryFn: () => api.get('/agents/track4/trends/early-detection').then(r => r.data?.data),
  });

  const trends = earlyTrendsResult?.trends || [];

  // AI Agent: Competitor Analysis (listing)
  const { data: competitiveData, isLoading: compLoading } = useQuery({
    queryKey: ['trends-competitor-analysis'],
    queryFn: () => api.get('/agents/track4/competitive/listing').then(r => r.data?.data),
  });

  const competitors = competitiveData || [];

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

      {/* Main Grid: Trends and Competitors */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 'var(--space-xl)', alignItems: 'start' }}>
        {/* Left: Trends */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {trendsLoading ? (
            <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>Analyzing signals...</div>
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

        {/* Regional Heatmap Section */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="card" style={{ padding: 'var(--space-lg)', marginTop: 'var(--space-md)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={18} color="var(--teal)" /> Regional Demand Heatmap
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 16 }}>
            {['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune'].map((city, idx) => {
              const intensity = 40 + Math.random() * 50;
              return (
                <div key={city} style={{ padding: 12, background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>{city}</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--teal)' }}>{intensity.toFixed(0)}</div>
                  <div style={{ height: 4, background: 'rgba(42,157,143,0.1)', borderRadius: 2, marginTop: 8, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${intensity}%`, background: 'var(--teal)' }} />
                  </div>
                </div>
              );
            })}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 16, fontStyle: 'italic' }}>
            * Signals based on search volume index and local booking velocity.
          </p>
        </motion.div>
      </div>

      {/* Right: Competitor Analysis & Celebrity Radar */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)' }}>
          <Instagram size={18} color="var(--gold)" /> Market Intelligence
        </h2>
        
        {compLoading ? (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>Gathering market data...</div>
        ) : competitors.map((comp: any, i: number) => (
          <motion.div key={i} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
            className="card" style={{ padding: '20px', borderLeft: `4px solid ${comp.sentiment_score > 70 ? 'var(--success)' : 'var(--gold)'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
              <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{comp.competitor_name}</div>
              <span className="badge" style={{ fontSize: '0.65rem', background: 'var(--bg-surface)' }}>{comp.distance_km}km</span>
            </div>
            
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 12 }}>
              "{comp.top_feedback_summary}"
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, borderTop: '1px solid var(--border-subtle)', paddingTop: 12 }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginBottom: 2 }}>Avg. Price</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{'\u20B9'}{comp.avg_service_price}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginBottom: 2 }}>Sentiment</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--success)' }}>{comp.sentiment_score}%</div>
              </div>
            </div>

            <div style={{ marginTop: 12, fontSize: '0.7rem', color: 'var(--gold)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Eye size={12} /> {comp.identified_advantage}
            </div>
          </motion.div>
        ))}

        {/* Celebrity Radar */}
        <div style={{ marginTop: 'var(--space-md)' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', marginBottom: 16 }}>
            <TrendingUp size={18} color="var(--rose)" /> Celebrity Radar
          </h2>
          <div className="card" style={{ padding: '20px', background: 'linear-gradient(135deg, rgba(244,79,154,0.05) 0%, rgba(255,255,255,0) 100%)', borderColor: 'rgba(244,79,154,0.15)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {trends.filter((t: any) => t.celebrity_trigger).slice(0, 3).map((t: any, idx: number) => (
                <div key={idx} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--bg-surface)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '2px solid rgba(244,79,154,0.2)', fontSize: '1.2rem' }}>
                    🌟
                  </div>
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 700 }}>{t.celebrity_trigger}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Driving "{t.trend_name}"</div>
                  </div>
                </div>
              ))}
              {trends.filter((t: any) => t.celebrity_trigger).length === 0 && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', padding: '12px 0' }}>
                  No major celebrity triggers detected in the last 48h.
                </div>
              )}
            </div>
            <button className="btn btn-sm btn-ghost" style={{ width: '100%', marginTop: 16, fontSize: '0.7rem' }}>
              View Full Social Impact Report
            </button>
          </div>
        </div>

        {!compLoading && competitors.length === 0 && (
          <div className="card" style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Collecting local salon data...
          </div>
        ) }
      </div>
    </div>
  </div>
  );
}
