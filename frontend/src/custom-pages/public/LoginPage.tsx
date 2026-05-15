import { useState, useEffect } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GoogleLogin } from '@react-oauth/google';
import { useAuthStore, getRoleRedirect } from '../../stores/authStore';
import api from '../../config/api';
import { Eye, EyeOff, Sparkles } from 'lucide-react';

interface DemoAccount {
  email: string;
  label: string;
  icon: string;
  color: string;
}

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [demoAccounts, setDemoAccounts] = useState<DemoAccount[]>([]);
  const [demoPassword, setDemoPassword] = useState('');

  const { login, isAuthenticated, user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/auth/demo-credentials').then(res => {
      if (res.data?.success) {
        setDemoAccounts(res.data.data.accounts);
        setDemoPassword(res.data.data.password);
      }
    }).catch(console.error);
  }, []);

  // Already logged in — go to the right dashboard
  if (isAuthenticated && user) {
    return <Navigate to={getRoleRedirect(user.role)} replace />;
  }

  const doLogin = async (emailVal: string, passwordVal: string) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/auth/login', { email: emailVal, password: passwordVal });
      const { access_token, user: u } = res.data?.data ?? {};
      if (!access_token || !u) {
        setError('Invalid response from server');
        return;
      }
      login(access_token, u);
      navigate(getRoleRedirect(u.role));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await doLogin(email, password);
  };

  const handleDemo = async (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    await doLogin(demoEmail, demoPassword);
  };

  const handleGoogleSuccess = async (credentialResponse: { credential?: string }) => {
    if (!credentialResponse.credential) return;
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/auth/google', { id_token: credentialResponse.credential });
      const { access_token, user: u } = res.data?.data ?? {};
      if (!access_token || !u) { setError('Invalid response from server'); return; }
      login(access_token, u);
      navigate(getRoleRedirect(u.role));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Google sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--bg-void)' }}>
      {/* Left brand panel */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
        padding: 48, background: 'radial-gradient(ellipse 80% 60% at 30% 50%, rgba(155,127,212,0.06) 0%, transparent 70%)',
        borderRight: '1px solid var(--border-subtle)',
      }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
          style={{ textAlign: 'center', maxWidth: 400 }}>
          <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'linear-gradient(135deg, var(--gold), var(--gold-dim))', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px', fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 800, color: 'var(--bg-deep)' }}>A</div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', color: 'var(--gold)', marginBottom: 16 }}>AURA</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', lineHeight: 1.7 }}>
            Unified Salon Intelligence Platform
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 12, fontStyle: 'italic' }}>
            "Every salon visit. Every soul. Understood."
          </p>
        </motion.div>
      </div>

      {/* Right form panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: 48 }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
          style={{ width: '100%', maxWidth: 400 }}>
          <h2 style={{ marginBottom: 8 }}>Welcome back</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>Sign in to your AURA account</p>

          {error && (
            <div style={{ background: 'var(--rose-glow)', border: '1px solid var(--rose)', borderRadius: 'var(--radius-md)', padding: '10px 14px', marginBottom: 16, color: 'var(--rose)', fontSize: '0.85rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 6 }}>Email</label>
              <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="your@email.com" required />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 6 }}>Password</label>
              <div style={{ position: 'relative' }}>
                <input className="input" type={showPassword ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required style={{ paddingRight: 40 }} />
                <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Google Sign-In */}
          <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%' }}>
              <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>or continue with</span>
              <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
            </div>
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError('Google sign-in failed')}
              theme="filled_black"
              shape="rectangular"
              width="400"
            />
          </div>

          <div style={{ textAlign: 'center', marginTop: 20 }}>
            <Link to="/register" style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Don't have an account? <span style={{ color: 'var(--gold)' }}>Sign up</span></Link>
          </div>

          {/* Quick Demo Login — authenticates via /auth/login against DB-seeded users */}
          <div style={{ marginTop: 40, borderTop: '1px solid var(--border-subtle)', paddingTop: 24 }}>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginBottom: 12 }}>
              <Sparkles size={12} style={{ display: 'inline', verticalAlign: 'middle' }} /> Quick Demo Login
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
              {DEMO_ACCOUNTS.map(d => (
                <button key={d.email} className="btn btn-ghost btn-sm" disabled={loading}
                  onClick={() => handleDemo(d.email)}
                  style={{ fontSize: '0.75rem' }}>
                  {loading ? '...' : d.label}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
