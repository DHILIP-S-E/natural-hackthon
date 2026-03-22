import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore, getRoleRedirect } from '../../stores/authStore';
import api from '../../config/api';

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', password: '', city: '', preferred_language: 'en' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const update = (field: string, value: string) => setForm(f => ({ ...f, [field]: value }));

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/auth/register', form);
      const { access_token, user } = res.data.data;
      login(access_token, user);
      navigate(getRoleRedirect(user.role));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-void)', padding: 24 }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ width: '100%', maxWidth: 480 }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'linear-gradient(135deg, var(--gold), var(--gold-dim))', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--font-display)', fontSize: 20, fontWeight: 800, color: 'var(--bg-deep)', marginBottom: 16 }}>A</div>
          <h2>Create Your Account</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: 8 }}>Join AURA — your beauty intelligence awaits</p>
        </div>

        {/* Progress */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 32 }}>
          {[1, 2, 3].map(s => (
            <div key={s} style={{ flex: 1, height: 3, borderRadius: 2, background: s <= step ? 'var(--gold)' : 'var(--border-subtle)', transition: 'background 0.3s' }} />
          ))}
        </div>

        {error && <div style={{ background: 'var(--rose-glow)', border: '1px solid var(--rose)', borderRadius: 'var(--radius-md)', padding: '10px 14px', marginBottom: 16, color: 'var(--rose)', fontSize: '0.85rem' }}>{error}</div>}

        <div className="card" style={{ padding: 'var(--space-xl)' }}>
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <h4>Personal Details</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>First Name</label>
                  <input className="input" value={form.first_name} onChange={e => update('first_name', e.target.value)} placeholder="Priya" />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Last Name</label>
                  <input className="input" value={form.last_name} onChange={e => update('last_name', e.target.value)} placeholder="Sharma" />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Email</label>
                <input className="input" type="email" value={form.email} onChange={e => update('email', e.target.value)} placeholder="priya@email.com" />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Phone</label>
                <input className="input" value={form.phone} onChange={e => update('phone', e.target.value)} placeholder="+91 98765 43210" />
              </div>
              <button className="btn btn-primary" onClick={() => setStep(2)} disabled={!form.first_name || !form.email}>Continue</button>
            </div>
          )}

          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <h4>Security & Preferences</h4>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Password</label>
                <input className="input" type="password" value={form.password} onChange={e => update('password', e.target.value)} placeholder="Min 8 characters" />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>City</label>
                <input className="input" value={form.city} onChange={e => update('city', e.target.value)} placeholder="Chennai" />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Language</label>
                <select className="select" value={form.preferred_language} onChange={e => update('preferred_language', e.target.value)}>
                  <option value="en">English</option>
                  <option value="ta">தமிழ் (Tamil)</option>
                  <option value="hi">हिंदी (Hindi)</option>
                  <option value="te">తెలుగు (Telugu)</option>
                  <option value="kn">ಕನ್ನಡ (Kannada)</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <button className="btn btn-ghost" onClick={() => setStep(1)}>Back</button>
                <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => setStep(3)} disabled={!form.password}>Continue</button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16, textAlign: 'center' }}>
              <h4>Confirm & Join</h4>
              <div style={{ background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', padding: 16 }}>
                <p style={{ fontSize: '0.85rem' }}><strong>{form.first_name} {form.last_name}</strong></p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{form.email}</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{form.city || 'No city set'}</p>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                By registering, you consent to AURA's data collection for beauty intelligence services under DPDP Act 2023.
              </p>
              <div style={{ display: 'flex', gap: 12 }}>
                <button className="btn btn-ghost" onClick={() => setStep(2)}>Back</button>
                <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleSubmit} disabled={loading}>
                  {loading ? 'Creating account...' : 'Create Account'}
                </button>
              </div>
            </div>
          )}
        </div>

        <p style={{ textAlign: 'center', marginTop: 24, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--gold)' }}>Sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
