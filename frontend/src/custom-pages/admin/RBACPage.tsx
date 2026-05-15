import { motion } from 'framer-motion';
import { Shield, Check, X } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import api from '../../config/api';

const ROLE_COLORS: Record<string, string> = {
  super_admin:       'var(--phoenix)',
  regional_manager:  'var(--bloom)',
  franchise_owner:   'var(--info)',
  salon_manager:     'var(--violet)',
  stylist:           'var(--gold)',
  customer:          'var(--teal)',
};

interface RbacMatrix {
  roles: string[];
  capabilities: string[];
  permissions: Record<string, string[]>;
}

export default function RBACPage() {
  const { data, isLoading } = useQuery<RbacMatrix>({
    queryKey: ['config', 'rbac-matrix'],
    queryFn: () => api.get('/config/rbac-matrix').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const roles = data?.roles ?? [];
  const capabilities = data?.capabilities ?? [];
  const permissions = data?.permissions ?? {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Shield size={28} style={{ color: 'var(--phoenix)' }} />
          Roles & Permissions
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          RBAC permission matrix across {roles.length} roles and {capabilities.length} capabilities
        </p>
      </div>

      {/* Permission Matrix */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="card" style={{ padding: 0, overflow: 'auto' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4>Permission Matrix</h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>Read-only view of current role capabilities</p>
        </div>

        {isLoading ? (
          <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Loading permissions...
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table>
              <thead>
                <tr>
                  <th style={{ minWidth: 150, position: 'sticky', left: 0, background: 'var(--bg-card)', zIndex: 1 }}>Capability</th>
                  {roles.map(role => (
                    <th key={role} style={{ textAlign: 'center', minWidth: 110 }}>
                      <span style={{
                        color: ROLE_COLORS[role] ?? 'var(--text-secondary)',
                        fontWeight: 700,
                        fontSize: '0.7rem',
                        textTransform: 'capitalize',
                      }}>{role.replace(/_/g, ' ')}</span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {capabilities.map(cap => (
                  <tr key={cap}>
                    <td style={{
                      padding: '12px 20px', fontWeight: 600, fontSize: '0.8rem',
                      position: 'sticky', left: 0, background: 'var(--bg-card)', zIndex: 1,
                      textTransform: 'capitalize',
                    }}>
                      {cap.replace(/_/g, ' ')}
                    </td>
                    {roles.map(role => {
                      const has = permissions[role]?.includes(cap);
                      return (
                        <td key={role} style={{ textAlign: 'center', padding: '12px' }}>
                          {has ? (
                            <div style={{
                              width: 24, height: 24, borderRadius: 6,
                              background: 'rgba(82,183,136,0.1)', display: 'inline-flex',
                              alignItems: 'center', justifyContent: 'center',
                            }}>
                              <Check size={14} style={{ color: 'var(--success)' }} />
                            </div>
                          ) : (
                            <div style={{
                              width: 24, height: 24, borderRadius: 6,
                              background: 'rgba(231,111,111,0.06)', display: 'inline-flex',
                              alignItems: 'center', justifyContent: 'center',
                            }}>
                              <X size={14} style={{ color: 'var(--text-faint)' }} />
                            </div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}
