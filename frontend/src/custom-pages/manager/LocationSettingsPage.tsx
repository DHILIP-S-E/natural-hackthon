import { motion } from 'framer-motion';
import { Settings, MapPin, Phone, Users, Sparkles, ScanFace, Clock, Loader } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { TiltCard } from '../../components/ui/TiltCard';
import api from '../../config/api';

interface LocationData {
  id: string;
  name: string;
  phone: string | null;
  city: string;
  code: string | null;
  seating_capacity: number | null;
  soulskin_enabled: boolean;
  smart_mirror_enabled: boolean;
  operating_hours: Record<string, { open: string; close: string }> | null;
}

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function LocationSettingsPage() {
  const { data: profile } = useQuery<{ location_id: string }>({
    queryKey: ['staff', 'me'],
    queryFn: () => api.get('/staff/me').then(r => r.data?.data),
    staleTime: 10 * 60 * 1000,
  });

  const locationId = profile?.location_id;

  const { data: location, isLoading } = useQuery<LocationData>({
    queryKey: ['location', locationId],
    queryFn: () => api.get(`/locations/${locationId}`).then(r => r.data?.data),
    enabled: !!locationId,
    staleTime: 5 * 60 * 1000,
  });

  const { data: sysConfig } = useQuery<{
    default_operating_hours: { day: string; open: string; close: string }[];
  }>({
    queryKey: ['config', 'system'],
    queryFn: () => api.get('/config/system').then(r => r.data?.data),
    staleTime: Infinity,
  });

  const featureToggles = [
    { key: 'soulskin_enabled', label: 'SOULSKIN Engine', enabled: location?.soulskin_enabled ?? false, icon: Sparkles, color: 'var(--violet)' },
    { key: 'smart_mirror_enabled', label: 'AI Smart Mirror', enabled: location?.smart_mirror_enabled ?? false, icon: ScanFace, color: 'var(--gold)' },
  ];

  const operatingHours = DAYS.map(day => {
    const fromLocation = location?.operating_hours?.[day];
    if (fromLocation) return { day, open: fromLocation.open, close: fromLocation.close };
    const fallback = sysConfig?.default_operating_hours?.find(h => h.day === day);
    return { day, open: fallback?.open ?? '—', close: fallback?.close ?? '—' };
  });

  if (isLoading || !location) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200, color: 'var(--text-muted)', gap: 10 }}>
        <Loader size={18} />
        {isLoading ? 'Loading location settings...' : 'No location assigned to your profile.'}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Settings size={28} style={{ color: 'var(--teal)' }} />
          Location Settings
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          Configuration for {location.name}
        </p>
      </div>

      {/* Location Info Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-md)' }}>
        {[
          { label: 'Location Name', value: location.name, icon: MapPin, color: 'var(--teal)' },
          { label: 'Phone', value: location.phone ?? '—', icon: Phone, color: 'var(--info)' },
          { label: 'Capacity', value: location.seating_capacity ? `${location.seating_capacity} chairs` : '—', icon: Users, color: 'var(--success)' },
        ].map((item, i) => {
          const Icon = item.icon;
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
              <TiltCard tiltIntensity={8} style={{ borderLeft: `4px solid ${item.color}`, padding: '24px', background: '#fff' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <Icon size={16} color={item.color} />
                  <span style={{ fontWeight: 600, fontSize: '0.75rem', letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>{item.label}</span>
                </div>
                <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>{item.value}</span>
              </TiltCard>
            </motion.div>
          );
        })}
      </div>

      {/* Feature Toggles */}
      <div>
        <h3 style={{ fontSize: '1rem', marginBottom: 'var(--space-md)' }}>Feature Toggles</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-md)' }}>
          {featureToggles.map((ft, i) => {
            const Icon = ft.icon;
            return (
              <motion.div key={ft.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 + i * 0.08 }}>
                <TiltCard tiltIntensity={5} style={{ borderLeft: `4px solid ${ft.color}`, padding: '24px', background: '#fff' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{ width: 36, height: 36, borderRadius: 8, background: `${ft.color}12`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Icon size={18} color={ft.color} />
                      </div>
                      <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>{ft.label}</span>
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
      </div>

      {/* Operating Hours */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Clock size={18} /> Operating Hours</h4>
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
