import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Users, Star, AlertTriangle, Award } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../../config/api';

const RISK_COLORS: Record<string, string> = { low: '#2A9D8F', medium: '#E8A87C', high: '#f44f9a' };
const STATUS_COLORS: Record<string, string> = { low: '#f0fdf4', medium: '#fff7ed', high: '#fef2f2' };
const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem', color: '#fff' };

export default function TeamManagement() {
  const { data: staffData, isLoading } = useQuery({
    queryKey: ['analytics-staff'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
  });

  const { data: attritionData } = useQuery({
    queryKey: ['analytics-attrition'],
    queryFn: () => api.get('/analytics/attrition').then(r => r.data?.data),
  });

  const team = staffData?.staff || [];
  const totalStaff = team.length;
  const avgRating = totalStaff > 0 ? (team.reduce((s: number, t: any) => s + (Number(t.current_rating) || 0), 0) / totalStaff).toFixed(1) : '0';
  const soulskinCert = team.filter((t: any) => t.soulskin_certified).length;
  const highRisk = attritionData?.risk_distribution?.high || team.filter((t: any) => t.attrition_risk === 'high').length;

  const chartData = team.slice(0, 8).map((t: any) => ({
    name: t.name?.split(' ')[0] || 'Unknown',
    revenue: Math.round((t.total_revenue || 0) / 100000 * 10) / 10,
    services: t.total_services || 0,
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}><Users size={28} style={{ color: 'var(--teal)' }} /> Team</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{totalStaff} staff members</p>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Team Size', value: totalStaff.toString(), icon: Users, color: '#2A9D8F' },
          { label: 'Avg Rating', value: avgRating, icon: Star, color: '#f44f9a' },
          { label: 'SOULSKIN Cert', value: `${soulskinCert}/${totalStaff}`, icon: Award, color: '#9B7FD4' },
          { label: 'Retention Risk', value: highRisk.toString(), icon: AlertTriangle, color: '#E8611A' },
        ].map((k, i) => {
          const Icon = k.icon;
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
              <TiltCard tiltIntensity={8} style={{ borderLeft: `4px solid ${k.color}`, padding: '24px', background: '#fff', height: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span className="kpi-label" style={{ fontWeight: 600, fontSize: '0.75rem', letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>{k.label}</span>
                  <div style={{ width: 28, height: 28, borderRadius: 6, background: `${k.color}10`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={14} color={k.color} />
                  </div>
                </div>
                <span className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 700 }}>{k.value}</span>
              </TiltCard>
            </motion.div>
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Team table */}
        <TiltCard tiltIntensity={3} className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4>Staff Members</h4>
          </div>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table>
              <thead>
                <tr><th>Name</th><th>Level</th><th>Rating</th><th>Services</th><th>Revenue</th><th>Risk</th></tr>
              </thead>
              <tbody>
                {team.length > 0 ? team.map((t: any, i: number) => {
                  const risk = t.attrition_risk || 'low';
                  const revLakhs = ((Number(t.total_revenue) || 0) / 100000).toFixed(1);
                  return (
                    <tr key={i} style={{ borderBottom: i < team.length - 1 ? '1px solid rgba(0,0,0,0.03)' : 'none' }}>
                      <td style={{ padding: '16px 20px' }}>
                        <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 10, color: '#1A1A24', fontSize: '0.9rem' }}>
                          {t.name}
                          {t.soulskin_certified && <div style={{ background: 'rgba(155,127,212,0.1)', padding: '2px 8px', borderRadius: 4, fontSize: '0.6rem', color: '#9B7FD4', fontWeight: 800, letterSpacing: '0.05em' }}>CERTIFIED</div>}
                        </div>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>{t.skill_level}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontWeight: 700, fontSize: '0.85rem' }}>
                          <Star size={12} fill="#f44f9a" color="#f44f9a" /> {(Number(t.current_rating) || 0).toFixed(1)}
                        </div>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>{t.total_services || 0}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', color: '#f44f9a', fontWeight: 600 }}>₹{revLakhs}L</td>
                      <td>
                        <span style={{
                          color: RISK_COLORS[risk] || RISK_COLORS.low,
                          background: STATUS_COLORS[risk] || STATUS_COLORS.low,
                          fontWeight: 700, fontSize: '0.65rem',
                          padding: '4px 10px', borderRadius: 5,
                          letterSpacing: '0.05em', textTransform: 'uppercase',
                        }}>{risk}</span>
                      </td>
                    </tr>
                  );
                }) : (
                  <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 32 }}>
                    {isLoading ? 'Loading...' : 'No staff data available'}
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
        </TiltCard>

        {/* Revenue comparison */}
        <TiltCard tiltIntensity={3} className="card">
          <h4 style={{ marginBottom: 16 }}>Revenue Comparison (₹L)</h4>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#252530" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" width={80} tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontWeight: 500 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: 'rgba(244,79,154,0.05)' }} />
                <Bar dataKey="revenue" fill="#f44f9a" radius={[0, 4, 4, 0]} barSize={24} name="Revenue (₹L)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No data</div>
          )}
        </TiltCard>
      </div>
    </div>
  );
}
