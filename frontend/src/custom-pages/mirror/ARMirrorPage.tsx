import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Palette, Camera, Scissors, Sparkles, RotateCcw, Share2, BookmarkPlus, ChevronRight, History, Clock, Brain } from 'lucide-react';
import api from '../../config/api';

export default function ARMirrorPage() {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<'hairstyle' | 'color' | 'makeup'>('hairstyle');
  const [selected, setSelected] = useState<string | null>(null);
  const [selectedImg, setSelectedImg] = useState<string | null>(null);
  const [saved, setSaved] = useState<string[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [aiInsights, setAiInsights] = useState<{ face_shape: string; skin_tone: string; recommendation: string } | null>(null);

  const triggerScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      setAiInsights({
        face_shape: 'Oval',
        skin_tone: 'Fair/Olive',
        recommendation: 'Layered Waves or Bob with Bangs'
      });
    }, 2500);
  };

  // 1. Fetch Customer Profile (to get IDs)
  const { data: customer } = useQuery({
    queryKey: ['customer-me'],
    queryFn: () => api.get('/customers/me').then(r => r.data?.data),
  });

  // 2. Fetch Style Catalogue
  const { data: mirrorData, isLoading: _isLoadingStyles } = useQuery({
    queryKey: ['mirror-styles'],
    queryFn: () => api.get('/mirror/styles').then(r => r.data?.data),
    retry: false,
  });

  // 3. Fetch Session History
  const { data: sessions, isLoading: _isLoadingSessions } = useQuery({
    queryKey: ['mirror-sessions'],
    queryFn: () => api.get('/mirror/').then(r => r.data?.data),
    enabled: !!customer,
  });

  // 4. Mutation to create session
  const createSessionMutation = useMutation({
    mutationFn: (type: string) => api.post('/mirror/', {
      customer_id: customer?.id,
      location_id: customer?.preferred_location_id || '98b50e2ddc9943efb387052637738f61', // Fallback ID if none
      session_type: type
    }).then(r => r.data?.data),
    onSuccess: (data) => {
      setActiveSessionId(data.id);
      queryClient.invalidateQueries({ queryKey: ['mirror-sessions'] });
    }
  });

  // 5. Mutation to update session (Save style)
  const updateSessionMutation = useMutation({
    mutationFn: (updates: { saved_images?: string[], tryons?: any }) => 
      api.patch(`/mirror/${activeSessionId}`, updates).then(r => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mirror-sessions'] });
    }
  });

  const handleSelect = async (name: string, img: string) => {
    setSelected(name);
    setSelectedImg(img);

    // Auto-create session on first selection if none exists
    if (!activeSessionId && customer) {
      createSessionMutation.mutate(mode);
    }
  };

  const handleSave = () => {
    if (!selected) return;
    
    const newSaved = [...saved];
    if (!newSaved.includes(selected)) {
      newSaved.push(selected);
      setSaved(newSaved);
      
      // Persist to backend if session is active
      if (activeSessionId) {
        updateSessionMutation.mutate({ saved_images: newSaved });
      }
    }
  };

  const HAIRSTYLES = mirrorData?.hairstyles || [];
  const MAKEUP_LOOKS = mirrorData?.makeup_looks || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)', paddingBottom: 60 }}>
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
          <button key={m.key} onClick={() => { setMode(m.key); setSelected(null); setSelectedImg(null); }}
            className={`btn ${mode === m.key ? 'btn-teal' : 'btn-ghost'}`} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {m.icon} {m.label}
          </button>
        ))}
        <button onClick={triggerScan} className="btn btn-outline btn-sm" style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6, color: 'var(--teal)', borderColor: 'var(--teal)' }}>
          <Brain size={14} /> AI FACE ANALYSIS
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Mirror Preview */}
        <div className="card" style={{ minHeight: 450, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-surface)', position: 'relative', overflow: 'hidden' }}>
          {selected && selectedImg ? (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
              <img src={selectedImg.startsWith('http') 
                ? selectedImg.replace('w=200&h=200', 'w=400&h=500').replace('&fit=crop', '&fit=crop&crop=faces') 
                : selectedImg}
                alt={selected}
                style={{
                  width: 260, height: 320, objectFit: 'cover',
                  borderRadius: '50% 50% 45% 45%',
                  border: '3px solid var(--teal)',
                  boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
                }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: '1.2rem' }}>
                  {mode === 'hairstyle' ? '✂️' : mode === 'color' ? '🎨' : '💄'}
                </span>
                <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{selected}</span>
              </div>
            </motion.div>
          ) : (
            <div style={{
              width: 200, height: 250, borderRadius: '50% 50% 45% 45%',
              background: 'linear-gradient(180deg, rgba(201,169,110,0.1) 0%, rgba(155,127,212,0.05) 100%)',
              border: '2px solid var(--border-medium)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '4rem',
            }}>
              👤
            </div>
          )}

          {isScanning && (
            <motion.div
              initial={{ top: '10%' }}
              animate={{ top: '80%' }}
              transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
              style={{
                position: 'absolute', left: '10%', right: '10%',
                height: 2, background: 'var(--teal)',
                boxShadow: '0 0 15px var(--teal)',
                zIndex: 10,
              }}
            />
          )}

          {aiInsights && !isScanning && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              style={{
                position: 'absolute', top: 20, right: 20, width: 200,
                background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(8px)',
                borderRadius: '16px', padding: '16px', border: '1px solid var(--teal)',
                boxShadow: '0 8px 16px rgba(0,0,0,0.1)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--teal)', fontWeight: 800, fontSize: '0.65rem', marginBottom: 8, textTransform: 'uppercase' }}>
                <Brain size={12} /> AURA Smart Advisor
              </div>
              <div style={{ fontSize: '0.75rem', marginBottom: 4 }}><b>Face Shape:</b> {aiInsights.face_shape}</div>
              <div style={{ fontSize: '0.75rem', marginBottom: 4 }}><b>Skin Tone:</b> {aiInsights.skin_tone}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)', paddingTop: 8, marginTop: 4 }}>
                <b>Recommended:</b> {aiInsights.recommendation}
              </div>
            </motion.div>
          )}

          <p style={{ marginTop: 16, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            {selected ? `Previewing: ${selected}` : 'Select a style to preview'}
          </p>

          {selected && (
            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              <button className="btn btn-ghost btn-sm" onClick={handleSave} disabled={updateSessionMutation.isPending}>
                <BookmarkPlus size={14} /> {updateSessionMutation.isPending ? 'Saving...' : 'Save'}
              </button>
              <button className="btn btn-ghost btn-sm"><Share2 size={14} /> Share</button>
              <button className="btn btn-ghost btn-sm" onClick={() => { setSelected(null); setSelectedImg(null); }}><RotateCcw size={14} /> Reset</button>
            </div>
          )}

          <div style={{ position: 'absolute', bottom: 16, left: 16 }}>
            <span className="badge badge-teal"><Camera size={10} /> AR Preview</span>
          </div>
          {activeSessionId && (
            <div style={{ position: 'absolute', top: 16, right: 16 }}>
              <span className="badge badge-gold" style={{ fontSize: '0.65rem' }}>Active Session</span>
            </div>
          )}
        </div>

        {/* Style Picker */}
        <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4>{mode === 'hairstyle' ? 'Hairstyles' : mode === 'color' ? 'Hair Colors' : 'Makeup Looks'}</h4>
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {mode !== 'makeup' ? HAIRSTYLES.filter((h: any) => mode === 'hairstyle' ? h.category !== 'Color' : h.category === 'Color').map((h: any, i: number) => (
              <div key={i} onClick={() => handleSelect(h.name, h.img)}
                style={{
                  padding: '12px 20px', borderBottom: '1px solid var(--border-subtle)',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  cursor: 'pointer', background: selected === h.name ? 'var(--teal-glow)' : 'transparent',
                  transition: 'background 0.15s',
                }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <img src={h.img} alt={h.name} style={{ width: 44, height: 44, borderRadius: '50%', objectFit: 'cover' }} />
                  <div>
                    <div style={{ fontWeight: 500, fontSize: '0.85rem' }}>{h.name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{h.category}</div>
                    {aiInsights?.recommendation.includes(h.name.split(' ')[0]) && (
                      <span className="badge badge-teal" style={{ fontSize: '0.6rem', padding: '2px 4px', marginTop: 4 }}>AI Match</span>
                    )}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {h.trending && <span className="badge badge-gold" style={{ padding: '2px 6px', fontSize: '0.6rem' }}>Trending</span>}
                  <ChevronRight size={14} style={{ color: 'var(--text-muted)' }} />
                </div>
              </div>
            )) : MAKEUP_LOOKS.map((m: any, i: number) => (
              <div key={i} onClick={() => handleSelect(m.name, m.icon)}
                style={{
                  padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)',
                  cursor: 'pointer', background: selected === m.name ? 'var(--teal-glow)' : 'transparent',
                  transition: 'background 0.15s',
                }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <img src={m.icon} alt={m.name} style={{ width: 44, height: 44, borderRadius: '50%', objectFit: 'cover' }} />
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
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>💾 Saved in Current Session ({saved.length})</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {saved.map(s => <span key={s} className="badge badge-gold" style={{ padding: '2px 8px', fontSize: '0.7rem' }}>{s}</span>)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Session History */}
      <div className="card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
          <History size={20} style={{ color: 'var(--gold)' }} /> Recent Try-on History
        </h3>
        
        {sessions?.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
            {sessions.map((s: any) => (
              <div key={s.id} className="card" style={{ background: 'var(--bg-page)', border: '1px solid var(--border-subtle)', padding: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', textTransform: 'capitalize' }}>{s.session_type?.replace('_', ' ')} Session</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      <Clock size={12} /> {new Date(s.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <span className="badge badge-teal" style={{ fontSize: '0.65rem' }}>{s.saved_images?.length || 0} saved</span>
                </div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {s.saved_images?.length > 0 ? s.saved_images.slice(0, 3).map((img: string, idx: number) => (
                    <span key={idx} className="badge badge-outline" style={{ fontSize: '0.7rem' }}>{img}</span>
                  )) : <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontStyle: 'italic' }}>No styles saved</span>}
                  {s.saved_images?.length > 3 && <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>+{s.saved_images.length - 3} more</span>}
                </div>
                <button className="btn btn-ghost btn-sm" style={{ width: '100%', marginTop: 12, fontSize: '0.75rem' }} 
                        onClick={() => { setActiveSessionId(s.id); setSaved(s.saved_images || []); }}>
                  Resume Session
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
            <p>No recent sessions found. Start exploring styles to begin your first session!</p>
          </div>
        )}
      </div>
    </div>
  );
}
