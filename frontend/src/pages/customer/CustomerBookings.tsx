import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin, Scissors, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import ArchetypeBadge from '../../components/ArchetypeBadge';
import api from '../../config/api';

const STATUS_STYLE: Record<string, { bg: string; color: string; icon: React.ReactNode; label: string }> = {
  confirmed: { bg: 'rgba(42,157,143,0.1)', color: 'var(--teal)', icon: <CheckCircle size={12} />, label: 'Confirmed' },
  completed: { bg: 'rgba(82,183,136,0.1)', color: 'var(--success)', icon: <CheckCircle size={12} />, label: 'Completed' },
  cancelled: { bg: 'rgba(231,111,111,0.1)', color: 'var(--error)', icon: <XCircle size={12} />, label: 'Cancelled' },
  pending: { bg: 'rgba(244,162,97,0.1)', color: 'var(--warning)', icon: <AlertCircle size={12} />, label: 'Pending' },
  checked_in: { bg: 'rgba(42,157,143,0.1)', color: 'var(--teal)', icon: <CheckCircle size={12} />, label: 'Checked In' },
  in_progress: { bg: 'rgba(155,127,212,0.1)', color: '#9B7FD4', icon: <CheckCircle size={12} />, label: 'In Progress' },
  no_show: { bg: 'rgba(231,111,111,0.1)', color: 'var(--error)', icon: <XCircle size={12} />, label: 'No Show' },
};

export default function CustomerBookings() {
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'past'>('all');

  // Fetch bookings from API
  const { data: apiBookings, isLoading } = useQuery({
    queryKey: ['customer-bookings'],
    queryFn: () => api.get('/bookings?page=1&per_page=20').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.bookings || d?.items || [];
    }),
  });

  // Map API response to the shape the UI expects
  const BOOKINGS = (apiBookings || []).map((b: any) => ({
    id: b.booking_number || b.id,
    service: b.service_name || b.service || 'Service',
    location: b.location_name || b.location || '',
    stylist: b.stylist_name || b.stylist || '',
    date: b.scheduled_at ? new Date(b.scheduled_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '',
    time: b.scheduled_at ? new Date(b.scheduled_at).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }) : '',
    status: b.status || 'pending',
    price: Number(b.final_price ?? b.base_price) || 0,
    archetype: b.archetype || b.soulskin_archetype || null,
  }));

  const filtered = BOOKINGS.filter((b: any) => {
    if (filter === 'upcoming') return b.status === 'confirmed' || b.status === 'pending' || b.status === 'checked_in';
    if (filter === 'past') return b.status === 'completed' || b.status === 'cancelled' || b.status === 'no_show';
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem' }}>My Bookings</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{BOOKINGS.length} total · {BOOKINGS.filter((b: any) => b.status === 'confirmed').length} upcoming</p>
        </div>
        <a href="/app/book" className="btn btn-primary"><Calendar size={16} /> Book New</a>
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        {(['all', 'upcoming', 'past'] as const).map(f => (
          <button key={f} onClick={() => setFilter(f)} className={`btn ${filter === f ? 'btn-teal' : 'btn-ghost'} btn-sm`}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
        {isLoading && !apiBookings ? (
          // Loading skeleton
          [...Array(4)].map((_, i) => (
            <div key={i} className="card" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)', background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%' }} />
                <div>
                  <div style={{ width: 150, height: 16, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4, marginBottom: 6 }} />
                  <div style={{ width: 220, height: 12, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} />
                </div>
              </div>
              <div style={{ width: 80, height: 24, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} />
            </div>
          ))
        ) : filtered.length === 0 ? (
          <div className="card" style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No bookings found.
          </div>
        ) : (
          filtered.map((b: any, i: number) => {
            const st = STATUS_STYLE[b.status] || STATUS_STYLE.pending;
            return (
              <motion.div key={b.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                className="card" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                  <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)', background: 'var(--bg-surface)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Scissors size={18} style={{ color: 'var(--gold)' }} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                      {b.service}
                      {b.archetype && <ArchetypeBadge archetype={b.archetype} size="sm" showLabel={false} />}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 8, marginTop: 2 }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}><Calendar size={10} /> {b.date}</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}><Clock size={10} /> {b.time}</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}><MapPin size={10} /> {b.location}</span>
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>₹{(Number(b.price) || 0).toLocaleString()}</span>
                  <span className="badge" style={{ background: st.bg, color: st.color, display: 'flex', alignItems: 'center', gap: 4 }}>
                    {st.icon} {st.label}
                  </span>
                </div>
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
}
