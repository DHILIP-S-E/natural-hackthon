import { motion } from 'framer-motion';
import { Shield, Check, X } from 'lucide-react';

const ROLES = ['super_admin', 'regional_manager', 'franchise_owner', 'salon_manager', 'stylist', 'customer'];

const CAPABILITIES = [
  'manage_staff',
  'view_reports',
  'run_soulskin',
  'manage_bookings',
  'view_customers',
  'manage_locations',
  'manage_config',
  'manage_rbac',
  'view_analytics',
  'manage_services',
];

const PERMISSIONS: Record<string, Set<string>> = {
  super_admin: new Set(CAPABILITIES),
  regional_manager: new Set(['manage_staff', 'view_reports', 'run_soulskin', 'manage_bookings', 'view_customers', 'manage_locations', 'view_analytics']),
  franchise_owner: new Set(['manage_staff', 'view_reports', 'run_soulskin', 'manage_bookings', 'view_customers', 'manage_locations', 'view_analytics']),
  salon_manager: new Set(['manage_staff', 'view_reports', 'run_soulskin', 'manage_bookings', 'view_customers', 'view_analytics', 'manage_services']),
  stylist: new Set(['run_soulskin', 'view_customers', 'manage_bookings']),
  customer: new Set(['manage_bookings', 'run_soulskin']),
};

const ROLE_COLORS: Record<string, string> = {
  super_admin: 'var(--phoenix)',
  regional_manager: 'var(--bloom)',
  franchise_owner: 'var(--info)',
  salon_manager: 'var(--violet)',
  stylist: 'var(--gold)',
  customer: 'var(--teal)',
};

export default function RBACPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Shield size={28} style={{ color: 'var(--phoenix)' }} />
          Roles & Permissions
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          RBAC permission matrix across {ROLES.length} roles and {CAPABILITIES.length} capabilities
        </p>
      </div>

      {/* Permission Matrix */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="card" style={{ padding: 0, overflow: 'auto' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4>Permission Matrix</h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>Read-only view of current role capabilities</p>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr>
                <th style={{ minWidth: 150, position: 'sticky', left: 0, background: 'var(--bg-card)', zIndex: 1 }}>Capability</th>
                {ROLES.map(role => (
                  <th key={role} style={{ textAlign: 'center', minWidth: 110 }}>
                    <span style={{
                      color: ROLE_COLORS[role], fontWeight: 700, fontSize: '0.7rem',
                      textTransform: 'capitalize',
                    }}>{role.replace('_', ' ')}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {CAPABILITIES.map((cap, i) => (
                <tr key={cap}>
                  <td style={{
                    padding: '12px 20px', fontWeight: 600, fontSize: '0.8rem',
                    position: 'sticky', left: 0, background: 'var(--bg-card)', zIndex: 1,
                    textTransform: 'capitalize',
                  }}>
                    {cap.replace('_', ' ')}
                  </td>
                  {ROLES.map(role => {
                    const has = PERMISSIONS[role]?.has(cap);
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
      </motion.div>
    </div>
  );
}
