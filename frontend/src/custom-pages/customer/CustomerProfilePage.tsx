import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation } from '@tanstack/react-query';
import { User, Save, CheckCircle } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import api from '../../config/api';

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'ta', label: 'Tamil' },
  { value: 'hi', label: 'Hindi' },
  { value: 'te', label: 'Telugu' },
  { value: 'kn', label: 'Kannada' },
];

const inputStyle: React.CSSProperties = {
  padding: '10px 14px',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--border-subtle)',
  fontSize: '0.9rem',
  background: 'var(--bg-surface)',
  outline: 'none',
  width: '100%',
  fontFamily: 'var(--font-body)',
  transition: 'border-color 0.15s',
};

const labelStyle: React.CSSProperties = {
  fontWeight: 600,
  fontSize: '0.8rem',
  color: 'var(--text-muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
  marginBottom: 6,
  display: 'block',
};

export default function CustomerProfilePage() {
  const [form, setForm] = useState({
    full_name: '',
    phone: '',
    city: '',
    preferred_language: 'en',
  });
  const [saved, setSaved] = useState(false);

  const { data: userData } = useQuery({
    queryKey: ['auth-me'],
    queryFn: () => api.get('/auth/me').then(r => r.data?.data),
    placeholderData: { full_name: '', phone: '', city: '', preferred_language: 'en' },
  });

  useEffect(() => {
    if (userData) {
      setForm({
        full_name: userData.full_name || '',
        phone: userData.phone || '',
        city: userData.city || '',
        preferred_language: userData.preferred_language || 'en',
      });
    }
  }, [userData]);

  const mutation = useMutation({
    mutationFn: (data: typeof form) => api.put('/auth/me', data).then(r => r.data),
    onSuccess: () => {
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  const handleChange = (field: string, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <User size={28} style={{ color: 'var(--gold)' }} />
          My Profile
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          Manage your account settings and preferences
        </p>
      </div>

      {/* Profile Form */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <TiltCard tiltIntensity={3} style={{ padding: '32px', background: '#fff', maxWidth: 560 }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            {/* Name */}
            <div>
              <label style={labelStyle}>Full Name</label>
              <input
                type="text"
                value={form.full_name}
                onChange={e => handleChange('full_name', e.target.value)}
                style={inputStyle}
                placeholder="Enter your full name"
              />
            </div>

            {/* Phone */}
            <div>
              <label style={labelStyle}>Phone</label>
              <input
                type="tel"
                value={form.phone}
                onChange={e => handleChange('phone', e.target.value)}
                style={inputStyle}
                placeholder="+91 XXXXX XXXXX"
              />
            </div>

            {/* City */}
            <div>
              <label style={labelStyle}>City</label>
              <input
                type="text"
                value={form.city}
                onChange={e => handleChange('city', e.target.value)}
                style={inputStyle}
                placeholder="Your city"
              />
            </div>

            {/* Language */}
            <div>
              <label style={labelStyle}>Preferred Language</label>
              <select
                value={form.preferred_language}
                onChange={e => handleChange('preferred_language', e.target.value)}
                style={{ ...inputStyle, cursor: 'pointer' }}
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.value} value={lang.value}>{lang.label}</option>
                ))}
              </select>
            </div>

            {/* Save */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <button
                type="submit"
                disabled={mutation.isPending}
                style={{
                  padding: '12px 32px',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: 'var(--gold)',
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  cursor: mutation.isPending ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  opacity: mutation.isPending ? 0.7 : 1,
                  transition: 'opacity 0.15s',
                }}
              >
                <Save size={16} />
                {mutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
              {saved && (
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  style={{ color: 'var(--success)', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}
                >
                  <CheckCircle size={16} /> Saved
                </motion.span>
              )}
            </div>
          </form>
        </TiltCard>
      </motion.div>
    </div>
  );
}
