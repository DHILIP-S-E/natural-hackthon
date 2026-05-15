import { motion } from 'framer-motion';
import { Settings, Sparkles, ScanFace, Clock } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { TiltCard } from '../../components/ui/TiltCard';
import api from '../../config/api';

const FEATURE_ICONS: Record<string, typeof Sparkles> = {
  soulskin_enabled: Sparkles,
  smart_mirror_enabled: ScanFace,
};

const FEATURE_COLORS: Record<string, string> = {
  soulskin_enabled: 'var(--violet)',
  smart_mirror_enabled: 'var(--gold)',
};

interface FeatureToggle {
  key: string;
  label: string;
  description: string;
  enabled: boolean;
}

interface SystemConfig {
  feature_toggles: FeatureToggle[];
  default_operating_hours: { day: string; open: string; close: string }[];
}

export default function SystemConfigPage() {
  const { data, isLoading } = useQuery<SystemConfig>({
    queryKey: ['config', 'system'],
    queryFn: () => api.get('/config/system').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const featureToggles = data?.feature_toggles ?? [];
  const operatingHours = data?.default_operating_hours ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Settings size={28} style={{ color: 'var(--gold)' }} />
          System Configuration
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          Platform-wide feature toggles and settings
        </p>
      </div>

      {/* Feature Toggles */}
      <div>
        <h3 style={{ fontSize: '1rem', marginBottom: 'var(--space-md)', display: 'flex', alignItems: 'center', gap: 8 }}>
          Feature Toggles
        </h3>
        {isLoading ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Loading...</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-md)' }}>
            {featureToggles.map((ft, i) => {
              const Icon = FEATURE_ICONS[ft.key] ?? Sparkles;
              const color = FEATURE_COLORS[ft.key] ?? 'var(--gold)';
              return (
                <motion.div key={ft.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                  <TiltCard tiltIntensity={5} style={{ borderLeft: `4px solid ${color}`, padding: '24px', background: '#fff' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{ width: 40, height: 40, borderRadius: 10, background: `${color}12`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Icon size={20} color={color} />
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{ft.label}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{ft.description}</div>
                        </div>
                      </div>
                      <div style={{
                        width: 44, height: 24, borderRadius: 12,
                        background: ft.enabled ? 'var(--success)' : 'var(--border-medium)',
                        position: 'relative', cursor: 'not-allowed', flexShrink: 0,
                      }}>
                        <div style={{
                          width: 18, height: 18, borderRadius: '50%', background: '#fff',
                          position: 'absolute', top: 3,
                          left: ft.enabled ? 23 : 3,
                          transition: 'left 0.2s',
                          boxShadow: 'var(--shadow-sm)',
                        }} />
                      </div>
                    </div>
                  </TiltCard>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>

      {/* Operating Hours */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Clock size={18} /> Default Operating Hours</h4>
        </div>
        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table>
            <thead>
              <tr><th>Day</th><th>Open</th><th>Close</th></tr>
            </thead>
            <tbody>
              {operatingHours.map((h, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, fontSize: '0.9rem', padding: '12px 20px' }}>{h.day}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 500 }}>{h.open}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 500 }}>{h.close}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
