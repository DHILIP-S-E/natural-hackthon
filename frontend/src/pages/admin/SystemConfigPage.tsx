import { motion } from 'framer-motion';
import { Settings, Sparkles, ScanFace, Clock } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';

const FEATURE_TOGGLES = [
  { key: 'soulskin_enabled', label: 'SOULSKIN Engine', description: 'AI-powered archetype-based beauty personality analysis', enabled: true, icon: Sparkles, color: 'var(--violet)' },
  { key: 'smart_mirror_enabled', label: 'AI Smart Mirror', description: 'AR-powered virtual try-on for hairstyles and makeup', enabled: true, icon: ScanFace, color: 'var(--gold)' },
];

const OPERATING_HOURS = [
  { day: 'Monday', open: '09:00', close: '21:00' },
  { day: 'Tuesday', open: '09:00', close: '21:00' },
  { day: 'Wednesday', open: '09:00', close: '21:00' },
  { day: 'Thursday', open: '09:00', close: '21:00' },
  { day: 'Friday', open: '09:00', close: '21:00' },
  { day: 'Saturday', open: '08:00', close: '22:00' },
  { day: 'Sunday', open: '10:00', close: '20:00' },
];

export default function SystemConfigPage() {
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
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-md)' }}>
          {FEATURE_TOGGLES.map((ft, i) => {
            const Icon = ft.icon;
            return (
              <motion.div key={ft.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                <TiltCard tiltIntensity={5} style={{ borderLeft: `4px solid ${ft.color}`, padding: '24px', background: '#fff' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{ width: 40, height: 40, borderRadius: 10, background: `${ft.color}12`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Icon size={20} color={ft.color} />
                      </div>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{ft.label}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{ft.description}</div>
                      </div>
                    </div>
                    {/* Toggle switch (read-only display) */}
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
              {OPERATING_HOURS.map((h, i) => (
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
