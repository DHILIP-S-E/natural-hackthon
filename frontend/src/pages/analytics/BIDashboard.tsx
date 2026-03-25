import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { BarChart3, DollarSign, TrendingUp, Users, Star, ArrowUpRight, ArrowDownRight, Sparkles, GitCompare } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, AreaChart, Area } from 'recharts';
import api from '../../config/api';

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem' };

const CATEGORY_COLORS: Record<string, string> = {
  Hair: '#C9A96E', Skin: '#2A9D8F', Nail: '#E8A87C', Makeup: '#9B7FD4', Wellness: '#6B8FA6',
  'hair-color': '#C9A96E', 'hair-cut': '#2A9D8F', facial: '#E8A87C', bridal: '#9B7FD4',
};

export default function BIDashboard() {
  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: revenue } = useQuery({
    queryKey: ['analytics', 'revenue', 180],
    queryFn: () => api.get('/analytics/revenue?days=180').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: quality } = useQuery({
    queryKey: ['analytics', 'quality', 30],
    queryFn: () => api.get('/analytics/quality?days=30').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: customers } = useQuery({
    queryKey: ['analytics', 'customers'],
    queryFn: () => api.get('/analytics/customers').then(r => r.data?.data),
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

  const { data: forecast } = useQuery({
    queryKey: ['analytics', 'forecast'],
    queryFn: () => api.get('/analytics/forecast').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const totalRevenue = Number(overview?.total_revenue) || 0;
  const revenueInLakhs = (totalRevenue / 100000).toFixed(1);
  const completionRate = Number(overview?.completion_rate) || 0;
  const avgQuality = Number(overview?.avg_quality_score) || 0;
  const avgRating = Number(overview?.avg_customer_rating) || 0;
  const soulskinCount = Number(overview?.soulskin_sessions) || 0;
  const totalBookings = Number(overview?.total_bookings) || 0;
  const soulskinRate = totalBookings > 0
    ? Math.round(soulskinCount / totalBookings * 100) : 0;

  const categoryData = (revenue?.by_category || []).map((c: any) => ({
    name: c.category || 'Other',
    value: Math.round((Number(c.revenue) || 0) / 1000),
    color: CATEGORY_COLORS[c.category] || '#6B8FA6',
  }));

  const locationData = (compare?.locations || []).slice(0, 8);

  const archetypeData = soulskinData?.archetype_distribution
    ? Object.entries(soulskinData.archetype_distribution).map(([name, count]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value: count as number,
        color: name === 'phoenix' ? '#E8611A' : name === 'river' ? '#4A9FD4' : name === 'moon' ? '#7B68C8' : name === 'bloom' ? '#E8A87C' : '#6B8FA6',
      }))
    : [];

  const growthTrend = forecast?.trend || 'stable';
  const growthRate = forecast?.growth_rate || 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <BarChart3 size={28} style={{ color: 'var(--gold)' }} /> Business Intelligence
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Revenue, quality, retention, and SOULSKIN analytics across all locations</p>
      </div>

      {/* KPI Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Total Revenue', value: `₹${revenueInLakhs}L`, change: `${growthRate > 0 ? '+' : ''}${growthRate}%`, positive: growthRate >= 0, icon: <DollarSign size={16} />, color: 'var(--gold)' },
          { label: 'Avg Quality', value: avgQuality.toFixed(1), change: avgQuality >= 4.5 ? 'Excellent' : 'Good', positive: avgQuality >= 4.0, icon: <Star size={16} />, color: 'var(--violet)' },
          { label: 'Completion Rate', value: `${completionRate}%`, change: completionRate >= 80 ? 'Healthy' : 'Needs attention', positive: completionRate >= 75, icon: <Users size={16} />, color: 'var(--teal)' },
          { label: 'SOULSKIN Rate', value: `${soulskinRate}%`, change: `${soulskinCount} sessions`, positive: soulskinRate > 20, icon: <Sparkles size={16} />, color: '#7B68C8' },
          { label: 'Avg Rating', value: avgRating.toFixed(1), change: avgRating >= 4.5 ? 'Excellent' : 'Good', positive: avgRating >= 4.0, icon: <TrendingUp size={16} />, color: 'var(--success)' },
        ].map((kpi, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${kpi.color}`, padding: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: kpi.color }}>{kpi.icon}<span className="kpi-label" style={{ fontSize: '0.65rem' }}>{kpi.label}</span></div>
            <span className="kpi-value" style={{ fontSize: '1.3rem' }}>{kpi.value}</span>
            <span className={`kpi-change ${kpi.positive ? 'positive' : 'negative'}`} style={{ display: 'flex', alignItems: 'center', gap: 2, fontSize: '0.7rem' }}>
              {kpi.positive ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />} {kpi.change}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Charts Row 1 */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Revenue by Location */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card">
          <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}><DollarSign size={16} /> Revenue by Location (₹K)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={(revenue?.by_location || []).map((l: any) => ({ name: l.location?.substring(0, 12) || 'Unknown', revenue: Math.round(l.revenue / 1000), bookings: l.bookings }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#252530" />
              <XAxis dataKey="name" tick={{ fill: '#5C5A70', fontSize: 11 }} />
              <YAxis tick={{ fill: '#5C5A70', fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="revenue" fill="#C9A96E" radius={[4, 4, 0, 0]} name="Revenue (₹K)" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Revenue by Category */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="card">
          <h4 style={{ marginBottom: 16 }}>Revenue by Category</h4>
          {categoryData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={categoryData} dataKey="value" cx="50%" cy="50%" outerRadius={75} innerRadius={40} paddingAngle={4}>
                    {categoryData.map((entry: any, i: number) => <Cell key={i} fill={entry.color} />)}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginTop: 8 }}>
                {categoryData.map((c: any, i: number) => (
                  <span key={i} style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-muted)' }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2, background: c.color, display: 'inline-block' }} />
                    {c.name} (₹{c.value}K)
                  </span>
                ))}
              </div>
            </>
          ) : (
            <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>No category data yet</div>
          )}
        </motion.div>
      </div>

      {/* Charts Row 2 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Customer LTV Tiers */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="card">
          <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}><Users size={16} /> Customer Segments</h4>
          {customers?.ltv_tiers ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginTop: 16 }}>
              {[
                { label: 'Gold (₹50K+)', value: customers.ltv_tiers.gold, color: '#C9A96E' },
                { label: 'Silver (₹20-50K)', value: customers.ltv_tiers.silver, color: '#9B9B9B' },
                { label: 'Bronze (₹5-20K)', value: customers.ltv_tiers.bronze, color: '#CD7F32' },
                { label: 'New (<₹5K)', value: customers.ltv_tiers.new, color: 'var(--teal)' },
              ].map((tier, i) => (
                <div key={i} style={{ textAlign: 'center', padding: 16, background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', borderTop: `3px solid ${tier.color}` }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: tier.color }}>{tier.value}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 4 }}>{tier.label}</div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ height: 150, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Loading...</div>
          )}
          <div style={{ marginTop: 16, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Total: {customers?.total_customers || 0} customers · Avg Beauty Score: {customers?.avg_beauty_score || 0}
          </div>
        </motion.div>

        {/* SOULSKIN Archetype Distribution */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="card">
          <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}><Sparkles size={16} /> SOULSKIN Impact</h4>
          {archetypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={archetypeData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#252530" />
                <XAxis type="number" tick={{ fill: '#5C5A70', fontSize: 11 }} />
                <YAxis dataKey="name" type="category" width={70} tick={{ fill: '#5C5A70', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="value" name="Sessions">
                  {archetypeData.map((entry: any, i: number) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No SOULSKIN data yet</div>
          )}
          {soulskinData && (
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 12, fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>With SOULSKIN: <strong style={{ color: 'var(--success)' }}>{soulskinData.avg_rating_with_soulskin}</strong></span>
              <span style={{ color: 'var(--text-muted)' }}>Without: <strong>{soulskinData.avg_rating_without_soulskin}</strong></span>
              <span style={{ color: soulskinData.rating_lift > 0 ? 'var(--success)' : 'var(--text-muted)' }}>Lift: +{soulskinData.rating_lift}</span>
            </div>
          )}
        </motion.div>
      </div>

      {/* Location Comparison */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><GitCompare size={16} /> Location Benchmarking</h4>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Location</th>
                <th>Revenue (₹K)</th>
                <th>Quality</th>
                <th>Bookings</th>
                <th>SOULSKIN</th>
                <th>Performance</th>
              </tr>
            </thead>
            <tbody>
              {locationData.length > 0 ? locationData.map((loc: any, i: number) => {
                const revK = Math.round(loc.revenue / 1000);
                const target = Math.round((loc.target || 500000) / 1000);
                const perf = revK > target ? 'Above Target' : revK > target * 0.8 ? 'On Track' : 'Below Target';
                const perfColor = revK > target ? 'var(--success)' : revK > target * 0.8 ? 'var(--warning)' : 'var(--error)';
                return (
                  <tr key={i}>
                    <td style={{ fontWeight: 500 }}>{loc.name}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--gold)' }}>₹{revK}K</td>
                    <td><Star size={12} style={{ color: 'var(--gold)', verticalAlign: 'middle' }} /> {loc.avg_quality}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{loc.total_bookings}</td>
                    <td><span className="badge badge-violet" style={{ padding: '2px 8px' }}>{loc.soulskin_sessions}</span></td>
                    <td><span style={{ color: perfColor, fontSize: '0.75rem', fontWeight: 600 }}>{perf}</span></td>
                  </tr>
                );
              }) : (
                <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 32 }}>No location data available</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
