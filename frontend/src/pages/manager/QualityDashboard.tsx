import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Star, CheckCircle, BarChart3, Sparkles, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../../config/api';

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem' };

export default function QualityDashboard() {
  const { data: stats } = useQuery({
    queryKey: ['quality-stats'],
    queryFn: () => api.get('/quality/stats/summary').then(r => r.data?.data),
  });

  const { data: assessments } = useQuery({
    queryKey: ['quality-assessments'],
    queryFn: () => api.get('/quality/?per_page=20').then(r => r.data?.data || []),
  });

  const { data: analyticsQuality } = useQuery({
    queryKey: ['analytics-quality'],
    queryFn: () => api.get('/analytics/quality?days=30').then(r => r.data?.data),
  });

  const { data: staffData } = useQuery({
    queryKey: ['analytics-staff'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
  });

  const avgOverall = Number(stats?.avg_overall_score || analyticsQuality?.avg_overall_score) || 0;
  const avgSop = Number(stats?.avg_sop_compliance || analyticsQuality?.avg_sop_compliance) || 0;
  const avgTiming = Number(stats?.avg_timing_score || analyticsQuality?.avg_timing_score) || 0;
  const totalAssessments = Number(stats?.total_assessments || analyticsQuality?.total_assessments) || 0;
  const flaggedCount = Number(stats?.flagged_count || analyticsQuality?.flagged_count) || 0;

  const recentAssessments = Array.isArray(assessments) ? assessments : [];

  // Build stylist name map from staff data
  const staffMap: Record<string, string> = {};
  if (staffData?.staff) {
    for (const s of staffData.staff) {
      staffMap[s.id] = s.name;
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Star size={28} style={{ color: 'var(--gold)' }} /> Quality Dashboard
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Service quality scoring, consistency tracking, and SOULSKIN alignment</p>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Overall Quality', value: (avgOverall / 20).toFixed(1), icon: <Star size={16} />, color: 'var(--gold)' },
          { label: 'SOP Compliance', value: `${avgSop.toFixed(0)}%`, icon: <CheckCircle size={16} />, color: 'var(--teal)' },
          { label: 'Timing Score', value: `${avgTiming.toFixed(0)}%`, icon: <BarChart3 size={16} />, color: 'var(--violet)' },
          { label: 'Assessments', value: totalAssessments.toString(), icon: <Sparkles size={16} />, color: 'var(--success)' },
          { label: 'Flagged', value: flaggedCount.toString(), icon: <AlertTriangle size={16} />, color: flaggedCount > 0 ? 'var(--error)' : 'var(--text-muted)' },
        ].map((k, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${k.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: k.color }}>{k.icon}<span className="kpi-label">{k.label}</span></div>
            <span className="kpi-value" style={{ fontSize: '1.3rem' }}>{k.value}</span>
          </motion.div>
        ))}
      </div>

      {/* Recent assessments */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4>Recent Assessments ({recentAssessments.length})</h4>
        </div>
        {recentAssessments.length > 0 ? recentAssessments.map((a: any, i: number) => {
          const score = a.overall_score ? (Number(a.overall_score) / 20).toFixed(1) : '—';
          const scoreNum = a.overall_score ? Number(a.overall_score) / 20 : 0;
          const sopPct = a.sop_compliance_score != null ? Number(a.sop_compliance_score).toFixed(0) : '—';
          const soulskin = a.soulskin_alignment_score ? (Number(a.soulskin_alignment_score) / 20).toFixed(1) : null;
          const stylistName = staffMap[a.stylist_id] || 'Stylist';
          const dateStr = a.created_at ? new Date(a.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) : '';

          return (
            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}
              style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{stylistName}</span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>· {dateStr}</span>
                  {a.is_flagged && <span style={{ fontSize: '0.6rem', color: 'var(--error)', background: 'rgba(231,111,111,0.1)', padding: '1px 6px', borderRadius: 4 }}>FLAGGED</span>}
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  SOP: {sopPct}% · Timing: {a.timing_score != null ? Number(a.timing_score).toFixed(0) : '—'}%
                  {a.ai_feedback && ` · ${a.ai_feedback.substring(0, 80)}...`}
                </p>
              </div>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: scoreNum >= 4.5 ? 'var(--success)' : scoreNum >= 3.5 ? 'var(--warning)' : 'var(--error)' }}>{score}</div>
                  <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>Score</div>
                </div>
                {soulskin && (
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--violet)' }}>{soulskin}</div>
                    <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>SOUL</div>
                  </div>
                )}
                {a.customer_rating && (
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Star size={10} style={{ color: 'var(--gold)' }} />{a.customer_rating}
                    </div>
                    <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>Cust</div>
                  </div>
                )}
              </div>
            </motion.div>
          );
        }) : (
          <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>No quality assessments recorded yet</div>
        )}
      </div>
    </div>
  );
}
