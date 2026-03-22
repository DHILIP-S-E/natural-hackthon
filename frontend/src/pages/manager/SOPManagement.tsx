import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, Plus, Search, ChevronRight, ChevronDown, Eye, Edit,
  AlertTriangle, Beaker, Clock, CheckCircle, X, Activity, Sparkles
} from 'lucide-react';
import api from '../../config/api';
import { ARCH_DATA } from '../../constants/archetypes';
import type { Archetype } from '../../types';

interface SOPStep {
  step: number;
  title: string;
  duration_minutes: number;
  critical: boolean;
  instructions: string;
  archetype_overlays?: Partial<Record<Archetype, string>>;
}

interface SOP {
  id: string;
  title: string;
  version: string;
  service: string;
  category: string;
  step_count: number;
  chemicals_involved: string[];
  is_chemical: boolean;
  created_at: string;
  updated_at: string;
  status: 'active' | 'draft' | 'archived';
  steps: SOPStep[];
}

export default function SOPManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSOP, setExpandedSOP] = useState<string | null>(null);

  const { data: sops, isLoading } = useQuery({
    queryKey: ['sops'],
    queryFn: async () => {
      const res = await api.get('/sops/');
      const d = res.data?.data;
      return (Array.isArray(d) ? d : d?.sops || d?.items || []) as SOP[];
    },
  });

  const list = Array.isArray(sops) ? sops : [];
  const filtered = list.filter(s =>
    (s.title ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.service ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.category ?? '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading && !list.length) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Activity size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading SOPs...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Manager</p>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>SOP Management</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
            {list.length} standard operating procedures &middot; {list.filter(s => s.is_chemical).length} chemical services
          </p>
        </div>
        <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Plus size={16} /> Create New SOP
        </button>
      </div>

      {/* Search */}
      <div style={{ position: 'relative' }}>
        <Search size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        <input
          type="text"
          placeholder="Search SOPs by title, service, or category..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          style={{
            width: '100%', padding: '12px 12px 12px 44px', borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)',
            fontSize: '0.9rem', outline: 'none',
          }}
        />
      </div>

      {/* SOP Table */}
      <div className="card" style={{ padding: 0 }}>
        {/* Table header */}
        <div style={{
          padding: '12px 20px', borderBottom: '1px solid var(--border-subtle)',
          display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 0.7fr 1.5fr 0.5fr',
          gap: 12, fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700,
        }}>
          <span>SOP Title</span>
          <span>Service</span>
          <span>Version</span>
          <span>Steps</span>
          <span>Chemicals</span>
          <span></span>
        </div>

        {filtered.length === 0 ? (
          <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <FileText size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
            <p>No SOPs found</p>
          </div>
        ) : (
          filtered.map((sop, i) => (
            <div key={sop.id}>
              {/* SOP Row */}
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
                style={{
                  padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)',
                  display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 0.7fr 1.5fr 0.5fr',
                  gap: 12, alignItems: 'center', cursor: 'pointer',
                  background: expandedSOP === sop.id ? 'rgba(244,79,154,0.02)' : undefined,
                }}
                onClick={() => setExpandedSOP(expandedSOP === sop.id ? null : sop.id)}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <FileText size={14} style={{ color: 'var(--gold)', flexShrink: 0 }} />
                    {sop.title}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 22 }}>{sop.category}</div>
                </div>
                <span style={{ fontSize: '0.85rem' }}>{sop.service}</span>
                <span className="badge" style={{
                  fontSize: '0.65rem', padding: '2px 8px', fontWeight: 700,
                  background: 'rgba(42,157,143,0.1)', color: 'var(--teal)',
                }}>{sop.version}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{sop.step_count}</span>
                <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                  {sop.chemicals_involved.length > 0 ? (
                    sop.chemicals_involved.slice(0, 2).map(c => (
                      <span key={c} style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(231,111,111,0.08)', color: 'var(--error)', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
                        <Beaker size={8} /> {c}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>None</span>
                  )}
                  {sop.chemicals_involved.length > 2 && (
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>+{sop.chemicals_involved.length - 2}</span>
                  )}
                </div>
                <div style={{ display: 'flex', gap: 4 }}>
                  <button className="btn btn-ghost btn-sm" style={{ padding: 4 }} onClick={e => { e.stopPropagation(); }}>
                    <Eye size={14} />
                  </button>
                  <ChevronDown size={16} style={{
                    color: 'var(--text-muted)', transition: 'transform 0.2s',
                    transform: expandedSOP === sop.id ? 'rotate(180deg)' : 'none',
                  }} />
                </div>
              </motion.div>

              {/* Expanded SOP Detail */}
              <AnimatePresence>
                {expandedSOP === sop.id && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                    style={{ overflow: 'hidden', background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)' }}>
                    <div style={{ padding: '20px 20px 20px 40px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Steps Detail</h4>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          Last updated: {sop.updated_at}
                        </div>
                      </div>

                      {sop.steps.map((step, si) => (
                        <div key={step.step} style={{
                          display: 'flex', gap: 16, padding: '12px 0',
                          borderBottom: si < sop.steps.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                        }}>
                          {/* Step number */}
                          <div style={{
                            width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                            background: step.critical ? 'rgba(231,111,111,0.1)' : 'rgba(244,79,154,0.08)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '0.75rem', fontWeight: 700,
                            color: step.critical ? 'var(--error)' : '#f44f9a',
                          }}>
                            {step.step}
                          </div>

                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                              <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{step.title}</span>
                              {step.critical && <AlertTriangle size={12} style={{ color: 'var(--error)' }} />}
                              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 3 }}>
                                <Clock size={10} /> {step.duration_minutes} min
                              </span>
                            </div>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 6 }}>
                              {step.instructions}
                            </p>

                            {/* SOULSKIN archetype overlays */}
                            {step.archetype_overlays && Object.entries(step.archetype_overlays).length > 0 && (
                              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
                                {Object.entries(step.archetype_overlays).map(([arch, note]) => {
                                  const ad = ARCH_DATA[arch];
                                  if (!ad) return null;
                                  const Icon = ad.icon;
                                  return (
                                    <div key={arch} style={{
                                      padding: '6px 10px', borderRadius: 'var(--radius-md)',
                                      background: `${ad.color}08`, border: `1px solid ${ad.color}15`,
                                      display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem',
                                    }}>
                                      <Icon size={10} color={ad.color} />
                                      <span style={{ color: ad.color, fontWeight: 600 }}>{ad.label}:</span>
                                      <span style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>{note}</span>
                                    </div>
                                  );
                                })}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
