import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Users2, Clock, UserCheck, Play, CheckCircle, Plus, Bell } from 'lucide-react';
import ArchetypeBadge from '../../components/ArchetypeBadge';
import api from '../../config/api';

const STATUS_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  waiting: { bg: 'rgba(244,162,97,0.1)', color: 'var(--warning)', label: 'Waiting' },
  assigned: { bg: 'rgba(42,157,143,0.1)', color: 'var(--teal)', label: 'Assigned' },
  in_service: { bg: 'rgba(201,169,110,0.1)', color: 'var(--gold)', label: 'In Service' },
  completed: { bg: 'rgba(82,183,136,0.1)', color: 'var(--success)', label: 'Completed' },
  left: { bg: 'rgba(231,111,111,0.1)', color: 'var(--error)', label: 'Left' },
};

const SOURCE_ICONS: Record<string, string> = { walk_in: '\uD83D\uDEB6', whatsapp: '\uD83D\uDCAC', app_checkin: '\uD83D\uDCF1' };

export default function QueueManagement() {
  const queryClient = useQueryClient();

  // Fetch locations to get the user's active location
  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: () => api.get('/locations').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.locations || d?.items || [];
    }),
  });

  const locationId = locations?.[0]?.id || '';
  const locationName = locations?.[0]?.name || 'Location';

  const { data: queueData } = useQuery({
    queryKey: ['queue', locationId],
    queryFn: () => api.get(`/queue/${locationId}`).then(r => r.data?.data),
    enabled: !!locationId,
    refetchInterval: 15_000, // Live queue: refresh every 15 seconds
  });

  const queue = Array.isArray(queueData) ? queueData : queueData?.entries || [];
  const recentlyServed: any[] = queueData?.recentlyServed || [];

  const assignMutation = useMutation({
    mutationFn: (entryId: number) => api.patch(`/queue/${locationId}/entries/${entryId}/assign`).then(r => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['queue', locationId] }),
  });

  const startMutation = useMutation({
    mutationFn: (entryId: number) => api.patch(`/queue/${locationId}/entries/${entryId}/start`).then(r => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['queue', locationId] }),
  });

  const completeMutation = useMutation({
    mutationFn: (entryId: number) => api.patch(`/queue/${locationId}/entries/${entryId}/complete`).then(r => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['queue', locationId] }),
  });

  const avgWait = Math.round(queue.filter((q: any) => q.status === 'waiting').reduce((sum: number, q: any) => sum + (q.waitMin ?? 0), 0) / Math.max(queue.filter((q: any) => q.status === 'waiting').length, 1));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}><Users2 size={28} style={{ color: 'var(--teal)' }} /> Smart Queue</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{locationName} · Real-time walk-in management</p>
        </div>
        <button className="btn btn-primary"><Plus size={16} /> Add Walk-In</button>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'In Queue', value: queue.filter((q: any) => q.status === 'waiting').length.toString(), icon: <Users2 size={18} />, color: 'var(--warning)' },
          { label: 'Avg Wait', value: `${avgWait} min`, icon: <Clock size={18} />, color: 'var(--teal)' },
          { label: 'Assigned', value: queue.filter((q: any) => q.status === 'assigned').length.toString(), icon: <UserCheck size={18} />, color: 'var(--gold)' },
          { label: 'Served Today', value: `${recentlyServed.length + queue.filter((q: any) => q.status === 'completed').length}`, icon: <CheckCircle size={18} />, color: 'var(--success)' },
        ].map((kpi, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${kpi.color}`, padding: 'var(--space-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: kpi.color }}>
              {kpi.icon}<span className="kpi-label">{kpi.label}</span>
            </div>
            <span className="kpi-value" style={{ fontSize: '1.5rem' }}>{kpi.value}</span>
          </motion.div>
        ))}
      </div>

      {/* Queue table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4>Active Queue</h4>
          <div style={{ display: 'flex', gap: 8 }}>
            {['All', 'Waiting', 'Assigned'].map(f => (
              <button key={f} className="btn btn-ghost btn-sm" style={{ padding: '4px 12px' }}>{f}</button>
            ))}
          </div>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Customer</th>
                <th>Service</th>
                <th>Stylist</th>
                <th>Wait</th>
                <th>Source</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {queue.map((q: any, i: number) => {
                const st = STATUS_STYLES[q.status];
                return (
                  <motion.tr key={q.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{q.position || '\u2014'}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontWeight: 500 }}>{q.name}</span>
                        {q.archetype && <ArchetypeBadge archetype={q.archetype} size="sm" showLabel={false} />}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{q.phone}</div>
                    </td>
                    <td style={{ fontSize: '0.85rem' }}>{q.service}</td>
                    <td style={{ fontSize: '0.85rem', color: q.stylist ? 'var(--text-primary)' : 'var(--text-muted)' }}>{q.stylist || 'Unassigned'}</td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: q.waitMin > 10 ? 'var(--warning)' : 'var(--text-secondary)' }}>
                        {q.waitMin} min
                      </span>
                    </td>
                    <td>{SOURCE_ICONS[q.source]} <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{(q.source ?? '').replace('_', ' ')}</span></td>
                    <td><span className="badge" style={{ background: st.bg, color: st.color, border: `1px solid ${st.color}30` }}>{st.label}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: 4 }}>
                        {q.status === 'waiting' && (
                          <button className="btn btn-teal btn-sm" style={{ padding: '4px 8px' }}
                            onClick={() => assignMutation.mutate(q.id)}
                            disabled={assignMutation.isPending}>
                            <UserCheck size={12} />
                          </button>
                        )}
                        {q.status === 'assigned' && (
                          <button className="btn btn-primary btn-sm" style={{ padding: '4px 8px' }}
                            onClick={() => startMutation.mutate(q.id)}
                            disabled={startMutation.isPending}>
                            <Play size={12} />
                          </button>
                        )}
                        {q.status === 'in_service' && (
                          <button className="btn btn-success btn-sm" style={{ padding: '4px 8px' }}
                            onClick={() => completeMutation.mutate(q.id)}
                            disabled={completeMutation.isPending}>
                            <CheckCircle size={12} />
                          </button>
                        )}
                        <button className="btn btn-ghost btn-sm" style={{ padding: '4px 8px' }}><Bell size={12} /></button>
                      </div>
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recently Served */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><CheckCircle size={18} style={{ color: 'var(--success)' }} /> Recently Served</h4>
        </div>
        {recentlyServed.map((r: any, i: number) => (
          <div key={i} style={{ padding: '10px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{r.name}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: 12 }}>{r.service}</span>
            </div>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Waited {r.waitedMin}m</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{r.completedAt}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
