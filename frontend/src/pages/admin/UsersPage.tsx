import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Users, Search, Shield } from 'lucide-react';
import api from '../../config/api';

const ROLES = ['All', 'customer', 'stylist', 'salon_manager', 'franchise_owner', 'regional_manager', 'super_admin'];

const ROLE_COLORS: Record<string, { color: string; bg: string }> = {
  customer: { color: 'var(--teal)', bg: 'rgba(42,157,143,0.1)' },
  stylist: { color: 'var(--gold)', bg: 'rgba(244,79,154,0.1)' },
  salon_manager: { color: 'var(--violet)', bg: 'rgba(155,127,212,0.1)' },
  franchise_owner: { color: 'var(--info)', bg: 'rgba(74,159,212,0.1)' },
  regional_manager: { color: 'var(--bloom)', bg: 'rgba(232,168,124,0.1)' },
  super_admin: { color: 'var(--phoenix)', bg: 'rgba(232,97,26,0.1)' },
};

const STATUS_STYLES: Record<string, { color: string; bg: string }> = {
  active: { color: 'var(--success)', bg: 'rgba(82,183,136,0.1)' },
  inactive: { color: 'var(--error)', bg: 'rgba(231,111,111,0.1)' },
};

export default function UsersPage() {
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => api.get('/auth/users').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.users || d?.items || [];
    }),
  });

  const list = Array.isArray(users) ? users : [];
  const filtered = list.filter((u: any) => {
    const matchSearch = (u.full_name ?? '').toLowerCase().includes(search.toLowerCase()) ||
      (u.email ?? '').toLowerCase().includes(search.toLowerCase());
    const matchRole = roleFilter === 'All' || u.role === roleFilter;
    return matchSearch && matchRole;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Shield size={28} style={{ color: 'var(--gold)' }} />
          User Management
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          {list.length} users across all roles
        </p>
      </div>

      {/* Search + Filter */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        <div style={{ position: 'relative', maxWidth: 320 }}>
          <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              padding: '10px 12px 10px 32px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)',
              fontSize: '0.85rem', background: 'var(--bg-surface)', outline: 'none', width: '100%',
            }}
          />
        </div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {ROLES.map(role => (
            <button
              key={role}
              onClick={() => setRoleFilter(role)}
              style={{
                padding: '6px 14px', borderRadius: 'var(--radius-full)',
                border: `1px solid ${roleFilter === role ? 'var(--gold)' : 'var(--border-subtle)'}`,
                background: roleFilter === role ? 'rgba(244,79,154,0.08)' : 'var(--bg-surface)',
                color: roleFilter === role ? 'var(--gold)' : 'var(--text-secondary)',
                fontWeight: 600, fontSize: '0.75rem', cursor: 'pointer',
                textTransform: 'capitalize', transition: 'all 0.15s',
              }}
            >
              {role === 'All' ? 'All' : role.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Users size={18} /> Users</h4>
          <span className="badge badge-teal">{filtered.length} results</span>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr>
            </thead>
            <tbody>
              {isLoading && !users ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i}>
                    <td style={{ padding: '14px 20px' }}><div style={{ width: 120, height: 16, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} /></td>
                    <td><div style={{ width: 160, height: 14, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} /></td>
                    <td><div style={{ width: 80, height: 22, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} /></td>
                    <td><div style={{ width: 60, height: 22, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} /></td>
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No users found.</td>
                </tr>
              ) : filtered.map((user, i) => {
                const rc = ROLE_COLORS[user.role] || ROLE_COLORS.customer;
                const sc = STATUS_STYLES[user.status] || STATUS_STYLES.active;
                return (
                  <tr key={user.id || i}>
                    <td style={{ padding: '14px 20px', fontWeight: 600, fontSize: '0.9rem' }}>{user.full_name}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{user.email}</td>
                    <td>
                      <span style={{
                        color: rc.color, background: rc.bg,
                        fontWeight: 700, fontSize: '0.65rem',
                        padding: '4px 10px', borderRadius: 5,
                        letterSpacing: '0.04em', textTransform: 'capitalize',
                      }}>{(user.role ?? '').replace('_', ' ')}</span>
                    </td>
                    <td>
                      <span style={{
                        color: sc.color, background: sc.bg,
                        fontWeight: 700, fontSize: '0.65rem',
                        padding: '4px 10px', borderRadius: 5,
                        letterSpacing: '0.05em', textTransform: 'uppercase',
                      }}>{user.status}</span>
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
