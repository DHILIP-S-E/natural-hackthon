import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Palette, Camera, Scissors, Sparkles, RotateCcw, Share2, BookmarkPlus, ChevronRight } from 'lucide-react';
import api from '../../config/api';

export default function ARMirrorPage() {
  const [mode, setMode] = useState<'hairstyle' | 'color' | 'makeup'>('hairstyle');
  const [selected, setSelected] = useState<string | null>(null);
  const [saved, setSaved] = useState<string[]>([]);

  const { data: mirrorData, isLoading: _isLoading } = useQuery({
    queryKey: ['mirror-styles'],
    queryFn: () => api.get('/mirror/styles').then(r => r.data?.data),
    retry: false,
  });

  const HAIRSTYLES: { name: string; category: string; trending: boolean; img: string }[] = mirrorData?.hairstyles || [];
  const MAKEUP_LOOKS: { name: string; desc: string; icon: string }[] = mirrorData?.makeup_looks || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <Palette size={28} style={{ color: 'var(--teal)' }} /> AI Smart Mirror
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Virtual try-on — hairstyles, colors, and makeup simulation</p>
      </div>

      {/* Mode toggles */}
      <div style={{ display: 'flex', gap: 8 }}>
        {[
          { key: 'hairstyle' as const, label: 'Hairstyles', icon: <Scissors size={14} /> },
          { key: 'color' as const, label: 'Hair Color', icon: <Palette size={14} /> },
          { key: 'makeup' as const, label: 'Makeup', icon: <Sparkles size={14} /> },
        ].map(m => (
          <button key={m.key} onClick={() => { setMode(m.key); setSelected(null); }}
            className={`btn ${mode === m.key ? 'btn-teal' : 'btn-ghost'}`} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {m.icon} {m.label}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Mirror Preview */}
        <div className="card" style={{ minHeight: 450, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-surface)', position: 'relative', overflow: 'hidden' }}>
          {/* Simulated AR preview */}
          <div style={{
            width: 200, height: 250, borderRadius: '50% 50% 45% 45%',
            background: 'linear-gradient(180deg, rgba(201,169,110,0.1) 0%, rgba(155,127,212,0.05) 100%)',
            border: '2px solid var(--border-medium)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '4rem', position: 'relative',
          }}>
            👤
            {selected && (
              <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                style={{ position: 'absolute', top: -10, right: -10, fontSize: '2rem' }}>
                {mode === 'hairstyle' ? '✂️' : mode === 'color' ? '🎨' : '💄'}
              </motion.div>
            )}
          </div>

          <p style={{ marginTop: 16, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            {selected ? `Previewing: ${selected}` : 'Select a style to preview'}
          </p>

          {selected && (
            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              <button className="btn btn-ghost btn-sm" onClick={() => {
                if (!saved.includes(selected)) setSaved([...saved, selected]);
              }}>
                <BookmarkPlus size={14} /> Save
              </button>
              <button className="btn btn-ghost btn-sm"><Share2 size={14} /> Share</button>
              <button className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}><RotateCcw size={14} /> Reset</button>
            </div>
          )}

          <div style={{ position: 'absolute', bottom: 16, left: 16 }}>
            <span className="badge badge-teal"><Camera size={10} /> AR Preview</span>
          </div>
        </div>

        {/* Style Picker */}
        <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4>{mode === 'hairstyle' ? 'Hairstyles' : mode === 'color' ? 'Hair Colors' : 'Makeup Looks'}</h4>
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {mode !== 'makeup' ? HAIRSTYLES.filter(h => mode === 'hairstyle' ? !h.category.includes('Color') : h.category === 'Color').concat(mode === 'color' ? HAIRSTYLES.filter(h => h.category === 'Color') : []).map((h, i) => (
              <div key={i} onClick={() => setSelected(h.name)}
                style={{
                  padding: '12px 20px', borderBottom: '1px solid var(--border-subtle)',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  cursor: 'pointer', background: selected === h.name ? 'var(--teal-glow)' : 'transparent',
                  transition: 'background 0.15s',
                }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ fontSize: '1.5rem' }}>{h.img}</span>
                  <div>
                    <div style={{ fontWeight: 500, fontSize: '0.85rem' }}>{h.name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{h.category}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {h.trending && <span className="badge badge-gold" style={{ padding: '2px 6px', fontSize: '0.6rem' }}>Trending</span>}
                  <ChevronRight size={14} style={{ color: 'var(--text-muted)' }} />
                </div>
              </div>
            )) : MAKEUP_LOOKS.map((m, i) => (
              <div key={i} onClick={() => setSelected(m.name)}
                style={{
                  padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)',
                  cursor: 'pointer', background: selected === m.name ? 'var(--teal-glow)' : 'transparent',
                  transition: 'background 0.15s',
                }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ fontSize: '1.5rem' }}>{m.icon}</span>
                  <div>
                    <div style={{ fontWeight: 500, fontSize: '0.85rem' }}>{m.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{m.desc}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Saved */}
          {saved.length > 0 && (
            <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-surface)' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>💾 Saved ({saved.length})</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {saved.map(s => <span key={s} className="badge badge-gold" style={{ padding: '2px 8px', fontSize: '0.7rem' }}>{s}</span>)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
