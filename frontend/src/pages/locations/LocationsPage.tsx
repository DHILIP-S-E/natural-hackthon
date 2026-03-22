import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Map, DollarSign, Star, Users, Building, Search, ArrowUpRight } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import { useNavigate } from 'react-router-dom';
import api from '../../config/api';

interface LocationsPageProps {
  scope: 'franchise' | 'regional' | 'admin';
}

interface Location {
  id: string;
  name: string;
  city: string;
  code: string;
  revenue: number;
  quality_score: number;
  bookings_count: number;
  status: string;
}

const SCOPE_LABELS: Record<string, string> = {
  franchise: 'Franchise',
  regional: 'Regional',
  admin: 'Network',
};

const STATUS_STYLES: Record<string, { color: string; bg: string }> = {
  active: { color: 'var(--success)', bg: 'rgba(82,183,136,0.1)' },
  maintenance: { color: 'var(--warning)', bg: 'rgba(244,162,97,0.1)' },
  inactive: { color: 'var(--error)', bg: 'rgba(231,111,111,0.1)' },
};

export default function LocationsPage({ scope }: LocationsPageProps) {
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const { data: locations = [], isLoading } = useQuery<Location[]>({
    queryKey: ['locations'],
    queryFn: () => api.get('/locations').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.locations || d?.items || [];
    }),
  });

  const list = Array.isArray(locations) ? locations : [];
  const filtered = list.filter(l =>
    (l.name ?? '').toLowerCase().includes(search.toLowerCase()) ||
    (l.city ?? '').toLowerCase().includes(search.toLowerCase()) ||
    (l.code ?? '').toLowerCase().includes(search.toLowerCase())
  );

  const totalRevenue = list.reduce((s, l) => s + (Number(l.revenue) || 0), 0);
  const avgQuality = list.length > 0 ? (list.reduce((s, l) => s + (Number(l.quality_score) || 0), 0) / list.length).toFixed(1) : '0';
  const totalStaff = list.length * 4; // estimated

  const kpis = [
    { label: 'Total Locations', value: list.length.toString(), icon: Building, color: 'var(--teal)' },
    { label: 'Total Revenue', value: `\u20B9${(totalRevenue / 100000).toFixed(1)}L`, icon: DollarSign, color: 'var(--gold)' },
    { label: 'Avg Quality', value: avgQuality, icon: Star, color: 'var(--violet)' },
    { label: 'Total Staff', value: totalStaff.toString(), icon: Users, color: 'var(--success)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Map size={28} style={{ color: 'var(--teal)' }} />
          {SCOPE_LABELS[scope]} Locations
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          {SCOPE_LABELS[scope]} overview across {list.length} locations
        </p>
      </div>

      {/* KPI Cards */}
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

      {/* Search + Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Building size={18} /> All Locations</h4>
          <div style={{ position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search locations..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{
                padding: '8px 12px 8px 30px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)',
                fontSize: '0.8rem', background: 'var(--bg-surface)', outline: 'none', width: 220,
              }}
            />
          </div>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>City</th>
                <th>Code</th>
                <th>Revenue</th>
                <th>Quality</th>
                <th>Bookings</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>Loading locations...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>No locations found</td></tr>
              ) : filtered.map((loc, i) => {
                const st = STATUS_STYLES[loc.status] || STATUS_STYLES.active;
                return (
                  <tr key={loc.id || i} style={{ cursor: 'pointer' }} onClick={() => navigate(`/${scope}/locations/${loc.id}`)}>
                    <td style={{ padding: '14px 20px' }}>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 6 }}>
                        {loc.name}
                        <ArrowUpRight size={12} style={{ color: 'var(--text-muted)' }} />
                      </div>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{loc.city}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 500 }}>{loc.code}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--gold)' }}>{`\u20B9${((Number(loc.revenue) || 0) / 100000).toFixed(1)}L`}</td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
                        <Star size={12} style={{ color: 'var(--gold)' }} />
                        {loc.quality_score ?? '-'}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{loc.bookings_count}</td>
                    <td>
                      <span style={{
                        color: st.color, background: st.bg,
                        fontWeight: 700, fontSize: '0.65rem',
                        padding: '4px 10px', borderRadius: 5,
                        letterSpacing: '0.05em', textTransform: 'uppercase',
                      }}>{loc.status}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
