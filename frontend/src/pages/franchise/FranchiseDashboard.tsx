import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Map, DollarSign, Users, Star, GitCompare } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../../config/api';

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem' };

export default function FranchiseDashboard() {
  const { data: compare } = useQuery({
    queryKey: ['analytics', 'compare'],
    queryFn: () => api.get('/analytics/compare').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: staffData } = useQuery({
    queryKey: ['analytics', 'staff'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const locations = compare?.locations || [];
  const totalRevenue = locations.reduce((s: number, l: any) => s + (l.revenue || 0), 0);
  const avgQuality = locations.length > 0
    ? (locations.reduce((s: number, l: any) => s + (l.avg_quality || 0), 0) / locations.length).toFixed(1)
    : '0';
  const totalStaff = staffData?.total_staff || 0;

  const chartData = locations.map((l: any) => ({
    location: l.name?.substring(0, 12) || 'Unknown',
    revenue: Math.round((l.revenue || 0) / 100000 * 10) / 10,
    quality: l.avg_quality || 0,
    retention: 0,
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem' }}>Franchise Dashboard</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Multi-location P&L, quality, and competitive benchmarking</p>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Total Revenue', value: `₹${(totalRevenue / 100000).toFixed(1)}L`, icon: <DollarSign size={16} />, color: 'var(--gold)' },
          { label: 'Locations', value: locations.length.toString(), icon: <Map size={16} />, color: 'var(--teal)' },
          { label: 'Avg Quality', value: avgQuality, icon: <Star size={16} />, color: 'var(--violet)' },
          { label: 'Total Staff', value: totalStaff.toString(), icon: <Users size={16} />, color: 'var(--success)' },
        ].map((kpi, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${kpi.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: kpi.color }}>{kpi.icon}<span className="kpi-label">{kpi.label}</span></div>
            <span className="kpi-value" style={{ fontSize: '1.5rem' }}>{kpi.value}</span>
          </motion.div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Revenue comparison chart */}
        <div className="card">
          <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}><GitCompare size={16} /> Revenue Comparison (₹ Lakhs)</h4>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#252530" />
                <XAxis type="number" tick={{ fill: '#5C5A70', fontSize: 11 }} />
                <YAxis dataKey="location" type="category" width={90} tick={{ fill: '#5C5A70', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="revenue" fill="#C9A96E" radius={[0, 4, 4, 0]} name="Revenue (₹L)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Loading...</div>
          )}
        </div>

        {/* Location cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {locations.length > 0 ? locations.map((loc: any, i: number) => {
            const revL = (Number(loc.revenue) || 0) / 100000;
            const target = (loc.target || 500000) / 100000;
            const onTrack = revL >= target;
            return (
              <motion.div key={i} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                className="card" style={{ padding: '14px 18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{loc.name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{loc.city}</div>
                  </div>
                  <span className={`badge ${onTrack ? 'badge-success' : 'badge-warning'}`}>{onTrack ? 'On Track' : 'Below Target'}</span>
                </div>
                <div style={{ display: 'flex', gap: 16, fontSize: '0.75rem' }}>
                  <div><span style={{ color: 'var(--gold)', fontWeight: 600 }}>₹{revL.toFixed(1)}L</span></div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 2 }}><Star size={10} style={{ color: 'var(--gold)' }} />{loc.avg_quality}</div>
                  <div><span style={{ fontWeight: 600 }}>{loc.total_bookings}</span> <span style={{ color: 'var(--text-muted)' }}>bookings</span></div>
                </div>
              </motion.div>
            );
          }) : (
            <div className="card" style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>Loading locations...</div>
          )}
        </div>
      </div>
    </div>
  );
}
