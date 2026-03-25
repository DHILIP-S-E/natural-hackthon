import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Eye, Sparkles, Droplets, Sun, Wind, Shield,
  Scissors, BookOpen, Clock, Activity, AlertTriangle,
  Star, Coffee, Smile
} from 'lucide-react';
import api from '../../config/api';
import BeautyScoreRing from '../../components/BeautyScoreRing';
import ArchetypeBadge from '../../components/ArchetypeBadge';
import { ARCH_DATA } from '../../constants/archetypes';
import type { CustomerProfile } from '../../types';

type TabKey = 'overview' | 'hair' | 'skin' | 'lifestyle' | 'safety' | 'soul' | 'history';

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'overview', label: 'Overview', icon: <Eye size={14} /> },
  { key: 'hair', label: 'Hair', icon: <Scissors size={14} /> },
  { key: 'skin', label: 'Skin', icon: <Droplets size={14} /> },
  { key: 'lifestyle', label: 'Lifestyle', icon: <Coffee size={14} /> },
  { key: 'safety', label: 'Safety', icon: <Shield size={14} /> },
  { key: 'soul', label: 'Soul Profile', icon: <Sparkles size={14} /> },
  { key: 'history', label: 'History', icon: <BookOpen size={14} /> },
];

function DiagnosticRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</div>
      <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>{value}</div>
    </div>
  );
}

export default function BeautyPassport() {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  const customerId = 'me'; // current logged-in customer
  const { data: customer, isLoading } = useQuery({
    queryKey: ['customer-profile', customerId],
    queryFn: async () => {
      const res = await api.get(`/customers/${customerId}`);
      return res.data.data as CustomerProfile;
    },
    retry: false,
  });

  const { data: visitHistory = [] } = useQuery({
    queryKey: ['customer-history', customerId],
    queryFn: async () => {
      const res = await api.get(`/customers/${customerId}/history`);
      return res.data.data ?? [];
    },
    retry: false,
  });

  const c = (customer as any) ?? {};

  if (isLoading && !c) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Activity size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading your Beauty Passport...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          <BeautyScoreRing score={c.beauty_score ?? 78} size={110} />
          <div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Beauty Passport</p>
            <h1 style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.01em' }}>{c.name ?? 'My Passport'}</h1>
            <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
              {c.dominant_archetype && (
                <ArchetypeBadge archetype={c.dominant_archetype} size="md" />
              )}
              <span className="badge badge-teal" style={{ padding: '5px 12px', fontWeight: 600 }}>{c.total_visits ?? 0} visits</span>
              <span className="badge" style={{ padding: '5px 12px', fontWeight: 600, background: 'rgba(155,127,212,0.1)', color: '#9B7FD4' }}>
                {c.passport_completeness ?? 0}% complete
              </span>
            </div>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Lifetime Value</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-display)' }}>
            {'\u20B9'}{(Number(c.lifetime_value) || 0).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Tab Bar */}
      <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid var(--border-subtle)', overflowX: 'auto' }}>
        {TABS.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            style={{
              padding: '12px 16px', background: 'none', border: 'none', cursor: 'pointer',
              color: activeTab === t.key ? '#f44f9a' : 'var(--text-muted)',
              borderBottom: activeTab === t.key ? '2px solid #f44f9a' : '2px solid transparent',
              fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6,
              transition: 'all 0.2s', letterSpacing: '0.06em', whiteSpace: 'nowrap',
            }}>
            {t.icon} {t.label.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ minHeight: 400 }}>
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-lg)' }}>
              {/* Quick Hair Summary */}
              <div className="card" style={{ padding: '24px', borderLeft: '4px solid #f44f9a' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, fontSize: '0.95rem', fontWeight: 700 }}>
                  <Scissors size={16} style={{ color: '#f44f9a' }} /> Hair Summary
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <DiagnosticRow label="Type" value={c.hair_type ?? 'N/A'} />
                  <DiagnosticRow label="Texture" value={c.hair_texture ?? 'N/A'} />
                  <DiagnosticRow label="Color" value={c.current_hair_color ?? 'N/A'} />
                  <DiagnosticRow label="Damage" value={`${c.hair_damage_level ?? 0}/5`} />
                </div>
              </div>

              {/* Quick Skin Summary */}
              <div className="card" style={{ padding: '24px', borderLeft: '4px solid #9B7FD4' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, fontSize: '0.95rem', fontWeight: 700 }}>
                  <Droplets size={16} style={{ color: '#9B7FD4' }} /> Skin Summary
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <DiagnosticRow label="Type" value={c.skin_type ?? 'N/A'} />
                  <DiagnosticRow label="Tone" value={c.skin_tone ?? 'N/A'} />
                  <DiagnosticRow label="Undertone" value={c.undertone ?? 'N/A'} />
                  <DiagnosticRow label="Concerns" value={c.primary_skin_concerns?.join(', ') ?? 'None'} />
                </div>
              </div>

              {/* Environment */}
              <div className="card" style={{ padding: '24px', borderLeft: '4px solid #E8A87C' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, fontSize: '0.95rem', fontWeight: 700 }}>
                  <Sun size={16} style={{ color: '#E8A87C' }} /> Environment
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                  <div style={{ textAlign: 'center' }}>
                    <Sun size={20} style={{ color: '#E8A87C', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{c.local_uv_index ?? '-'}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>UV Index</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Droplets size={20} style={{ color: '#4A9FD4', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{c.local_humidity ?? '-'}%</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Humidity</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Wind size={20} style={{ color: '#6B8FA6', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{c.local_aqi ?? '-'}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>AQI</div>
                  </div>
                </div>
              </div>

              {/* Safety / Allergies */}
              <div className="card" style={{ padding: '24px', borderLeft: '4px solid var(--error)' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, fontSize: '0.95rem', fontWeight: 700 }}>
                  <Shield size={16} style={{ color: 'var(--error)' }} /> Safety & Goals
                </h4>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>Known Allergies</div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {(c.known_allergies ?? []).length > 0
                      ? c.known_allergies.map((a: string) => <span key={a} className="badge badge-rose" style={{ fontWeight: 600 }}>{a}</span>)
                      : <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None recorded</span>}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>Active Goal</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{c.primary_goal ?? 'No goal set'}</div>
                  <div style={{ marginTop: 10, height: 6, background: 'rgba(0,0,0,0.04)', borderRadius: 3 }}>
                    <motion.div initial={{ width: 0 }} animate={{ width: `${c.goal_progress_pct ?? 0}%` }} transition={{ duration: 0.8 }}
                      style={{ height: '100%', background: '#f44f9a', borderRadius: 3 }} />
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 4 }}>{c.goal_progress_pct ?? 0}% complete</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* HAIR TAB */}
        {activeTab === 'hair' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-lg)' }}>
              <div className="card" style={{ padding: '24px' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Scissors size={16} style={{ color: '#f44f9a' }} /> Hair Diagnostics
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <DiagnosticRow label="Hair Type" value={c.hair_type ?? 'N/A'} />
                  <DiagnosticRow label="Hair Texture" value={c.hair_texture ?? 'N/A'} />
                  <DiagnosticRow label="Hair Porosity" value={c.hair_porosity ?? 'N/A'} />
                  <DiagnosticRow label="Hair Density" value={c.hair_density ?? 'N/A'} />
                  <DiagnosticRow label="Scalp Condition" value={c.scalp_condition ?? 'N/A'} />
                  <DiagnosticRow label="Natural Color" value={c.natural_hair_color ?? 'N/A'} />
                  <DiagnosticRow label="Current Color" value={c.current_hair_color ?? 'N/A'} />
                </div>
              </div>
              <div className="card" style={{ padding: '24px' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700 }}>Damage Assessment</h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
                  <div style={{ fontSize: '3rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: (c.hair_damage_level ?? 0) <= 2 ? 'var(--success)' : (c.hair_damage_level ?? 0) <= 3 ? 'var(--warning)' : 'var(--error)' }}>
                    {c.hair_damage_level ?? 0}
                  </div>
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>out of 5</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Damage Level</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 4 }}>
                  {[1, 2, 3, 4, 5].map(level => (
                    <div key={level} style={{
                      flex: 1, height: 8, borderRadius: 4,
                      background: level <= (c.hair_damage_level ?? 0)
                        ? level <= 2 ? 'var(--success)' : level <= 3 ? 'var(--warning)' : 'var(--error)'
                        : 'var(--border-subtle)',
                    }} />
                  ))}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  <span>Minimal</span><span>Severe</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* SKIN TAB */}
        {activeTab === 'skin' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-lg)' }}>
              <div className="card" style={{ padding: '24px' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Droplets size={16} style={{ color: '#9B7FD4' }} /> Skin Diagnostics
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <DiagnosticRow label="Skin Type" value={c.skin_type ?? 'N/A'} />
                  <DiagnosticRow label="Skin Tone" value={c.skin_tone ?? 'N/A'} />
                  <DiagnosticRow label="Undertone" value={c.undertone ?? 'N/A'} />
                  <DiagnosticRow label="Sensitivity" value={c.skin_sensitivity ?? 'N/A'} />
                </div>
              </div>
              <div className="card" style={{ padding: '24px' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700 }}>Skin Concerns</h4>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
                  {(c.primary_skin_concerns ?? []).map((concern: string) => (
                    <span key={concern} className="badge" style={{ padding: '6px 14px', background: 'rgba(155,127,212,0.1)', color: '#9B7FD4', fontWeight: 600 }}>{concern}</span>
                  ))}
                  {(c.primary_skin_concerns ?? []).length === 0 && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No concerns recorded</span>
                  )}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>Acne Severity</div>
                    <div style={{ display: 'flex', gap: 4 }}>
                      {[1, 2, 3, 4, 5].map(l => (
                        <div key={l} style={{ width: 24, height: 6, borderRadius: 3, background: l <= (c.acne_severity ?? 0) ? 'var(--warning)' : 'var(--border-subtle)' }} />
                      ))}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>Pigmentation Level</div>
                    <div style={{ display: 'flex', gap: 4 }}>
                      {[1, 2, 3, 4, 5].map(l => (
                        <div key={l} style={{ width: 24, height: 6, borderRadius: 3, background: l <= (c.pigmentation_level ?? 0) ? '#E8A87C' : 'var(--border-subtle)' }} />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* LIFESTYLE TAB */}
        {activeTab === 'lifestyle' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-lg)' }}>
              <div className="card" style={{ padding: '24px' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Coffee size={16} style={{ color: '#E8A87C' }} /> Lifestyle Factors
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <DiagnosticRow label="City" value={c.city ?? 'N/A'} />
                  <DiagnosticRow label="Climate" value={c.climate_type ?? 'N/A'} />
                  <DiagnosticRow label="Stress Level" value={c.stress_level ?? 'N/A'} />
                  <DiagnosticRow label="Diet" value={c.diet_type ?? 'N/A'} />
                </div>
              </div>
              <div className="card" style={{ padding: '24px', borderTop: '4px solid #E8A87C' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Sun size={16} style={{ color: '#E8A87C' }} /> Environmental Context
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                  <div style={{ textAlign: 'center' }}>
                    <Sun size={20} style={{ color: '#E8A87C', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{c.local_uv_index ?? '-'}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>UV Index</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Droplets size={20} style={{ color: '#4A9FD4', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{c.local_humidity ?? '-'}%</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Humidity</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Wind size={20} style={{ color: '#6B8FA6', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: (c.local_aqi ?? 0) > 100 ? '#6B8FA6' : 'var(--text-primary)' }}>{c.local_aqi ?? '-'}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>AQI</div>
                  </div>
                </div>
                {(c.local_uv_index ?? 0) >= 8 && (
                  <div style={{ marginTop: 16, padding: '12px 14px', background: 'rgba(232,168,124,0.08)', border: '1px solid rgba(232,168,124,0.15)', borderRadius: 'var(--radius-md)', fontSize: '0.75rem', color: '#B46A3D', fontWeight: 500, lineHeight: 1.5 }}>
                    High UV detected in {c.city}. SPF 50 recommended every 2 hours.
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* SAFETY TAB */}
        {activeTab === 'safety' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-lg)' }}>
              <div className="card" style={{ padding: '24px', border: '1px solid rgba(231,111,111,0.2)' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--error)' }}>
                  <AlertTriangle size={16} /> Known Allergies
                </h4>
                {(c.known_allergies ?? []).length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {c.known_allergies.map((allergy: string, i: number) => (
                      <motion.div key={allergy} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                        style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: 'rgba(231,111,111,0.06)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(231,111,111,0.1)' }}>
                        <AlertTriangle size={16} style={{ color: 'var(--error)', flexShrink: 0 }} />
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{allergy}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Flagged in all service protocols</div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    <Shield size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
                    <p>No allergies recorded</p>
                  </div>
                )}
              </div>
              <div className="card" style={{ padding: '24px' }}>
                <h4 style={{ marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Smile size={16} style={{ color: '#2A9D8F' }} /> Sensitivity Profile
                </h4>
                <div style={{ display: 'grid', gap: 16 }}>
                  <DiagnosticRow label="Emotional Sensitivity" value={c.emotional_sensitivity ?? 'N/A'} />
                  <DiagnosticRow label="Skin Sensitivity" value={c.skin_sensitivity ?? 'N/A'} />
                  <div style={{ padding: '12px', background: 'rgba(42,157,143,0.06)', borderRadius: 'var(--radius-md)', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    All stylists are briefed on your sensitivity profile before each session to ensure a comfortable experience.
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* SOUL PROFILE TAB */}
        {activeTab === 'soul' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="soulskin-bg" style={{ borderRadius: 'var(--radius-lg)', padding: 'var(--space-2xl)', textAlign: 'center' }}>
            <Sparkles size={32} style={{ color: '#9B7FD4', marginBottom: 20, opacity: 0.7 }} />
            <h3 style={{ color: '#F0EEF8', marginBottom: 12, fontFamily: 'var(--font-display)', fontSize: '1.75rem' }}>Soul Profile</h3>
            <p style={{ color: '#9B99B0', marginBottom: 32, fontSize: '1rem', maxWidth: 500, margin: '0 auto 32px' }}>Your emotional archetypes mapped across your beauty journey.</p>

            {/* Archetype chips */}
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginBottom: 48, flexWrap: 'wrap' }}>
              {Object.entries(ARCH_DATA).map(([key, data]) => {
                const Icon = data.icon;
                const isCurrent = c.dominant_archetype === key;
                return (
                  <div key={key} style={{
                    background: isCurrent ? `${data.color}30` : `${data.color}18`,
                    border: `${isCurrent ? 2 : 1}px solid ${data.color}${isCurrent ? '80' : '30'}`,
                    borderRadius: 'var(--radius-full)', padding: '8px 18px',
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
                    transform: isCurrent ? 'scale(1.1)' : 'scale(1)',
                  }}>
                    <Icon size={14} color={data.color} strokeWidth={2.5} />
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: data.color }}>{data.label}</span>
                    {isCurrent && <span style={{ fontSize: '0.6rem', color: data.color, opacity: 0.8 }}>Current</span>}
                  </div>
                );
              })}
            </div>

            {/* Archetype history */}
            {(c.archetype_history ?? []).length > 0 && (
              <div style={{ maxWidth: 500, margin: '0 auto' }}>
                <h4 style={{ fontSize: '0.85rem', color: '#9B99B0', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Archetype Timeline</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                  {c.archetype_history.map((entry: { archetype: string; date: string }, i: number) => {
                    const archData = ARCH_DATA[entry.archetype];
                    if (!archData) return null;
                    const Icon = archData.icon;
                    return (
                      <div key={i} style={{ display: 'flex', gap: 16, padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 30, flexShrink: 0 }}>
                          <div style={{ width: 10, height: 10, borderRadius: '50%', background: archData.color }} />
                          {i < c.archetype_history.length - 1 && <div style={{ width: 1, flex: 1, background: 'rgba(255,255,255,0.08)' }} />}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1 }}>
                          <Icon size={14} color={archData.color} />
                          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: archData.color }}>{archData.label}</span>
                          <span style={{ fontSize: '0.7rem', color: '#5C5A70', marginLeft: 'auto' }}>{entry.date}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* HISTORY TAB */}
        {activeTab === 'history' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div className="card" style={{ padding: 0 }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Clock size={16} /> Visit History
                </h4>
                <span className="badge badge-teal" style={{ fontWeight: 600 }}>{visitHistory.length} visits</span>
              </div>
              {visitHistory.length === 0 ? (
                <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <BookOpen size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
                  <p>No visit history yet</p>
                </div>
              ) : (
                visitHistory.map((visit: any, i: number) => {
                  const archData = visit.archetype ? ARCH_DATA[visit.archetype] : null;
                  const ArchIcon = archData?.icon;
                  return (
                    <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                      style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                        <div style={{ width: 40, height: 40, borderRadius: 'var(--radius-md)', background: 'var(--bg-surface)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Scissors size={16} style={{ color: 'var(--gold)' }} />
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                            {visit.service}
                            {archData && ArchIcon && (
                              <div style={{ background: `${archData.color}12`, padding: '2px 8px', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                                <ArchIcon size={10} color={archData.color} strokeWidth={3} />
                                <span style={{ fontSize: '0.6rem', fontWeight: 800, color: archData.color }}>{archData.label.toUpperCase()}</span>
                              </div>
                            )}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                            {visit.date} &middot; {visit.stylist}
                          </div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{'\u20B9'}{(Number(visit.amount) || 0).toLocaleString()}</span>
                        <div style={{ display: 'flex', gap: 2 }}>
                          {[...Array(5)].map((_, s) => (
                            <Star key={s} size={12} fill={s < visit.rating ? '#f44f9a' : 'transparent'} color={s < visit.rating ? '#f44f9a' : 'rgba(0,0,0,0.1)'} />
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
