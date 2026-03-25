import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Sun, Moon as MoonIcon, Calendar, Droplets, Scissors, CheckCircle, XCircle,
  ShoppingBag, Sparkles, Send, Activity
} from 'lucide-react';
import api from '../../config/api';
import { ARCH_DATA } from '../../constants/archetypes';

const ARCH_RITUALS: Record<string, string> = {
  phoenix: 'Light a candle before your evening routine. Focus on what you are releasing and what you are becoming.',
  river: 'Apply your products slowly, using flowing circular motions. Play ambient water sounds.',
  moon: 'Do your evening routine in low light. Speak gently to yourself. This is rest, not performance.',
  bloom: 'Smile at yourself in the mirror. Name one thing you love about your appearance today.',
  storm: 'Press your palms to your face for 10 seconds after each step. Ground yourself through touch.',
};

export default function HomecarePage() {
  const { data: plan, isLoading } = useQuery({
    queryKey: ['homecare-plan'],
    queryFn: () => api.get('/homecare/').then(r => {
      const items = r.data?.data;
      if (Array.isArray(items) && items.length > 0) return items[0];
      if (items && !Array.isArray(items)) return items;
      return null;
    }),
  });

  const p = plan;
  const archData = p?.archetype ? ARCH_DATA[p.archetype] : null;
  const ArchIcon = archData?.icon;

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Activity size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading your Homecare Plan...</p>
        </div>
      </div>
    );
  }

  if (!p) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Sparkles size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
          <p style={{ fontSize: '1rem' }}>No homecare plan yet</p>
          <p style={{ fontSize: '0.8rem' }}>Your stylist will create one after your next visit</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Homecare</p>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>My Homecare Plan</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
            {p.plan_duration_weeks}-week plan &middot; Generated {p.generated_at} &middot; Next visit: {p.next_visit}
          </p>
        </div>
        <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#25D366', borderColor: '#25D366' }}>
          <Send size={16} /> Send to WhatsApp
        </button>
      </div>

      {/* Archetype Ritual Card */}
      {archData && ArchIcon && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          style={{
            padding: '24px', borderRadius: 'var(--radius-lg)',
            background: `linear-gradient(135deg, ${archData.color}08, ${archData.color}15)`,
            border: `1px solid ${archData.color}25`,
          }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: `${archData.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArchIcon size={18} color={archData.color} />
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Your Archetype Ritual</div>
              <div style={{ fontWeight: 700, color: archData.color }}>{archData.label}</div>
            </div>
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontStyle: 'italic' }}>
            "{p?.archetype ? ARCH_RITUALS[p.archetype] || '' : ''}"
          </p>
        </motion.div>
      )}

      {/* Routines Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Hair Routine */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="card" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: 20, fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Scissors size={18} style={{ color: '#f44f9a' }} /> Hair Routine
          </h3>

          {p.hair_routine && Object.entries(p.hair_routine as Record<string, string[]>).map(([time, steps]) => (
            <div key={time} style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                {time === 'morning' && <Sun size={14} style={{ color: '#E8A87C' }} />}
                {time === 'evening' && <MoonIcon size={14} style={{ color: '#7B68C8' }} />}
                {time === 'weekly' && <Calendar size={14} style={{ color: '#2A9D8F' }} />}
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>{time}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, paddingLeft: 22 }}>
                {steps.map((step: string, i: number) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: '0.85rem', lineHeight: 1.5 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#f44f9a', marginTop: 6, flexShrink: 0 }} />
                    {step}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </motion.div>

        {/* Skin Routine */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="card" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: 20, fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Droplets size={18} style={{ color: '#9B7FD4' }} /> Skin Routine
          </h3>

          {p.skin_routine && Object.entries(p.skin_routine as Record<string, string[]>).map(([time, steps]) => (
            <div key={time} style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                {time === 'morning' && <Sun size={14} style={{ color: '#E8A87C' }} />}
                {time === 'evening' && <MoonIcon size={14} style={{ color: '#7B68C8' }} />}
                {time === 'weekly' && <Calendar size={14} style={{ color: '#2A9D8F' }} />}
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>{time}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, paddingLeft: 22 }}>
                {steps.map((step: string, i: number) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: '0.85rem', lineHeight: 1.5 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#9B7FD4', marginTop: 6, flexShrink: 0 }} />
                    {step}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Dos and Don'ts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="card" style={{ padding: '24px', borderLeft: '4px solid var(--success)' }}>
          <h4 style={{ marginBottom: 16, fontSize: '0.95rem', fontWeight: 700, color: 'var(--success)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <CheckCircle size={16} /> Do's
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {(p.dos ?? []).map((item: string, i: number) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, fontSize: '0.85rem', lineHeight: 1.5 }}>
                <CheckCircle size={14} style={{ color: 'var(--success)', flexShrink: 0, marginTop: 2 }} />
                {item}
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="card" style={{ padding: '24px', borderLeft: '4px solid var(--error)' }}>
          <h4 style={{ marginBottom: 16, fontSize: '0.95rem', fontWeight: 700, color: 'var(--error)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <XCircle size={16} /> Don'ts
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {(p.donts ?? []).map((item: string, i: number) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, fontSize: '0.85rem', lineHeight: 1.5 }}>
                <XCircle size={14} style={{ color: 'var(--error)', flexShrink: 0, marginTop: 2 }} />
                {item}
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Product Recommendations */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
        className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ShoppingBag size={16} /> Product Recommendations
          </h4>
          <span className="badge badge-teal" style={{ fontWeight: 600 }}>{(p.product_recommendations ?? []).length} products</span>
        </div>
        {(p.product_recommendations ?? []).length === 0 ? (
          <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <ShoppingBag size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
            <p>No product recommendations yet</p>
          </div>
        ) : (
          (p.product_recommendations as Array<{ name: string; brand: string; usage: string; price: number; essential: boolean }>).map((prod, _i) => (
            <div key={prod.name} style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                  {prod.name}
                  {prod.essential && <span className="badge badge-rose" style={{ fontSize: '0.6rem', padding: '2px 6px' }}>Essential</span>}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                  {prod.brand} &middot; {prod.usage}
                </div>
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{'\u20B9'}{(Number(prod.price) || 0).toLocaleString()}</span>
            </div>
          ))
        )}
      </motion.div>
    </div>
  );
}
