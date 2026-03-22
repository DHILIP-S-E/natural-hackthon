import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { MapPin, DollarSign, Star, Users, Calendar, Activity } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import api from '../../config/api';

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem', color: '#fff' };

export default function LocationDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: loc, isLoading: locLoading } = useQuery({
    queryKey: ['location', id],
    queryFn: () => api.get(`/locations/${id}`).then(r => r.data?.data),
    enabled: !!id,
  });

  const { data: staffRaw } = useQuery({
    queryKey: ['analytics-staff', id],
    queryFn: () => api.get(`/analytics/staff?location_id=${id}`).then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.staff || d?.items || [];
    }),
    enabled: !!id,
  });

  const { data: soulskinRaw } = useQuery({
    queryKey: ['analytics-soulskin', id],
    queryFn: () => api.get(`/analytics/soulskin?location_id=${id}`).then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.distribution || d?.items || [];
    }),
    enabled: !!id,
  });

  const staff = Array.isArray(staffRaw) ? staffRaw : [];
  const soulskinData = Array.isArray(soulskinRaw) ? soulskinRaw : [];

  if (locLoading || !loc) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300, color: 'var(--text-muted)' }}>
        Loading location details...
      </div>
    );
  }

  const monthlyRevenue = loc.monthly_revenue || [];

  const kpis = [
    { label: 'Monthly Revenue', value: `\u20B9${((loc.revenue ?? 0) / 100000).toFixed(1)}L`, icon: DollarSign, color: 'var(--gold)' },
    { label: 'Quality Score', value: loc.quality_score != null ? String(loc.quality_score) : '-', icon: Star, color: 'var(--violet)' },
    { label: 'Bookings', value: loc.bookings_count != null ? String(loc.bookings_count) : '-', icon: Calendar, color: 'var(--teal)' },
    { label: 'Staff', value: String(loc.staff_count || staff.length || 0), icon: Users, color: 'var(--success)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card" style={{ borderLeft: '4px solid var(--teal)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
              <MapPin size={28} style={{ color: 'var(--teal)' }} />
              {loc.name || 'Location'}
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
              {loc.city || ''} &middot; Code: {loc.code || ''} &middot; Capacity: {loc.capacity || loc.seating_capacity || 8} chairs
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="badge badge-success" style={{ textTransform: 'uppercase', fontSize: '0.65rem' }}>{loc.status || 'active'}</span>
            {loc.soulskin_enabled && <span className="badge badge-violet">SOULSKIN</span>}
          </div>
        </div>
      </motion.div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-md)' }}>
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
              <TiltCard tiltIntensity={8} style={{ borderLeft: `4px solid ${kpi.color}`, padding: '24px', background: '#fff', height: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span style={{ fontWeight: 600, fontSize: '0.75rem', letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>{kpi.label}</span>
                  <div style={{ width: 28, height: 28, borderRadius: 6, background: `${kpi.color}10`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={14} color={kpi.color} />
                  </div>
                </div>
                <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{kpi.value}</span>
              </TiltCard>
            </motion.div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Revenue Trend */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <TiltCard tiltIntensity={3} className="card">
            <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <DollarSign size={18} style={{ color: 'var(--gold)' }} /> Monthly Revenue Trend
            </h4>
            {monthlyRevenue.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={monthlyRevenue}>
                  <defs>
                    <linearGradient id="revGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f44f9a" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#f44f9a" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                  <XAxis dataKey="month" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${v / 100000}L`} />
                  <Tooltip contentStyle={tooltipStyle} formatter={(v: any) => [`\u20B9${((Number(v) || 0) / 1000).toFixed(0)}K`, 'Revenue']} />
                  <Area type="monotone" dataKey="revenue" stroke="#f44f9a" fill="url(#revGradient)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No revenue data available</div>
            )}
          </TiltCard>
        </motion.div>

        {/* SOULSKIN Donut */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <TiltCard tiltIntensity={3} className="card">
            <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={18} style={{ color: 'var(--violet)' }} /> SOULSKIN Adoption
            </h4>
            {soulskinData.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={soulskinData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3}>
                      {soulskinData.map((entry: any, index: number) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={tooltipStyle} />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                  {soulskinData.map((d: any, i: number) => (
                    <span key={i} style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <div style={{ width: 8, height: 8, borderRadius: '50%', background: d.color }} />
                      {d.name} ({d.value}%)
                    </span>
                  ))}
                </div>
              </>
            ) : (
              <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No SOULSKIN data available</div>
            )}
          </TiltCard>
        </motion.div>
      </div>

      {/* Staff Mini-Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Users size={18} /> Staff ({staff.length})</h4>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr><th>Name</th><th>Role</th><th>Rating</th><th>Services</th></tr>
            </thead>
            <tbody>
              {staff.length === 0 ? (
                <tr><td colSpan={4} style={{ textAlign: 'center', padding: 24, color: 'var(--text-muted)' }}>No staff data available</td></tr>
              ) : staff.slice(0, 5).map((s: any, i: number) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, fontSize: '0.9rem', padding: '12px 20px' }}>{s.name}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.role}</td>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
                      <Star size={12} style={{ color: 'var(--gold)' }} /> {s.rating}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{s.services}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
