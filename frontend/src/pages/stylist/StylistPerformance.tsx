import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Star, Trophy, TrendingUp, Scissors, Award, Heart } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useAuthStore } from '../../stores/authStore';
import api from '../../config/api';

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem' };

export default function StylistPerformance() {
  const user = useAuthStore(s => s.user);

  const { data: staffData } = useQuery({
    queryKey: ['analytics-staff'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
  });

  const { data: qualityData } = useQuery({
    queryKey: ['quality-assessments-mine'],
    queryFn: () => api.get('/quality/?per_page=10').then(r => r.data?.data || []),
  });

  const { data: feedbackData } = useQuery({
    queryKey: ['feedback-mine'],
    queryFn: () => api.get('/feedback/?per_page=5').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.feedback || [];
    }),
  });

  const { data: skillData } = useQuery({
    queryKey: ['analytics-skill-gap'],
    queryFn: () => api.get('/analytics/skill-gap').then(r => r.data?.data),
  });

  // Find current user's staff profile
  const allStaff = staffData?.staff || [];
  const myProfile = allStaff.find((s: any) =>
    (s.name ?? '').toLowerCase().includes((user?.first_name ?? '').toLowerCase() || '___')
  ) || allStaff[0];

  const ranking = myProfile ? allStaff.indexOf(myProfile) + 1 : 0;
  const totalRevenue = myProfile ? Math.round((Number(myProfile.total_revenue) || 0) / 100000 * 10) / 10 : 0;
  const totalServices = Number(myProfile?.total_services) || 0;
  const avgRating = Number(myProfile?.current_rating) || 0;
  const soulskinCert = myProfile?.soulskin_certified || false;
  const specializations = myProfile?.specializations || [];

  const recentFeedback = feedbackData || [];

  // Build skills from specializations
  const skills = specializations.map((s: string, i: number) => ({
    name: s,
    level: Math.max(60, 95 - i * 5),
    certification: i === 0 ? 'Primary' : 'Trained',
  }));
  if (soulskinCert) {
    skills.push({ name: 'SOULSKIN', level: 95, certification: 'Certified' });
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem' }}>My Performance</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          {myProfile?.name || user?.first_name || 'Stylist'} · {myProfile?.skill_level || 'L1'}
        </p>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Total Revenue', value: `₹${totalRevenue}L`, icon: <TrendingUp size={16} />, color: 'var(--gold)' },
          { label: 'Services Done', value: totalServices.toString(), icon: <Scissors size={16} />, color: 'var(--teal)' },
          { label: 'Avg Rating', value: avgRating.toFixed(1), icon: <Star size={16} />, color: 'var(--gold)' },
          { label: 'SOULSKIN', value: soulskinCert ? 'Certified' : 'Pending', icon: <Heart size={16} />, color: 'var(--violet)' },
          { label: 'Ranking', value: ranking > 0 ? `#${ranking}` : '—', icon: <Trophy size={16} />, color: 'var(--success)' },
        ].map((k, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${k.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: k.color }}>{k.icon}<span className="kpi-label">{k.label}</span></div>
            <span className="kpi-value" style={{ fontSize: '1.3rem' }}>{k.value}</span>
          </motion.div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Leaderboard comparison */}
        <div className="card">
          <h4 style={{ marginBottom: 16 }}>Team Leaderboard (₹ Lakhs)</h4>
          {allStaff.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={allStaff.slice(0, 6).map((s: any) => ({
                name: s.name?.split(' ')[0] || 'Unknown',
                revenue: Math.round((s.total_revenue || 0) / 100000 * 10) / 10,
                isMe: s === myProfile,
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#252530" />
                <XAxis dataKey="name" tick={{ fill: '#5C5A70', fontSize: 11 }} />
                <YAxis tick={{ fill: '#5C5A70', fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="revenue" fill="#C9A96E" radius={[4, 4, 0, 0]} name="Revenue (₹L)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Loading...</div>
          )}
        </div>

        {/* Skills */}
        <div className="card">
          <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}><Award size={16} /> Skill Matrix</h4>
          {skills.length > 0 ? skills.map((s: any, i: number) => (
            <div key={i} style={{ marginBottom: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                <span>{s.name}</span>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>{s.certification}</span>
              </div>
              <div style={{ height: 6, background: 'var(--border-subtle)', borderRadius: 3 }}>
                <motion.div initial={{ width: 0 }} animate={{ width: `${s.level}%` }} transition={{ delay: 0.3 + i * 0.1, duration: 0.5 }}
                  style={{ height: '100%', background: s.level > 90 ? 'var(--gold)' : 'var(--teal)', borderRadius: 3 }} />
              </div>
            </div>
          )) : (
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No skills recorded yet</div>
          )}
        </div>
      </div>

      {/* Reviews */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4>Recent Reviews</h4>
        </div>
        {recentFeedback.length > 0 ? recentFeedback.map((r: any, i: number) => {
          const rating = r.overall_rating || 0;
          const dateStr = r.created_at ? new Date(r.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) : '';
          return (
            <div key={i} style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontWeight: 500, fontSize: '0.85rem' }}>{r.customer_name || 'Customer'}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  {Array.from({ length: rating }).map((_, j) => <Star key={j} size={12} style={{ color: 'var(--gold)', fill: 'var(--gold)' }} />)}
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 6 }}>{dateStr}</span>
                </div>
              </div>
              {r.comment && <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>"{r.comment}"</p>}
            </div>
          );
        }) : (
          <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>No reviews yet</div>
        )}
      </div>
    </div>
  );
}
