import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Search, AlertTriangle, Calendar, ChevronRight, Users, Activity
} from 'lucide-react';
import api from '../../config/api';
import BeautyScoreRing from '../../components/BeautyScoreRing';
import { ARCH_DATA } from '../../constants/archetypes';
import type { Archetype } from '../../types';

interface CustomerCard {
  id: string;
  name: string;
  initials: string;
  beautyScore: number;
  dominantArchetype: Archetype | null;
  lastVisit: string;
  totalVisits: number;
  allergies: string[];
  topServices: string[];
  phone?: string;
}

export default function StylistCustomers() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: customers, isLoading } = useQuery({
    queryKey: ['stylist-customers'],
    queryFn: () => api.get('/customers').then(r => {
      const d = r.data?.data;
      const items = Array.isArray(d) ? d : d?.customers || d?.items || [];
      return items.map((c: any): CustomerCard => ({
        id: c.id ?? c._id ?? '',
        name: c.name ?? '',
        initials: c.initials ?? (c.name ? c.name.split(' ').map((w: string) => w[0]).join('').toUpperCase().slice(0, 2) : '??'),
        beautyScore: c.beauty_score ?? c.beautyScore ?? 0,
        dominantArchetype: c.dominant_archetype ?? c.dominantArchetype ?? null,
        lastVisit: c.last_visit ?? c.lastVisit ?? '',
        totalVisits: c.total_visits ?? c.totalVisits ?? 0,
        allergies: c.allergies ?? [],
        topServices: c.top_services ?? c.topServices ?? [],
        phone: c.phone,
      }));
    }),
  });

  const list = customers ?? [];

  const filtered = list.filter((c: any) =>
    (c.name ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (c.topServices ?? []).some((s: any) => (s ?? '').toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Activity size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading customers...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Stylist</p>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>My Customers</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
            {list.length} assigned customers &middot; {list.filter((c: any) => c.allergies.length > 0).length} with allergy alerts
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="badge badge-teal" style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
            <Users size={12} /> {list.length} total
          </span>
        </div>
      </div>

      {/* Search */}
      <div style={{ position: 'relative' }}>
        <Search size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        <input
          type="text"
          placeholder="Search customers by name or service..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          style={{
            width: '100%', padding: '12px 12px 12px 44px', borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)',
            fontSize: '0.9rem', outline: 'none', transition: 'border-color 0.2s',
          }}
        />
      </div>

      {/* Customer Cards */}
      {filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
          <Users size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
          <p style={{ fontSize: '1rem' }}>No customers found</p>
          <p style={{ fontSize: '0.8rem' }}>Try a different search term</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 'var(--space-md)' }}>
          {filtered.map((customer: any, i: any) => {
            const archData2 = customer.dominantArchetype ? ARCH_DATA[customer.dominantArchetype] : null;
            const ArchIcon = archData2?.icon;
            return (
              <motion.div key={customer.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                className="card" style={{ padding: '20px', cursor: 'pointer', transition: 'box-shadow 0.2s' }}>
                <div style={{ display: 'flex', gap: 16 }}>
                  {/* Avatar + Score Ring */}
                  <div style={{ position: 'relative', flexShrink: 0 }}>
                    <BeautyScoreRing score={customer.beautyScore} size={64} strokeWidth={4} />
                    <div style={{
                      position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: -2 }}>
                        {customer.initials}
                      </span>
                    </div>
                  </div>

                  {/* Details */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>{customer.name}</span>
                      {archData2 && ArchIcon && (
                        <div style={{
                          background: `${archData2.color}12`, padding: '2px 8px', borderRadius: 4,
                          display: 'flex', alignItems: 'center', gap: 4,
                        }}>
                          <ArchIcon size={10} color={archData2.color} strokeWidth={3} />
                          <span style={{ fontSize: '0.6rem', fontWeight: 800, color: archData2.color }}>{archData2.label.toUpperCase()}</span>
                        </div>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                        <Calendar size={10} /> {customer.lastVisit}
                      </span>
                      <span>{customer.totalVisits} visits</span>
                    </div>

                    {/* Service tags */}
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}>
                      {customer.topServices.map((s: any) => (
                        <span key={s} className="badge badge-teal" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>{s}</span>
                      ))}
                    </div>

                    {/* Allergy warning */}
                    {customer.allergies.length > 0 && (
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 6, padding: '6px 10px',
                        background: 'rgba(231,111,111,0.06)', borderRadius: 'var(--radius-md)',
                        border: '1px solid rgba(231,111,111,0.1)',
                      }}>
                        <AlertTriangle size={12} style={{ color: 'var(--error)', flexShrink: 0 }} />
                        <span style={{ fontSize: '0.75rem', color: 'var(--error)', fontWeight: 500 }}>
                          Allergies: {customer.allergies.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Chevron */}
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <ChevronRight size={18} style={{ color: 'var(--text-muted)' }} />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
