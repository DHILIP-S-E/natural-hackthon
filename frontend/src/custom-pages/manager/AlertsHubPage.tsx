import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, CloudSun, Flag, Bell } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import api from '../../config/api';

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

function EmptyState({ text }: { text: string }) {
  return (
    <TiltCard tiltIntensity={3} style={{ padding: '32px', background: '#fff', textAlign: 'center' }}>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{text}</p>
    </TiltCard>
  );
}

function LoadingCard() {
  return <div className="card" style={{ padding: 20, height: 64, background: 'var(--bg-card)', animation: 'pulse 1.5s ease-in-out infinite' }} />;
}

export default function AlertsHubPage() {
  const { data: climateAlerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['climate-alerts'],
    queryFn: () => api.get('/climate/alerts').then(r => r.data?.data),
  });

  const { data: notifications, isLoading: notifsLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.get('/notifications').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.notifications || [];
    }),
  });

  const { data: qualityFlags, isLoading: flagsLoading } = useQuery({
    queryKey: ['quality-flagged'],
    queryFn: () => api.get('/quality/?per_page=10').then(r => {
      const data = r.data?.data || [];
      return (Array.isArray(data) ? data : []).filter((a: any) => a.is_flagged);
    }),
  });

  const alerts: any[] = climateAlerts || [];
  const notifs: any[] = notifications || [];
  const flags: any[] = qualityFlags || [];

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
          {alertsLoading ? <LoadingCard /> : alerts.length === 0 ? (
            <EmptyState text="No climate alerts — conditions are normal" />
          ) : alerts.map((alert: any, i: number) => {
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
          {flagsLoading ? <LoadingCard /> : flags.length > 0 ? flags.map((flag: any, i: number) => {
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
          ) : (
            <EmptyState text="No quality flags — all scores above threshold" />
          )}
        </motion.div>
      </div>

      {/* Notifications */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Bell size={18} /> Recent Notifications</h4>
        </div>
        <div>
          {notifsLoading ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading notifications...</div>
          ) : notifs.length === 0 ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>No notifications yet</div>
          ) : notifs.map((n: any, i: number) => (
            <div key={n.id || i} style={{
              padding: '14px 20px',
              borderBottom: i < notifs.length - 1 ? '1px solid var(--border-subtle)' : 'none',
              display: 'flex', alignItems: 'center', gap: 12,
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
                background: NOTIF_COLORS[n.notification_type || n.type] || 'var(--text-muted)',
              }} />
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-primary)' }}>{n.title}</p>
                {n.body && <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 2 }}>{n.body}</p>}
              </div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {n.created_at ? new Date(n.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}
              </span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
