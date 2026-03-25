import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  MapPin, Calendar, Target, ShoppingBag, Home, BarChart3,
  CheckCircle, Circle, Clock, RefreshCw
} from 'lucide-react';
import api from '../../config/api';
import BeautyScoreRing from '../../components/BeautyScoreRing';
import { ARCH_DATA } from '../../constants/archetypes';

type TabKey = 'salon' | 'homecare' | 'products' | 'progress';

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'salon', label: 'Salon Plan', icon: <Calendar size={14} /> },
  { key: 'homecare', label: 'Home Care', icon: <Home size={14} /> },
  { key: 'products', label: 'Products', icon: <ShoppingBag size={14} /> },
  { key: 'progress', label: 'Progress', icon: <BarChart3 size={14} /> },
];

export default function BeautyJourney() {
  const [activeTab, setActiveTab] = useState<TabKey>('salon');

  const { data: journeyData, isLoading } = useQuery({
    queryKey: ['beauty-journey'],
    queryFn: () => api.get('/journey/').then(r => {
      const items = r.data?.data;
      if (Array.isArray(items) && items.length > 0) return items[0];
      if (items && !Array.isArray(items)) return items;
      return null;
    }),
  });

  const plan = journeyData;
  const milestones: any[] = plan?.milestones ?? [];
  const homecareSteps: any[] = plan?.homecare_steps ?? plan?.homecare ?? [];
  const products: any[] = plan?.products ?? plan?.product_recommendations ?? [];
  const progressData: any[] = plan?.progress_data ?? plan?.progress ?? [];
  const progressPct = plan ? (plan.current_week / plan.duration_weeks) * 100 : 0;

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <MapPin size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading your Beauty Journey...</p>
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Target size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
          <p style={{ fontSize: '1rem' }}>No journey plan yet</p>
          <p style={{ fontSize: '0.8rem' }}>Ask your stylist to create a beauty journey plan for you</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Beauty Journey</p>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>My Transformation Plan</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
            {plan.duration_weeks}-week plan &middot; Week {plan.current_week} of {plan.duration_weeks}
          </p>
        </div>
        <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <RefreshCw size={16} /> Generate New Journey Plan
        </button>
      </div>

      {/* Goal Statement + Progress Ring */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="card" style={{ padding: '24px', display: 'flex', gap: 32, alignItems: 'center', borderLeft: '4px solid #f44f9a' }}>
        <BeautyScoreRing score={plan.overall_progress} size={90} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>Goal</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 12 }}>{plan.goal}</div>
          <div style={{ display: 'flex', gap: 24 }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Start Score</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{plan.beauty_score_start}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Current</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#f44f9a' }}>{plan.beauty_score_current}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Target</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--success)' }}>{plan.beauty_score_target}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Est. Cost</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{'\u20B9'}{(Number(plan.estimated_cost) || 0).toLocaleString()}</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Week progress bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 6 }}>
          <span>Week {plan.current_week}</span>
          <span>{Math.round(progressPct)}% of journey</span>
        </div>
        <div style={{ height: 6, background: 'var(--border-subtle)', borderRadius: 3 }}>
          <motion.div initial={{ width: 0 }} animate={{ width: `${progressPct}%` }} transition={{ duration: 0.8 }}
            style={{ height: '100%', background: '#f44f9a', borderRadius: 3 }} />
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid var(--border-subtle)' }}>
        {TABS.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            style={{
              padding: '12px 16px', background: 'none', border: 'none', cursor: 'pointer',
              color: activeTab === t.key ? '#f44f9a' : 'var(--text-muted)',
              borderBottom: activeTab === t.key ? '2px solid #f44f9a' : '2px solid transparent',
              fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6,
              transition: 'all 0.2s', letterSpacing: '0.06em',
            }}>
            {t.icon} {t.label.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ minHeight: 400 }}>
        {/* SALON PLAN - Timeline */}
        {activeTab === 'salon' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0, position: 'relative' }}>
              {milestones.map((m, i) => {
                const archData = m.archetype ? ARCH_DATA[m.archetype] : null;
                const ArchIcon = archData?.icon;
                const isCurrent = m.current === true;
                return (
                  <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                    style={{ display: 'flex', gap: 20, position: 'relative' }}>
                    {/* Timeline line */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 40, flexShrink: 0 }}>
                      <div style={{
                        width: isCurrent ? 16 : 12, height: isCurrent ? 16 : 12, borderRadius: '50%',
                        background: m.completed ? 'var(--success)' : isCurrent ? '#f44f9a' : 'var(--border-medium)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        border: isCurrent ? '3px solid rgba(244,79,154,0.3)' : 'none',
                      }}>
                        {m.completed && <CheckCircle size={8} color="#fff" />}
                      </div>
                      {i < milestones.length - 1 && <div style={{ width: 2, flex: 1, minHeight: 40, background: m.completed ? 'var(--success)' : 'var(--border-subtle)' }} />}
                    </div>

                    {/* Content card */}
                    <div className="card" style={{
                      flex: 1, padding: '16px 20px', marginBottom: 12,
                      borderLeft: isCurrent ? '3px solid #f44f9a' : m.completed ? '3px solid var(--success)' : '3px solid transparent',
                      background: isCurrent ? 'rgba(244,79,154,0.03)' : undefined,
                      opacity: m.completed ? 0.7 : 1,
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>WEEK {m.week}</span>
                          {isCurrent && <span className="badge badge-rose" style={{ fontSize: '0.6rem', padding: '2px 8px' }}>Current</span>}
                          {m.completed && <span className="badge badge-success" style={{ fontSize: '0.6rem', padding: '2px 8px' }}>Done</span>}
                        </div>
                        {archData && ArchIcon && (
                          <div style={{ background: `${archData.color}12`, padding: '3px 8px', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <ArchIcon size={10} color={archData.color} strokeWidth={3} />
                            <span style={{ fontSize: '0.6rem', fontWeight: 800, color: archData.color }}>{archData.label.toUpperCase()}</span>
                          </div>
                        )}
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: 4 }}>{m.title}</div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 8, lineHeight: 1.5 }}>{m.description}</p>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Calendar size={12} /> {m.service}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* HOME CARE */}
        {activeTab === 'homecare' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-lg)' }}>
              {homecareSteps.map((routine, i) => (
                <motion.div key={routine.time} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                  className="card" style={{ padding: '24px' }}>
                  <h4 style={{ marginBottom: 16, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Clock size={16} style={{ color: '#f44f9a' }} /> {routine.time}
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {routine.steps.map((step: any, j: number) => (
                      <div key={j} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: '0.85rem' }}>
                        <Circle size={8} style={{ color: 'var(--border-medium)', flexShrink: 0 }} />
                        {step}
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* PRODUCTS */}
        {activeTab === 'products' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div className="card" style={{ padding: 0 }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><ShoppingBag size={16} /> Recommended Products</h4>
                <span className="badge badge-teal" style={{ fontWeight: 600 }}>{products.length} items</span>
              </div>
              {products.map((p, i) => (
                <motion.div key={p.name} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}
                  style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                      {p.name}
                      {p.inPlan && <span className="badge badge-success" style={{ fontSize: '0.6rem', padding: '2px 6px' }}>In Plan</span>}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{p.brand}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <span className="badge" style={{
                      padding: '3px 8px', fontWeight: 600, fontSize: '0.7rem',
                      background: p.priority === 'Essential' ? 'rgba(244,79,154,0.1)' : p.priority === 'Recommended' ? 'rgba(42,157,143,0.1)' : 'rgba(0,0,0,0.04)',
                      color: p.priority === 'Essential' ? '#f44f9a' : p.priority === 'Recommended' ? 'var(--teal)' : 'var(--text-muted)',
                    }}>{p.priority}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, minWidth: 60, textAlign: 'right' }}>{'\u20B9'}{(Number(p.price) || 0).toLocaleString()}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* PROGRESS */}
        {activeTab === 'progress' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-lg)' }}>
              {progressData.map((p, i) => {
                const range = p.inverted ? (p.start - p.target) : (p.target - p.start);
                const achieved = p.inverted ? (p.start - p.current) : (p.current - p.start);
                const pct = range > 0 ? Math.min(100, Math.round((achieved / range) * 100)) : 0;
                return (
                  <motion.div key={p.metric} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                    className="card" style={{ padding: '24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                      <h4 style={{ fontSize: '0.9rem', fontWeight: 700 }}>{p.metric}</h4>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#f44f9a' }}>{pct}%</span>
                    </div>
                    <div style={{ height: 8, background: 'var(--border-subtle)', borderRadius: 4, marginBottom: 12 }}>
                      <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ delay: 0.3, duration: 0.8 }}
                        style={{ height: '100%', background: pct >= 80 ? 'var(--success)' : pct >= 40 ? '#f44f9a' : 'var(--warning)', borderRadius: 4 }} />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>Start: {p.start}{p.unit}</span>
                      <span style={{ color: '#f44f9a', fontWeight: 600 }}>Now: {p.current}{p.unit}</span>
                      <span>Target: {p.target}{p.unit}</span>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
