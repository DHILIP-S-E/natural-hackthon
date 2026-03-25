import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Brain, Sparkles, ScanFace, User, Scissors, TrendingUp, Users, BarChart3, Cpu } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import api from '../../config/api';

const AI_MODULES = [
  { name: 'Beauty Passport', description: 'Unified customer beauty profile with history, preferences, and AI insights.', icon: User, color: 'var(--teal)' },
  { name: 'SOULSKIN Engine', description: 'Archetype-based beauty personality analysis using psychometric + skin data.', icon: Sparkles, color: 'var(--violet)' },
  { name: 'AI Smart Mirror', description: 'AR-powered virtual try-on for hair, makeup, and skincare visualization.', icon: ScanFace, color: 'var(--gold)' },
  { name: 'Digital Twin', description: '3D avatar representing the customer for style simulation and planning.', icon: User, color: 'var(--info)' },
  { name: 'AI Stylist', description: 'Intelligent service recommendations based on customer profile and trends.', icon: Scissors, color: 'var(--bloom)' },
  { name: 'Trend Intelligence', description: 'Real-time beauty trend tracking from social media and search data.', icon: TrendingUp, color: 'var(--phoenix)' },
  { name: 'Staff Intelligence', description: 'Performance analytics, skill mapping, and retention prediction for staff.', icon: Users, color: 'var(--storm)' },
  { name: 'Salon BI', description: 'Business intelligence dashboards with revenue, quality, and operational metrics.', icon: BarChart3, color: 'var(--success)' },
];

export default function AIEnginePage() {
  const { data: registry } = useQuery({
    queryKey: ['agent-registry'],
    queryFn: () => api.get('/agents/registry').then(r => r.data),
  });

  const totalAgents = registry?.total_agents || 0;
  const tracks = registry?.tracks || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Brain size={28} style={{ color: 'var(--violet)' }} />
          AI Engine
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          {AI_MODULES.length} AI modules · {totalAgents} business logic agents across 6 tracks
        </p>
      </div>

      {/* Agent Registry Summary */}
      {totalAgents > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 'var(--space-sm)' }}>
          {Object.entries(tracks).map(([track, info]: [string, any], i) => (
            <motion.div key={track} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
              className="kpi-card" style={{ padding: 12, textAlign: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, marginBottom: 4 }}>
                <Cpu size={12} style={{ color: 'var(--teal)' }} />
                <span style={{ fontSize: '0.65rem', textTransform: 'capitalize', color: 'var(--text-muted)' }}>{track}</span>
              </div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{info.count}</div>
              <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{info.ps_range}</div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Modules Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-md)' }}>
        {AI_MODULES.map((mod, i) => {
          const Icon = mod.icon;
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
              <TiltCard tiltIntensity={8} style={{ borderLeft: `4px solid ${mod.color}`, padding: '24px', background: '#fff', height: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 8, background: `${mod.color}12`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={18} color={mod.color} />
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{mod.name}</div>
                  <span className="badge badge-success" style={{ fontSize: '0.6rem', padding: '2px 8px', textTransform: 'uppercase', marginLeft: 'auto' }}>
                    active
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {mod.description}
                </p>
              </TiltCard>
            </motion.div>
          );
        })}
      </div>

      {/* Agent Details */}
      {registry?.agents && registry.agents.length > 0 && (
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Cpu size={16} /> Registered Agents ({totalAgents})</h4>
          </div>
          <div className="table-container" style={{ border: 'none', borderRadius: 0, maxHeight: 400, overflow: 'auto' }}>
            <table>
              <thead>
                <tr><th>Agent</th><th>Track</th><th>Method</th><th>Path</th><th>PS Codes</th></tr>
              </thead>
              <tbody>
                {registry.agents.slice(0, 30).map((agent: any, i: number) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 500, fontSize: '0.8rem' }}>{agent.name}</td>
                    <td><span className="badge" style={{ fontSize: '0.6rem', padding: '1px 6px', textTransform: 'capitalize' }}>{agent.track}</span></td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: agent.method === 'POST' ? 'var(--teal)' : 'var(--text-muted)' }}>{agent.method}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{agent.path}</td>
                    <td style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{(agent.ps_codes || []).join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
