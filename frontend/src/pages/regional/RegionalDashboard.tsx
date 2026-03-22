import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Map, DollarSign, Users, Star, TrendingUp, Building, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import api from '../../config/api';

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem' };

export default function RegionalDashboard() {
  const { data: compare } = useQuery({
    queryKey: ['analytics-compare-regional'],
    queryFn: () => api.get('/analytics/compare').then(r => r.data?.data),
  });

  const { data: overview } = useQuery({
    queryKey: ['analytics-overview-regional'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data?.data),
  });

  const { data: staffData } = useQuery({
    queryKey: ['analytics-staff-regional'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
  });

  const locations = compare?.locations || [];
  const regions = compare?.regions || [];
  const totalRevenue = overview?.total_revenue || locations.reduce((s: number, l: any) => s + (l.revenue || 0), 0);
  const totalLocations = locations.length || 0;
  const totalStaff = staffData?.total_staff || overview?.total_staff || 0;
  const avgQuality = overview?.avg_quality_score ? (overview.avg_quality_score / 20).toFixed(1) : '0';
  const totalCustomers = overview?.total_customers || 0;

  const revenueByRegion = regions.length > 0
    ? regions.map((r: any) => ({ region: r.name || r.region || 'Unknown', revenue: ((r.revenue ?? 0) / 100000) }))
    : locations.map((l: any) => ({ region: (l.name ?? '').substring(0, 12) || 'Unknown', revenue: ((l.revenue ?? 0) / 100000) }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Map size={28} style={{ color: 'var(--teal)' }} /> Regional Dashboard
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Cross-region performance analytics and franchise benchmarking</p>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Total Revenue', value: `₹${(totalRevenue / 100000).toFixed(1)}L`, icon: <DollarSign size={16} />, color: 'var(--gold)' },
          { label: 'Regions', value: String(regions.length || 1), icon: <Map size={16} />, color: 'var(--teal)' },
          { label: 'Locations', value: String(totalLocations), icon: <Building size={16} />, color: 'var(--violet)' },
          { label: 'Total Staff', value: String(totalStaff), icon: <Users size={16} />, color: 'var(--success)' },
          { label: 'Avg Quality', value: avgQuality, icon: <Star size={16} />, color: 'var(--gold)' },
        ].map((kpi, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${kpi.color}`, padding: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: kpi.color }}>{kpi.icon}<span className="kpi-label" style={{ fontSize: '0.65rem' }}>{kpi.label}</span></div>
            <span className="kpi-value" style={{ fontSize: '1.3rem' }}>{kpi.value}</span>
          </motion.div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Revenue by region bar */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card">
          <h4 style={{ marginBottom: 16 }}>Revenue by Region (₹ Lakhs)</h4>
          {revenueByRegion.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={revenueByRegion}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="region" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="revenue" fill="#C9A96E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No data available</div>
          )}
        </motion.div>

        {/* Location comparison */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="card">
          <h4 style={{ marginBottom: 16 }}>Location Performance</h4>
          {locations.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={locations.slice(0, 8).map((l: any) => ({ name: (l.name ?? '').substring(0, 10), quality: l.avg_quality ?? 0, revenue: ((l.revenue ?? 0) / 100000) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="revenue" fill="#2A9D8F" radius={[4, 4, 0, 0]} name="Revenue (₹L)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No data available</div>
          )}
        </motion.div>
      </div>

      {/* Location table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4>Location Breakdown</h4>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr><th>Location</th><th>City</th><th>Revenue (₹L)</th><th>Quality</th><th>Bookings</th></tr>
            </thead>
            <tbody>
              {locations.length === 0 ? (
                <tr><td colSpan={5} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>No location data available</td></tr>
              ) : locations.map((l: any, i: number) => (
                <tr key={l.id || i}>
                  <td style={{ fontWeight: 500 }}>{l.name ?? ''}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{l.city ?? ''}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--gold)' }}>₹{((l.revenue ?? 0) / 100000).toFixed(1)}L</td>
                  <td><Star size={12} style={{ color: 'var(--gold)', verticalAlign: 'middle' }} /> {l.avg_quality ?? '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{l.bookings_count ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
