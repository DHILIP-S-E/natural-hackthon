import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Sparkles, Heart, Calendar, BookOpen, Award, TrendingUp, Sun, Droplets, Wind, Eye, Star, Shield } from 'lucide-react';
import BeautyScoreRing from '../../components/BeautyScoreRing';
import { TiltCard } from '../../components/ui/TiltCard';
import { Icon3D } from '../../components/ui/Icon3D';
import api from '../../config/api';
import { useAuthStore } from '../../stores/authStore';
import { ARCH_DATA } from '../../constants/archetypes';

// Skeleton defined outside render to avoid remount on re-render
const Skeleton = ({ width = '100%', height = 20 }: { width?: string | number; height?: number }) => (
  <div style={{ width, height, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', borderRadius: 'var(--radius-sm)' }} />
);

export default function CustomerDashboard() {
  const [activeTab, setActiveTab] = useState<'passport' | 'soulskin' | 'journey'>('passport');
  const user = useAuthStore((s) => s.user);
  const customerId = user?.id || 'me';

  // Fetch customer profile
  const { data: profileData, isLoading: profileLoading } = useQuery({
    queryKey: ['customer-profile', customerId],
    queryFn: () => api.get('/customers/' + customerId).then(r => r.data?.data),
  });

  // Fetch recent bookings (for journey timeline)
  const { data: bookingsData, isLoading: bookingsLoading } = useQuery({
    queryKey: ['customer-bookings-recent'],
    queryFn: () => api.get('/bookings?page=1&per_page=5').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.bookings || d?.items || [];
    }),
  });

  // Fetch climate data for customer's city
  const customerCity = profileData?.city || '';
  const { data: climateData } = useQuery({
    queryKey: ['climate', customerCity],
    queryFn: () => api.get('/climate?city=' + encodeURIComponent(customerCity)).then(r => r.data?.data),
    enabled: !!customerCity,
  });

  // Map API profile to the shape the UI expects
  const CUSTOMER = profileData ? {
    name: profileData.name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || '',
    beautyScore: profileData.beauty_score ?? 0,
    passport: profileData.passport_completeness ?? 0,
    hair: {
      type: profileData.hair_type || '--',
      texture: profileData.hair_texture || '--',
      color: profileData.natural_hair_color || '--',
      damage: profileData.hair_damage_level ?? 0,
    },
    skin: {
      type: profileData.skin_type || '--',
      tone: profileData.skin_tone || '--',
      undertone: profileData.undertone || '--',
      concerns: profileData.primary_skin_concerns?.length ? profileData.primary_skin_concerns : [],
    },
    archetype: profileData.dominant_archetype || 'bloom',
    allergies: profileData.known_allergies?.length ? profileData.known_allergies : [],
    goal: profileData.primary_goal || '',
    goalProgress: profileData.goal_progress_pct ?? 0,
    visits: profileData.total_visits ?? 0,
    ltv: profileData.lifetime_value ?? 0,
    city: profileData.city || '',
    uv: climateData?.uv_index ?? profileData.local_uv_index ?? 0,
    humidity: climateData?.humidity_pct ?? profileData.local_humidity ?? 0,
    aqi: climateData?.aqi ?? profileData.local_aqi ?? 0,
  } : {
    name: `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || '',
    beautyScore: 0, passport: 0,
    hair: { type: '--', texture: '--', color: '--', damage: 0 },
    skin: { type: '--', tone: '--', undertone: '--', concerns: [] as string[] },
    archetype: 'bloom' as const,
    allergies: [] as string[],
    goal: '', goalProgress: 0,
    visits: 0, ltv: 0,
    city: '', uv: 0, humidity: 0, aqi: 0,
  };

  // Map bookings to journey entries
  const JOURNEY = (Array.isArray(bookingsData) ? bookingsData : []).map((b: any) => ({
    date: b.scheduled_at ? new Date(b.scheduled_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '',
    service: b.service_name || b.service || 'Service',
    archetype: b.archetype || b.soulskin_archetype || 'bloom',
    rating: b.customer_rating ?? b.rating ?? 5,
  }));

  const isLoading = profileLoading && !profileData;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header with beauty score */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          {isLoading ? (
            <Skeleton width={110} height={110} />
          ) : (
            <BeautyScoreRing score={CUSTOMER.beautyScore} size={110} />
          )}
          <div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Salon Passport</p>
            {isLoading ? (
              <Skeleton width={200} height={32} />
            ) : (
              <h1 style={{ fontSize: '2rem', fontWeight: 700, color: '#1A1A24', letterSpacing: '-0.01em' }}>{CUSTOMER.name}</h1>
            )}
            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              {(() => {
                const arch = ARCH_DATA[CUSTOMER.archetype] || ARCH_DATA.bloom;
                const Icon = arch.icon;
                return (
                  <div style={{ background: `${arch.color}12`, border: `1px solid ${arch.color}25`, color: arch.color, padding: '5px 12px', borderRadius: 'var(--radius-full)', fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Icon size={12} strokeWidth={2.5} /> {arch.label}
                  </div>
                );
              })()}
              <span className="badge badge-teal" style={{ padding: '5px 12px', fontWeight: 600 }}>{CUSTOMER.visits} visits</span>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>MEMBER SINCE</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-display)' }}>OCT 2024</div>
        </div>
      </div>

      {/* Quick KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-md)' }}>
        {[
          { label: 'Next Visit', value: 'Mar 25', icon: Calendar, color: '#2A9D8F' },
          { label: 'Goal Progress', value: `${CUSTOMER.goalProgress}%`, icon: TrendingUp, color: '#f44f9a' },
          { label: 'Passport', value: `${CUSTOMER.passport}%`, icon: Award, color: '#9B7FD4' },
          { label: 'Soul Journal', value: `${JOURNEY.length}`, icon: Heart, color: '#E8A87C' },
        ].map((k, i) => {
          const Icon = k.icon;
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
              <TiltCard tiltIntensity={5} style={{ borderLeft: `4px solid ${k.color}`, padding: '20px', background: '#fff', height: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: k.color, marginBottom: 8 }}>
                  <div style={{ width: 24, height: 24, borderRadius: 6, background: `${k.color}12`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={14} color={k.color} />
                  </div>
                  <span className="kpi-label" style={{ fontWeight: 600, fontSize: '0.75rem', letterSpacing: '0.02em', color: 'var(--text-muted)' }}>{k.label}</span>
                </div>
                <span className="kpi-value" style={{ fontSize: '1.35rem', fontWeight: 700 }}>{k.value}</span>
              </TiltCard>
            </motion.div>
          );
        })}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 24, borderBottom: '1px solid var(--border-subtle)', paddingBottom: 0 }}>
        {[
          { key: 'passport' as const, label: 'BEAUTY PASSPORT', icon: <Eye size={14} /> },
          { key: 'soulskin' as const, label: 'SOULSKIN', icon: <Sparkles size={14} /> },
          { key: 'journey' as const, label: 'JOURNEY', icon: <BookOpen size={14} /> },
        ].map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            style={{
              padding: '12px 4px', background: 'none', border: 'none', cursor: 'pointer',
              color: activeTab === t.key ? '#f44f9a' : 'var(--text-muted)',
              borderBottom: activeTab === t.key ? '2px solid #f44f9a' : '2px solid transparent',
              fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8,
              transition: 'all 0.2s', letterSpacing: '0.08em'
            }}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ minHeight: 400 }}>
        {activeTab === 'passport' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-lg)' }}>
              {/* Hair diagnostics */}
              <TiltCard tiltIntensity={3} className="card" style={{ padding: '24px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, color: '#1A1A24' }}>
                  <div style={{ width: 28, height: 28, borderRadius: 6, background: 'rgba(244,79,154,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon3D size="sm" color="#f44f9a">👩</Icon3D>
                  </div>
                  Hair Profile
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  {[
                    { l: 'Type', v: CUSTOMER.hair.type },
                    { l: 'Texture', v: CUSTOMER.hair.texture },
                    { l: 'Color', v: CUSTOMER.hair.color },
                    { l: 'Damage Level', v: `${CUSTOMER.hair.damage}/5` },
                  ].map((f, i) => (
                    <div key={i}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 2 }}>{f.l}</div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>{f.v}</div>
                    </div>
                  ))}
                </div>
              </TiltCard>

              {/* Skin diagnostics */}
              <TiltCard tiltIntensity={3} className="card" style={{ padding: '24px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, color: '#1A1A24' }}>
                  <div style={{ width: 28, height: 28, borderRadius: 6, background: 'rgba(155,127,212,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon3D size="sm" color="#9B7FD4">✨</Icon3D>
                  </div>
                  Skin Profile
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  {[
                    { l: 'Type', v: CUSTOMER.skin.type },
                    { l: 'Tone', v: CUSTOMER.skin.tone },
                    { l: 'Undertone', v: CUSTOMER.skin.undertone },
                    { l: 'Concerns', v: CUSTOMER.skin.concerns.join(', ') },
                  ].map((f, i) => (
                    <div key={i}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 2 }}>{f.l}</div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>{f.v}</div>
                    </div>
                  ))}
                </div>
              </TiltCard>

              {/* Environment */}
              <TiltCard tiltIntensity={3} className="card" style={{ borderTop: '4px solid #E8A87C', padding: '24px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, color: '#1A1A24' }}>
                  <div style={{ width: 28, height: 28, borderRadius: 6, background: 'rgba(232,168,124,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Sun size={16} color="#E8A87C" />
                  </div>
                  Environmental Context
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                  <div style={{ textAlign: 'center' }}>
                    <Sun size={20} style={{ color: '#E8A87C', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{CUSTOMER.uv}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>UV Index</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Droplets size={20} style={{ color: '#4A9FD4', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{CUSTOMER.humidity}%</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Humidity</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Wind size={20} style={{ color: '#6B8FA6', marginBottom: 4 }} />
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#6B8FA6' }}>{CUSTOMER.aqi}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>AQI</div>
                  </div>
                </div>
                <div style={{ marginTop: 16, padding: '12px 14px', background: 'rgba(232,168,124,0.08)', border: '1px solid rgba(232,168,124,0.15)', borderRadius: 'var(--radius-md)', fontSize: '0.75rem', color: '#B46A3D', fontWeight: 500, lineHeight: 1.5 }}>
                  ⚠️ High UV detected. We recommend SPF 50 application every 2 hours for today's {CUSTOMER.city} climate.
                </div>
              </TiltCard>

              {/* Allergies & Goals */}
              <TiltCard tiltIntensity={3} className="card" style={{ padding: '24px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20, fontSize: '0.95rem', fontWeight: 700, color: '#1A1A24' }}>
                  <div style={{ width: 28, height: 28, borderRadius: 6, background: 'rgba(232,97,26,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Shield size={16} color="#E8611A" />
                  </div>
                  Safety & Goals
                </h4>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>Known Allergies</div>
                  <div style={{ display: 'flex', gap: 6 }}>
                    {CUSTOMER.allergies.map((a: string) => <span key={a} className="badge badge-rose" style={{ fontWeight: 600 }}>{a}</span>)}
                  </div>
                </div>
                <div style={{ marginTop: 16 }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>Active Goal</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{CUSTOMER.goal}</div>
                  <div style={{ marginTop: 10, height: 6, background: 'rgba(0,0,0,0.04)', borderRadius: 3 }}>
                    <motion.div initial={{ width: 0 }} animate={{ width: `${CUSTOMER.goalProgress}%` }} transition={{ duration: 0.8 }}
                      style={{ height: '100%', background: '#f44f9a', borderRadius: 3 }} />
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 4, fontWeight: 500 }}>{CUSTOMER.goalProgress}% complete</div>
                </div>
              </TiltCard>
            </div>
          </motion.div>
        )}

        {activeTab === 'soulskin' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="soulskin-bg" style={{ borderRadius: 'var(--radius-lg)', padding: 'var(--space-2xl)', textAlign: 'center' }}>
            <Sparkles size={32} style={{ color: '#9B7FD4', marginBottom: 20, opacity: 0.7 }} />
            <h3 className="soulskin-text-glow" style={{ color: '#F0EEF8', marginBottom: 12, fontFamily: 'var(--font-display)', fontSize: '1.75rem' }}>Your Soul Journal</h3>
            <p style={{ color: '#9B99B0', marginBottom: 32, fontSize: '1rem', maxWidth: 500, margin: '0 auto 32px' }}>Track your emotional evolution through our proprietary SOULSKIN mapping.</p>

            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginBottom: 48, flexWrap: 'wrap' }}>
              {Object.entries(ARCH_DATA).map(([key, data]) => {
                const Icon = data.icon;
                return (
                  <div key={key} style={{ background: `${data.color}18`, border: `1px solid ${data.color}30`, borderRadius: 'var(--radius-full)', padding: '8px 18px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                    <Icon size={14} color={data.color} strokeWidth={2.5} />
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: data.color }}>{data.label}</span>
                  </div>
                );
              })}
            </div>

            <div style={{ maxWidth: 460, margin: '0 auto' }}>
              <div className="card" style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(155,127,212,0.25)', padding: '32px' }}>
                <p style={{ fontStyle: 'italic', color: '#F0EEF8', marginBottom: 24, fontSize: '1.1rem', lineHeight: 1.6 }}>
                  "You are currently in full bloom. Something new is opening inside you — a celebration, a beginning, a joy that has been waiting."
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: 8, alignItems: 'center', marginBottom: 8 }}>
                  {(() => { const BloomIcon = ARCH_DATA.bloom.icon; return <BloomIcon size={24} color="#E8A87C" />; })()}
                  <span style={{ fontSize: '1rem', fontWeight: 700, color: '#E8A87C', letterSpacing: '0.05em' }}>BLOOM</span>
                </div>
                <p style={{ fontSize: '0.75rem', color: '#5C5A70', marginTop: 12, letterSpacing: '0.1em' }}>LAST READING: MARCH 15, 2026</p>
              </div>
            </div>

            <button className="btn btn-violet btn-lg" style={{ marginTop: 32 }}>
              <Sparkles size={16} /> Start New Session
            </button>
          </motion.div>
        )}

        {activeTab === 'journey' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {bookingsLoading && !bookingsData ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16, padding: '16px 0' }}>
                {[1, 2, 3].map(i => (
                  <div key={i} style={{ display: 'flex', gap: 20, padding: '16px 0' }}>
                    <Skeleton width={10} height={10} />
                    <div style={{ flex: 1 }}>
                      <Skeleton width={200} height={18} />
                      <div style={{ marginTop: 8 }}><Skeleton width={80} height={14} /></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : JOURNEY.length === 0 ? (
              <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No journey entries yet. Book a service to get started.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                {JOURNEY.map((j, i) => (
                  <div key={i} style={{ display: 'flex', gap: 20, padding: '16px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 40, flexShrink: 0 }}>
                      <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f44f9a' }} />
                      {i < JOURNEY.length - 1 && <div style={{ width: 1, flex: 1, background: 'var(--border-subtle)' }} />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                        <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1A1A24' }}>{j.service}</span>
                        {(() => {
                          const arch = ARCH_DATA[j.archetype] || ARCH_DATA.bloom;
                          const Icon = arch.icon;
                          return (
                            <div style={{ background: `${arch.color}12`, padding: '3px 8px', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                              <Icon size={10} color={arch.color} strokeWidth={3} />
                              <span style={{ fontSize: '0.65rem', fontWeight: 800, color: arch.color }}>{arch.label.toUpperCase()}</span>
                            </div>
                          );
                        })()}
                        <div style={{ display: 'flex', gap: 2, marginLeft: 'auto' }}>
                          {[...Array(5)].map((_, s) => <Star key={s} size={12} fill={s < j.rating ? '#f44f9a' : 'transparent'} color={s < j.rating ? '#f44f9a' : 'rgba(0,0,0,0.1)'} />)}
                        </div>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>{j.date}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
