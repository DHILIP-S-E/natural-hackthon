import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Sparkles, Star, Users, BarChart3, TrendingUp, Activity, Award
} from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import api from '../../config/api';
import { ARCH_DATA } from '../../constants/archetypes';

// Default empty analytics structure
const DEFAULT_KPI = {
  sessionsThisMonth: 0,
  avgRatingWithSoulskin: 0,
  avgRatingWithout: 0,
  mostCommonArchetype: '',
  certifiedStaffCount: 0,
  totalStaff: 0,
  ratingImprovement: '0%',
  repeatRateWithSoulskin: 0,
  repeatRateWithout: 0,
};

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem' };

const RADIAN = Math.PI / 180;
function renderCustomLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={700}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
}

export default function SoulskinAnalytics() {
  const { data, isLoading } = useQuery({
    queryKey: ['soulskin-analytics'],
    queryFn: async () => {
      const res = await api.get('/analytics/soulskin');
      return res.data?.data;
    },
    retry: false,
  });

  const KPI = data?.kpi || data || DEFAULT_KPI;
  const ARCHETYPE_DISTRIBUTION: { name: string; value: number; color: string }[] = data?.archetype_distribution || [];
  const RATING_COMPARISON: { service: string; withSoulskin: number; without: number }[] = data?.rating_comparison || [];
  const MONTHLY_TREND: { month: string; sessions: number; rating: number }[] = data?.monthly_trend || [];
  const CERTIFIED_STAFF: { name: string; role: string; certified_date: string; score: number; sessions: number }[] = data?.certified_staff || [];

  const mostCommonArch = KPI.mostCommonArchetype ? ARCH_DATA[KPI.mostCommonArchetype] : null;
  const MostCommonIcon = mostCommonArch?.icon;

  if (isLoading && !data) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Activity size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading SOULSKIN analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Analytics</p>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 12 }}>
            <Sparkles size={28} style={{ color: '#9B7FD4' }} /> SOULSKIN Analytics
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
            SOULSKIN performance insights
          </p>
        </div>
        <span className="badge badge-violet" style={{ fontWeight: 700, fontSize: '0.8rem', padding: '8px 16px' }}>
          SOULSKIN Active
        </span>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Sessions This Month', value: String(KPI.sessionsThisMonth), icon: <Sparkles size={16} />, color: '#9B7FD4' },
          {
            label: 'Avg Rating (SOULSKIN)', value: String(KPI.avgRatingWithSoulskin),
            subtitle: `vs ${KPI.avgRatingWithout} without (${KPI.ratingImprovement})`,
            icon: <Star size={16} />, color: 'var(--gold)',
          },
          {
            label: 'Most Common Archetype',
            value: mostCommonArch?.label ?? '-',
            icon: MostCommonIcon ? <MostCommonIcon size={16} /> : <Sparkles size={16} />,
            color: mostCommonArch?.color ?? '#9B7FD4',
          },
          { label: 'Certified Staff', value: `${KPI.certifiedStaffCount} / ${KPI.totalStaff}`, icon: <Award size={16} />, color: 'var(--success)' },
        ].map((k, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
            className="kpi-card" style={{ borderLeft: `4px solid ${k.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span className="kpi-label" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>{k.label}</span>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: `${k.color}12`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: k.color }}>
                {k.icon}
              </div>
            </div>
            <span className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 700 }}>{k.value}</span>
            {(k as any).subtitle && (
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 4 }}>{(k as any).subtitle}</div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 'var(--space-lg)' }}>
        {/* Archetype Distribution Donut */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
          className="card" style={{ padding: '24px' }}>
          <h4 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sparkles size={16} style={{ color: '#9B7FD4' }} /> Archetype Distribution
          </h4>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={ARCHETYPE_DISTRIBUTION}
                cx="50%" cy="50%"
                innerRadius={55} outerRadius={90}
                paddingAngle={3}
                dataKey="value"
                labelLine={false}
                label={renderCustomLabel}
              >
                {ARCHETYPE_DISTRIBUTION.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
          {/* Legend */}
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', marginTop: 12 }}>
            {ARCHETYPE_DISTRIBUTION.map(d => {
              const ad = Object.values(ARCH_DATA).find(a => a.label === d.name);
              const Icon = ad?.icon;
              return (
                <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem' }}>
                  {Icon && <Icon size={12} color={d.color} />}
                  <span style={{ color: 'var(--text-muted)' }}>{d.name}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{d.value}</span>
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Rating Impact Chart */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
          className="card" style={{ padding: '24px' }}>
          <h4 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BarChart3 size={16} style={{ color: 'var(--gold)' }} /> Rating Impact: With vs Without SOULSKIN
          </h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={RATING_COMPARISON} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
              <XAxis dataKey="service" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <YAxis domain={[3.5, 5.2]} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend
                formatter={(value: string) => <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{value}</span>}
              />
              <Bar dataKey="withSoulskin" fill="#9B7FD4" name="With SOULSKIN" radius={[4, 4, 0, 0]} />
              <Bar dataKey="without" fill="var(--border-medium)" name="Without SOULSKIN" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Repeat Rate Comparison + Monthly Trend */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Repeat Rate */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="card" style={{ padding: '24px' }}>
          <h4 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
            <TrendingUp size={16} style={{ color: 'var(--teal)' }} /> Customer Repeat Rate
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#9B7FD4' }}>{KPI.repeatRateWithSoulskin}%</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>With SOULSKIN</div>
              <div style={{ height: 8, background: 'var(--border-subtle)', borderRadius: 4, marginTop: 12 }}>
                <motion.div initial={{ width: 0 }} animate={{ width: `${KPI.repeatRateWithSoulskin}%` }} transition={{ delay: 0.6, duration: 0.8 }}
                  style={{ height: '100%', background: '#9B7FD4', borderRadius: 4 }} />
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{KPI.repeatRateWithout}%</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>Without SOULSKIN</div>
              <div style={{ height: 8, background: 'var(--border-subtle)', borderRadius: 4, marginTop: 12 }}>
                <motion.div initial={{ width: 0 }} animate={{ width: `${KPI.repeatRateWithout}%` }} transition={{ delay: 0.6, duration: 0.8 }}
                  style={{ height: '100%', background: 'var(--border-medium)', borderRadius: 4 }} />
              </div>
            </div>
          </div>
          <div style={{ textAlign: 'center', marginTop: 20, padding: '12px', background: 'rgba(155,127,212,0.06)', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: '#9B7FD4', fontWeight: 600 }}>
            SOULSKIN customers are {KPI.repeatRateWithSoulskin - KPI.repeatRateWithout}% more likely to return
          </div>
        </motion.div>

        {/* Monthly session trend */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
          className="card" style={{ padding: '24px' }}>
          <h4 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BarChart3 size={16} style={{ color: '#9B7FD4' }} /> SOULSKIN Adoption Trend
          </h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={MONTHLY_TREND}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
              <XAxis dataKey="month" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="sessions" fill="#9B7FD4" radius={[4, 4, 0, 0]} name="Sessions" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Certified Staff Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}
        className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Users size={16} /> SOULSKIN Certified Staff
          </h4>
          <span className="badge badge-violet" style={{ fontWeight: 600 }}>{CERTIFIED_STAFF.length} certified</span>
        </div>
        {CERTIFIED_STAFF.map((staff, i) => (
          <div key={staff.name} style={{
            padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%', background: 'rgba(155,127,212,0.1)',
                border: '2px solid rgba(155,127,212,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 600, fontSize: '0.8rem', color: '#9B7FD4',
              }}>
                {(staff.name ?? '').split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{staff.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{staff.role} &middot; Certified {staff.certified_date}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#9B7FD4' }}>{staff.score}%</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Score</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{staff.sessions}</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Sessions</div>
              </div>
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
