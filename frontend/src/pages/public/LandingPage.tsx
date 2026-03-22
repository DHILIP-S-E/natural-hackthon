import { useRef, useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, useInView, useMotionValue, useSpring } from 'framer-motion';
import { Brain, TrendingUp, Eye, Heart, Zap, Palette, Users, BarChart3, ArrowRight, Shield, Wifi, Sparkles } from 'lucide-react';

/* ────────────────────────────────────────────────
   DATA
─────────────────────────────────────────────────*/
const STATS = [
  { value: '750+', label: 'Salon Locations' },
  { value: '8', label: 'AI Modules' },
  { value: '6', label: 'User Roles' },
  { value: '∞', label: 'Possibilities' },
];

const INTELLIGENCE_LAYERS = [
  { icon: Eye, title: 'Physical', label: 'Reads the body', desc: 'Computer vision · Skin & hair diagnostics · Real-time biometric analysis.', accent: '#f44f9a' },
  { icon: Heart, title: 'Emotional', label: 'Reads the soul', desc: 'Mood detection · Archetype matching · Emotion-to-beauty mapping.', accent: '#9B7FD4' },
  { icon: TrendingUp, title: 'Predictive', label: 'Reads the future', desc: 'Trend forecasting · Demand planning · Attrition intelligence.', accent: '#2A9D8F' },
];

const MODULES = [
  { name: 'Beauty Passport', icon: Eye, desc: 'Digital beauty identity, AI diagnostics, lifelong profile.' },
  { name: 'SOULSKIN Engine', icon: Heart, desc: 'Emotion-to-beauty, soul reading, sensory design.' },
  { name: 'AI Smart Mirror', icon: Palette, desc: 'AR try-on, virtual hairstyles, makeup simulation.' },
  { name: 'Digital Beauty Twin', icon: Brain, desc: '3D face model, future skin projection.' },
  { name: 'AI Stylist Assistant', icon: Zap, desc: 'Real-time SOP guidance, AI co-pilot.' },
  { name: 'Trend Intelligence', icon: TrendingUp, desc: 'Social listening, demand forecasting.' },
  { name: 'Staff Intelligence', icon: Users, desc: 'Skill mapping, training ROI, attrition prediction.' },
  { name: 'Salon BI Dashboard', icon: BarChart3, desc: 'Revenue, quality, retention, benchmarking.' },
];

const ARCHETYPES = [
  { name: 'Phoenix', element: 'Fire', color: '#E8611A' },
  { name: 'River', element: 'Water', color: '#4A9FD4' },
  { name: 'Moon', element: 'Light', color: '#9B7FD4' },
  { name: 'Bloom', element: 'Earth', color: '#E8A87C' },
  { name: 'Storm', element: 'Air', color: '#6B8FA6' },
];

/* ────────────────────────────────────────────────
   SUBCOMPONENTS
─────────────────────────────────────────────────*/
function StatCounter({ value, label, delay = 0 }: { value: string; label: string; delay?: number }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  return (
    <motion.div ref={ref} initial={{ opacity: 0, y: 24 }} animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      style={{ textAlign: 'center', position: 'relative' }}>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(2.5rem, 4vw, 3.5rem)', fontWeight: 700, color: '#1A1A24', letterSpacing: '-0.02em', lineHeight: 1 }}>
        {value}
      </div>
      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8, textTransform: 'uppercase', letterSpacing: '0.12em', fontWeight: 500 }}>
        {label}
      </div>
    </motion.div>
  );
}

function AuraLogo() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
        {/* Outer ring */}
        <circle cx="18" cy="18" r="17" stroke="#f44f9a" strokeWidth="1.5" />
        {/* Inner diamond */}
        <path d="M18 5 L31 18 L18 31 L5 18 Z" stroke="#f44f9a" strokeWidth="1.5" fill="none" />
        {/* Center dot */}
        <circle cx="18" cy="18" r="3" fill="#f44f9a" />
        {/* Small intersect marks */}
        <circle cx="18" cy="5" r="1.5" fill="#f44f9a" />
        <circle cx="31" cy="18" r="1.5" fill="#f44f9a" />
        <circle cx="18" cy="31" r="1.5" fill="#f44f9a" />
        <circle cx="5" cy="18" r="1.5" fill="#f44f9a" />
      </svg>
      <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', fontWeight: 700, letterSpacing: '0.1em', color: '#1A1A24' }}>
        AURA
      </span>
    </div>
  );
}

/* ────────────────────────────────────────────────
   MAGNETIC BUTTON EFFECT (subtle premium micro-interaction)
─────────────────────────────────────────────────*/
function MagneticBtn({ children, to, href, ghost = false }: { children: React.ReactNode; to?: string; href?: string; ghost?: boolean }) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const xs = useSpring(x, { stiffness: 300, damping: 25 });
  const ys = useSpring(y, { stiffness: 300, damping: 25 });

  const onMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    x.set(((e.clientX - r.left) / r.width - 0.5) * 14);
    y.set(((e.clientY - r.top) / r.height - 0.5) * 14);
  };
  const onLeave = () => { x.set(0); y.set(0); };

  const style: React.CSSProperties = ghost
    ? { display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 28px', border: '1px solid var(--border-medium)', borderRadius: 'var(--radius-full)', fontFamily: 'var(--font-body)', fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer', background: 'transparent', color: 'var(--text-secondary)', textDecoration: 'none', letterSpacing: '0.02em', transition: 'all 0.2s', whiteSpace: 'nowrap' }
    : { display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 28px', border: 'none', borderRadius: 'var(--radius-full)', fontFamily: 'var(--font-body)', fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer', background: '#f44f9a', color: '#fff', textDecoration: 'none', letterSpacing: '0.04em', boxShadow: '0 4px 24px rgba(244,79,154,0.3)', whiteSpace: 'nowrap' };

  const inner = (
    <motion.div onMouseMove={onMove} onMouseLeave={onLeave} style={{ x: xs, y: ys, display: 'inline-flex' }}>
      {to ? <Link to={to} style={style}>{children}</Link>
        : href ? <a href={href} style={style}>{children}</a>
        : <span style={style}>{children}</span>}
    </motion.div>
  );
  return inner;
}

/* ────────────────────────────────────────────────
   MAIN PAGE
─────────────────────────────────────────────────*/
export default function LandingPage() {
  const [taglineIndex, setTaglineIndex] = useState(0);
  const taglines = [
    { line1: 'Every Salon Visit.', line2: 'Every Soul, Understood.' },
    { line1: 'Where AI Meets', line2: 'the Art of Beauty.' },
    { line1: 'The World\'s First', line2: 'Emotion-to-Beauty System.' },
  ];

  useEffect(() => {
    const t = setInterval(() => setTaglineIndex(i => (i + 1) % taglines.length), 5000);
    return () => clearInterval(t);
  }, []);

  // Cursor follow orb (purely CSS-driven, ultra-subtle)
  const cursorX = useMotionValue(-200);
  const cursorY = useMotionValue(-200);
  const cx = useSpring(cursorX, { stiffness: 80, damping: 30 });
  const cy = useSpring(cursorY, { stiffness: 80, damping: 30 });
  const trackMouse = useCallback((e: MouseEvent) => { cursorX.set(e.clientX); cursorY.set(e.clientY); }, []);
  useEffect(() => { window.addEventListener('mousemove', trackMouse); return () => window.removeEventListener('mousemove', trackMouse); }, []);

  return (
    <div style={{ background: '#FFFFFF', minHeight: '100vh', color: 'var(--text-primary)', position: 'relative', overflowX: 'hidden' }}>

      {/* Cursor orb - professional, not distracting */}
      <motion.div style={{ left: cx, top: cy, x: '-50%', y: '-50%', position: 'fixed', zIndex: 0, pointerEvents: 'none', width: 500, height: 500, borderRadius: '50%', background: 'radial-gradient(circle, rgba(244,79,154,0.04) 0%, transparent 70%)', filter: 'blur(20px)' }} />

      {/* ── NAV ── */}
      <motion.nav
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'rgba(255,255,255,0.88)', backdropFilter: 'blur(16px)', borderBottom: '1px solid rgba(0,0,0,0.06)', padding: '0 clamp(24px, 5vw, 60px)', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <AuraLogo />
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <Link to="/login" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500, padding: '8px 16px', borderRadius: 'var(--radius-full)', transition: 'all 0.2s' }}>
            Sign In
          </Link>
          <MagneticBtn to="/register">Get Started <ArrowRight size={15} /></MagneticBtn>
        </div>
      </motion.nav>

      {/* ── HERO ── */}
      <section style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 'clamp(100px, 15vh, 160px) clamp(24px, 6vw, 80px) 80px', position: 'relative', zIndex: 1 }}>
        {/* Subtle patterned top decoration */}
        <div style={{ position: 'absolute', top: 80, left: '50%', transform: 'translateX(-50%)', width: 600, height: 600, background: 'radial-gradient(ellipse 60% 50% at 50% 50%, rgba(244,79,154,0.07) 0%, transparent 70%)', borderRadius: '50%', pointerEvents: 'none' }} />

        {/* Eyebrow */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.15 }}
          style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(244,79,154,0.06)', border: '1px solid rgba(244,79,154,0.15)', borderRadius: 'var(--radius-full)', padding: '6px 16px', marginBottom: 32 }}>
          <Sparkles size={12} color="#f44f9a" />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f44f9a', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Naturals BeautyTech 2026</span>
        </motion.div>

        {/* Animated tagline */}
        <div style={{ overflow: 'hidden', marginBottom: 28 }}>
          <motion.h1
            key={taglineIndex}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(2.6rem, 6vw, 5rem)', fontWeight: 700, lineHeight: 1.08, color: '#0F0F1A', letterSpacing: '-0.02em', maxWidth: 760 }}>
            {taglines[taglineIndex].line1}<br />
            <span style={{ color: '#f44f9a' }}>{taglines[taglineIndex].line2}</span>
          </motion.h1>
        </div>

        <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.3 }}
          style={{ fontSize: 'clamp(1rem, 2vw, 1.18rem)', color: 'var(--text-secondary)', maxWidth: 560, lineHeight: 1.75, marginBottom: 44 }}>
          AURA unifies 750+ Naturals salons under one AI platform — reading bodies, souls, and futures to deliver beauty that truly resonates.
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.45 }}
          style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
          <MagneticBtn href="#modules">Explore Platform <ArrowRight size={15} /></MagneticBtn>
          <MagneticBtn to="/login" ghost>Sign In</MagneticBtn>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div animate={{ y: [0, 8, 0] }} transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          style={{ position: 'absolute', bottom: 36, left: '50%', transform: 'translateX(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, opacity: 0.35 }}>
          <div style={{ width: 1, height: 48, background: 'linear-gradient(to bottom, transparent, #0F0F1A)' }} />
          <div style={{ fontSize: '0.65rem', letterSpacing: '0.15em', color: '#0F0F1A', textTransform: 'uppercase' }}>Scroll</div>
        </motion.div>
      </section>

      {/* ── STATS BAR ── */}
      <section style={{ borderTop: '1px solid rgba(0,0,0,0.07)', borderBottom: '1px solid rgba(0,0,0,0.07)', padding: '60px clamp(24px,6vw,80px)', position: 'relative', zIndex: 1, background: '#F9F9FB' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 32 }}>
          {STATS.map((s, i) => <StatCounter key={i} {...s} delay={i * 0.1} />)}
        </div>
      </section>

      {/* ── THREE INTELLIGENCE LAYERS ── */}
      <section style={{ padding: 'clamp(80px,10vw,120px) clamp(24px,6vw,80px)', maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 1 }}>
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ marginBottom: 56, textAlign: 'center' }}>
          <p style={{ fontSize: '0.75rem', letterSpacing: '0.14em', textTransform: 'uppercase', color: '#f44f9a', fontWeight: 600, marginBottom: 12 }}>The AURA Framework</p>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(1.8rem,3.5vw,2.8rem)', fontWeight: 700, color: '#0F0F1A', letterSpacing: '-0.02em' }}>Three Layers of Intelligence</h2>
        </motion.div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px,1fr))', gap: 2, borderRadius: 'var(--radius-xl)', overflow: 'hidden', border: '1px solid rgba(0,0,0,0.08)' }}>
          {INTELLIGENCE_LAYERS.map((layer, i) => {
            const Icon = layer.icon;
            return (
              <motion.div key={i} initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.12, ease: [0.22,1,0.36,1], duration: 0.6 }}
                style={{ padding: 'clamp(32px,4vw,52px) clamp(28px,3vw,44px)', background: '#fff', borderRight: i < 2 ? '1px solid rgba(0,0,0,0.06)' : 'none', position: 'relative', overflow: 'hidden', cursor: 'default', transition: 'background 0.3s' }}
                whileHover={{ background: `${layer.accent}05` }}>
                {/* Accent line top */}
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: layer.accent, opacity: 0.8, borderRadius: '0 0 4px 4px' }} />
                <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)', background: `${layer.accent}12`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>
                  <Icon size={22} color={layer.accent} />
                </div>
                <p style={{ fontSize: '0.7rem', letterSpacing: '0.12em', textTransform: 'uppercase', color: layer.accent, fontWeight: 600, marginBottom: 8 }}>{layer.label}</p>
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 700, color: '#0F0F1A', marginBottom: 12 }}>{layer.title}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>{layer.desc}</p>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* ── SOULSKIN SECTION ── */}
      <section style={{ background: '#0F0F1A', padding: 'clamp(80px,10vw,120px) clamp(24px,6vw,80px)', position: 'relative', overflow: 'hidden' }}>
        {/* Background orb */}
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: 700, height: 700, borderRadius: '50%', background: 'radial-gradient(circle, rgba(155,127,212,0.12) 0%, transparent 65%)', pointerEvents: 'none' }} />
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, alignItems: 'center' }}>
          <motion.div initial={{ opacity: 0, x: -32 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.8, ease: [0.22,1,0.36,1] }}>
            <p style={{ fontSize: '0.7rem', letterSpacing: '0.14em', color: '#9B7FD4', textTransform: 'uppercase', fontWeight: 600, marginBottom: 16 }}>Emotional Intelligence</p>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(2rem,4vw,3rem)', fontWeight: 700, color: '#F0EEF8', lineHeight: 1.1, letterSpacing: '-0.02em', marginBottom: 20 }}>
              Introducing<br /><span style={{ color: '#9B7FD4' }}>SOULSKIN</span>
            </h2>
            <p style={{ color: '#9B99B0', lineHeight: 1.8, fontStyle: 'italic', fontSize: '1rem', borderLeft: '2px solid #9B7FD433', paddingLeft: 16, marginBottom: 36 }}>
              "People don't visit salons to change their hair. They visit when something in their life is changing."
            </p>
            <Link to="/register" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: '#9B7FD4', color: '#fff', padding: '13px 26px', borderRadius: 'var(--radius-full)', fontSize: '0.875rem', fontWeight: 600, textDecoration: 'none', letterSpacing: '0.03em', boxShadow: '0 4px 24px rgba(155,127,212,0.3)' }}>
              Discover SOULSKIN <ArrowRight size={15} />
            </Link>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 32 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.8, ease: [0.22,1,0.36,1] }}>
            {/* The 3 questions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 32 }}>
              {['The song that describes your life right now...', 'The colour that matches your mood today...', 'Describe how you want to feel when you leave...'].map((q, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 + i * 0.1 }}
                  style={{ background: 'rgba(155,127,212,0.07)', border: '1px solid rgba(155,127,212,0.15)', borderRadius: 'var(--radius-lg)', padding: '16px 20px', color: '#9B99B0', fontSize: '0.9rem', fontStyle: 'italic', lineHeight: 1.6 }}>
                  {q}
                </motion.div>
              ))}
            </div>
            {/* Archetype pills */}
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {ARCHETYPES.map((a, i) => (
                <motion.div key={i} initial={{ opacity: 0, scale: 0.9 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: 0.3 + i * 0.07 }}
                  style={{ background: `${a.color}18`, border: `1px solid ${a.color}30`, borderRadius: 'var(--radius-full)', padding: '6px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: a.color }}>{a.name}</span>
                  <span style={{ fontSize: '0.65rem', color: '#5C5A70', letterSpacing: '0.06em' }}>{a.element}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── 8 MODULES GRID ── */}
      <section id="modules" style={{ padding: 'clamp(80px,10vw,120px) clamp(24px,6vw,80px)', maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 1 }}>
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ marginBottom: 56, textAlign: 'center' }}>
          <p style={{ fontSize: '0.75rem', letterSpacing: '0.14em', textTransform: 'uppercase', color: '#f44f9a', fontWeight: 600, marginBottom: 12 }}>Platform Overview</p>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(1.8rem,3.5vw,2.8rem)', fontWeight: 700, color: '#0F0F1A', letterSpacing: '-0.02em' }}>8 Intelligence Modules</h2>
        </motion.div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px,1fr))', gap: 16 }}>
          {MODULES.map((m, i) => {
            const Icon = m.icon;
            return (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.05, ease: [0.22,1,0.36,1], duration: 0.5 }}
                whileHover={{ y: -4, boxShadow: '0 12px 36px rgba(0,0,0,0.09)', borderColor: 'rgba(244,79,154,0.25)' }}
                style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.08)', borderRadius: 'var(--radius-lg)', padding: '28px 24px', display: 'flex', flexDirection: 'column', gap: 14, transition: 'box-shadow 0.3s, border-color 0.3s', cursor: 'default' }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(244,79,154,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon size={18} color="#f44f9a" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#0F0F1A', marginBottom: 6 }}>{m.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.65 }}>{m.desc}</div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* ── TECH / CREDIBILITY ── */}
      <section style={{ borderTop: '1px solid rgba(0,0,0,0.07)', background: '#F9F9FB', padding: '48px clamp(24px,6vw,80px)' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 24 }}>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'center' }}>
            {[{ icon: Shield, label: 'DPDP Compliant' }, { icon: Zap, label: 'ACID Transactions' }, { icon: Wifi, label: 'Offline-First PWA' }].map((b, i) => {
              const Icon = b.icon;
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>
                  <Icon size={14} color="var(--text-muted)" /> {b.label}
                </div>
              );
            })}
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {['FastAPI', 'React 18', 'PostgreSQL', 'TypeScript'].map(t => (
              <span key={t} style={{ fontSize: '0.7rem', color: 'var(--text-muted)', background: '#fff', padding: '4px 12px', borderRadius: 'var(--radius-full)', border: '1px solid rgba(0,0,0,0.08)', fontFamily: 'var(--font-mono)' }}>{t}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{ padding: 'clamp(80px,10vw,120px) clamp(24px,6vw,80px)', textAlign: 'center', position: 'relative', zIndex: 1 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 60% 50% at 50% 80%, rgba(244,79,154,0.05) 0%, transparent 70%)', pointerEvents: 'none' }} />
        <motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.7, ease: [0.22,1,0.36,1] }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(2rem,4vw,3.2rem)', fontWeight: 700, color: '#0F0F1A', letterSpacing: '-0.02em', marginBottom: 16 }}>
            Ready to transform <span style={{ color: '#f44f9a' }}>Naturals</span>?
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 40, fontSize: '1.05rem', maxWidth: 480, margin: '0 auto 40px' }}>
            Every soul deserves a salon that truly understands them.
          </p>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            <MagneticBtn to="/register">Get Started <ArrowRight size={15} /></MagneticBtn>
            <MagneticBtn to="/login" ghost>Sign In</MagneticBtn>
          </div>
        </motion.div>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{ borderTop: '1px solid rgba(0,0,0,0.07)', padding: '24px clamp(24px,6vw,60px)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <AuraLogo />
        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          AURA v2.0 — Naturals BeautyTech Hackathon 2026
        </p>
      </footer>
    </div>
  );
}
