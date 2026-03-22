import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, CloudSun, Flag, Bell } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import api from '../../config/api';

// Empty defaults for when API data is not yet loaded
const EMPTY_ALERTS: any[] = [];
const EMPTY_FLAGS: any[] = [];
const EMPTY_NOTIFICATIONS: any[] = [];

const SEVERITY_COLORS: Record<string, { dot: string; border: string }> = {
  warning: { dot: 'var(--warning)', border: 'rgba(244,162,97,0.3)' },
  info: { dot: 'var(--info)', border: 'rgba(74,159,212,0.3)' },
  error: { dot: 'var(--error)', border: 'rgba(231,111,111,0.3)' },
};

const NOTIF_COLORS: Record<string, string> = {
  booking: 'var(--teal)',
  achievement: 'var(--violet)',
  quality: 'var(--warning)',
  milestone: 'var(--success)',
  trend: 'var(--gold)',
};

export default function AlertsHubPage() {
  const { data: climateAlerts } = useQuery({
    queryKey: ['climate-alerts'],
    queryFn: () => api.get('/climate/alerts').then(r => r.data?.data),
    placeholderData: EMPTY_ALERTS,
  });

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.get('/notifications').then(r => r.data?.data),
    placeholderData: EMPTY_NOTIFICATIONS,
  });

  const { data: qualityFlags } = useQuery({
    queryKey: ['quality-flagged'],
    queryFn: () => api.get('/quality/?per_page=10').then(r => {
      const data = r.data?.data || [];
      return (Array.isArray(data) ? data : []).filter((a: any) => a.is_flagged);
    }),
    placeholderData: EMPTY_FLAGS,
  });

  const alerts = climateAlerts || EMPTY_ALERTS;
  const notifs = notifications || EMPTY_NOTIFICATIONS;
  const flags = qualityFlags || EMPTY_FLAGS;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <AlertTriangle size={28} style={{ color: 'var(--warning)' }} />
          Alerts Hub
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          Climate alerts, quality flags, and system notifications
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Climate Alerts */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <CloudSun size={18} style={{ color: 'var(--warning)' }} /> Climate Alerts
          </h3>
          {alerts.map((alert: any, i: number) => {
            const sev = SEVERITY_COLORS[alert.severity] || SEVERITY_COLORS.info;
            return (
              <TiltCard key={alert.id || i} tiltIntensity={5} style={{
                padding: '20px', background: '#fff',
                borderLeft: `4px solid ${sev.dot}`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{alert.title}</span>
                  <span className={`badge ${alert.severity === 'warning' ? 'badge-warning' : 'badge-teal'}`} style={{ fontSize: '0.6rem', padding: '2px 8px' }}>
                    {(alert.severity ?? '').toUpperCase()}
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{alert.message}</p>
              </TiltCard>
            );
          })}
        </motion.div>

        {/* Quality Flags */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Flag size={18} style={{ color: 'var(--error)' }} /> Quality Flags
          </h3>
          {flags.length > 0 ? flags.map((flag: any, i: number) => {
            const score = flag.overall_score ? (Number(flag.overall_score) / 20).toFixed(1) : Number(flag.score) || 0;
            const scoreNum = typeof score === 'string' ? parseFloat(score) : score;
            return (
              <TiltCard key={flag.id || i} tiltIntensity={5} style={{
                padding: '20px', background: '#fff',
                borderLeft: '4px solid var(--error)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{flag.stylist || 'Stylist'}</span>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '0.85rem',
                    color: scoreNum < 4 ? 'var(--error)' : 'var(--warning)',
                  }}>{score}</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{flag.flag_reason || flag.issue || 'Score below threshold'}</p>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 8 }}>
                  {flag.created_at ? new Date(flag.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) : ''}
                </div>
              </TiltCard>
            );
          }) : (
            <TiltCard tiltIntensity={3} style={{ padding: '32px', background: '#fff', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No quality flags — all scores above threshold</p>
            </TiltCard>
          )}
        </motion.div>
      </div>

      {/* Notifications */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Bell size={18} /> Recent Notifications</h4>
        </div>
        <div>
          {notifs.map((n: any, i: number) => (
            <div key={n.id || i} style={{
              padding: '14px 20px',
              borderBottom: i < notifs.length - 1 ? '1px solid var(--border-subtle)' : 'none',
              display: 'flex', alignItems: 'center', gap: 12,
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
                background: NOTIF_COLORS[n.type] || 'var(--text-muted)',
              }} />
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{n.message}</p>
              </div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{n.time}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
