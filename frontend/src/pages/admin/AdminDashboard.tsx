import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Map, DollarSign, Users, Star, Sparkles, Building, ArrowUpRight, Brain, Shield } from 'lucide-react';
import api from '../../config/api';

export default function AdminDashboard() {
  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: compare } = useQuery({
    queryKey: ['analytics', 'compare'],
    queryFn: () => api.get('/analytics/compare').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: soulskinData } = useQuery({
    queryKey: ['analytics', 'soulskin'],
    queryFn: () => api.get('/analytics/soulskin').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: registry } = useQuery({
    queryKey: ['agents', 'registry'],
    queryFn: () => api.get('/agents/registry').then(r => r.data),
    staleTime: 10 * 60 * 1000,
  });

  const { data: staffData } = useQuery({
    queryKey: ['analytics', 'staff'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const totalRevenue = Number(overview?.total_revenue) || 0;
  const locations = compare?.locations || [];
  const totalStaff = Number(staffData?.total_staff) || 0;
  const avgQuality = Number(overview?.avg_quality_score) || 0;
  const soulskinSessions = Number(overview?.soulskin_sessions) || 0;
  const totalCustomers = Number(overview?.total_customers) || 0;

  const kpiData = [
    { label: 'Network Revenue', value: `₹${(totalRevenue / 100000).toFixed(1)}L`, change: `${overview?.total_bookings || 0} bookings`, positive: true, icon: <DollarSign size={18} />, color: 'var(--gold)' },
    { label: 'Active Locations', value: locations.length.toString(), change: 'All operational', positive: true, icon: <Building size={18} />, color: 'var(--teal)' },
    { label: 'Total Staff', value: totalStaff.toString(), change: 'Active', positive: true, icon: <Users size={18} />, color: 'var(--success)' },
    { label: 'Avg Quality', value: (avgQuality / 20).toFixed(1), change: avgQuality >= 80 ? 'Excellent' : 'Good', positive: avgQuality >= 70, icon: <Star size={18} />, color: 'var(--violet)' },
    { label: 'SOULSKIN', value: soulskinSessions.toString(), change: 'sessions', positive: true, icon: <Sparkles size={18} />, color: 'var(--moon)' },
    { label: 'Customer Base', value: totalCustomers.toLocaleString(), change: 'Total', positive: true, icon: <Users size={18} />, color: 'var(--bloom)' },
  ];

  const archetypeDist = soulskinData?.archetype_distribution || {};
  const totalSoulSessions = soulskinData?.total_sessions || 0;
  const ARCH_CONFIG: Record<string, { emoji: string; color: string }> = {
    phoenix: { emoji: '🔥', color: 'var(--phoenix)' },
    bloom: { emoji: '🌸', color: 'var(--bloom)' },
    storm: { emoji: '⛈️', color: 'var(--storm)' },
    river: { emoji: '🌊', color: 'var(--river)' },
    moon: { emoji: '🌙', color: 'var(--moon)' },
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Shield size={28} style={{ color: 'var(--gold)' }} />
          AURA Command Center
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          Super Admin — {locations.length} Locations · {registry?.total_agents || 0} AI Agents
        </p>
      </div>

      {/* KPI Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-md)' }}>
        {kpiData.map((kpi, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${kpi.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="kpi-label">{kpi.label}</span>
              <div style={{ color: kpi.color }}>{kpi.icon}</div>
            </div>
            <span className="kpi-value" style={{ fontSize: '1.5rem' }}>{kpi.value}</span>
            <span className="kpi-change positive" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <ArrowUpRight size={12} /> {kpi.change}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Location Performance */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Map size={18} /> Location Performance</h4>
          </div>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table>
              <thead><tr><th>Location</th><th>Revenue</th><th>Quality</th><th>Bookings</th><th>SOULSKIN</th></tr></thead>
              <tbody>
                {locations.length > 0 ? locations.map((loc: any, i: number) => (
                  <tr key={i}>
                    <td>
                      <div style={{ fontWeight: 500 }}>{loc.name}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{loc.city}</div>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--gold)' }}>₹{Math.round(loc.revenue / 1000)}K</td>
                    <td><Star size={12} style={{ color: 'var(--gold)' }} /> {loc.avg_quality}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{loc.total_bookings}</td>
                    <td><span className="badge badge-violet" style={{ padding: '2px 8px' }}>{loc.soulskin_sessions}</span></td>
                  </tr>
                )) : (
                  <tr><td colSpan={5} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>Loading...</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* AI Modules */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Brain size={18} style={{ color: 'var(--violet)' }} /> AI Agents ({registry?.total_agents || 0})</h4>
          </div>
          <div>
            {registry?.tracks ? Object.entries(registry.tracks).map(([track, info]: [string, any]) => (
              <div key={track} style={{ padding: '10px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 500, textTransform: 'capitalize' }}>{track}</div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{info.ps_range}</div>
                </div>
                <span className="badge badge-success" style={{ padding: '2px 8px', fontSize: '0.65rem' }}>{info.count} agents</span>
              </div>
            )) : (
              <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</div>
            )}
          </div>
        </motion.div>
      </div>

      {/* SOULSKIN Network Insights */}
      <div className="card" style={{ borderTop: '3px solid var(--violet)', background: 'rgba(155,127,212,0.03)' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, color: 'var(--violet)' }}>
          <Sparkles size={18} /> SOULSKIN Network Insights
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
          {Object.entries(ARCH_CONFIG).map(([key, cfg], i) => {
            const count = archetypeDist[key] || 0;
            const pct = totalSoulSessions > 0 ? Math.round(count / totalSoulSessions * 100) : 0;
            return (
              <div key={key} style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 'var(--radius-md)', border: `1px solid ${cfg.color}30` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontSize: '1.5rem' }}>{cfg.emoji}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: cfg.color }}>{pct}%</span>
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'capitalize' }}>{key}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{count} sessions</div>
                <div style={{ marginTop: 8, height: 3, background: 'var(--border-subtle)', borderRadius: 2 }}>
                  <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 0.8, delay: 0.3 + i * 0.1 }}
                    style={{ height: '100%', background: cfg.color, borderRadius: 2 }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
