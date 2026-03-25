import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft, CheckCircle, AlertTriangle, Clock, Camera,
  Sparkles, MessageCircle, X, Beaker, Play, Pause, Award, FileText, Activity
} from 'lucide-react';
import api from '../../config/api';
import ArchetypeBadge from '../../components/ArchetypeBadge';
import { ARCH_DATA } from '../../constants/archetypes';
import type { Archetype } from '../../types';

interface StepData {
  step: number;
  title: string;
  instructions: string;
  duration_minutes: number;
  critical: boolean;
  warning?: string;
  products?: string[];
  ai_coaching?: string;
  photo_prompt?: boolean;
}

const DEFAULT_SESSION = {
  id: '',
  booking_id: '',
  customer: { name: 'Customer', initials: 'C', beautyScore: 0, allergies: [] as string[], archetype: null as Archetype | null },
  service: { name: 'Service', duration: 0 },
  soulskin_active: false,
  archetype_applied: null as Archetype | null,
  soulskin_script: { opening: '', mid: '', closing: '' },
  soulskin_sensory: { aroma: '', lighting: '', music: '' },
};

function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) return `${hrs}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  return `${mins}:${String(secs).padStart(2, '0')}`;
}

export default function LiveSession() {
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [sessionTimer, setSessionTimer] = useState(0);
  const [sessionActive, setSessionActive] = useState(true);
  const [showDeviationModal, setShowDeviationModal] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [deviationNote, setDeviationNote] = useState('');
  const [showPhotoPrompt, setShowPhotoPrompt] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Session timer
  useEffect(() => {
    if (sessionActive) {
      timerRef.current = setInterval(() => {
        setSessionTimer(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [sessionActive]);

  const { data: sessionData } = useQuery({
    queryKey: ['live-session'],
    queryFn: async () => {
      const res = await api.get('/sessions/active');
      return res.data?.data;
    },
    retry: false,
  });

  const session = sessionData ?? DEFAULT_SESSION;
  const sopSteps: StepData[] = session.sop_steps || sessionData?.sop_steps || [];
  const step = sopSteps[currentStep - 1];
  const totalSteps = sopSteps.length;
  const archData = session.archetype_applied ? ARCH_DATA[session.archetype_applied] : null;
  const ArchIcon = archData?.icon;

  const handleMarkComplete = useCallback(() => {
    if (!completedSteps.includes(currentStep)) {
      setCompletedSteps(prev => [...prev, currentStep]);
    }
    // Check for photo prompt on first and last steps
    if (step.photo_prompt) {
      setShowPhotoPrompt(true);
      return;
    }
    if (currentStep < totalSteps) {
      setCurrentStep(prev => prev + 1);
    } else {
      setShowCompleteModal(true);
      setSessionActive(false);
    }
  }, [currentStep, completedSteps, step, totalSteps]);

  const handlePhotoCaptureDone = useCallback(() => {
    setShowPhotoPrompt(false);
    if (currentStep < totalSteps) {
      setCurrentStep(prev => prev + 1);
    } else {
      setShowCompleteModal(true);
      setSessionActive(false);
    }
  }, [currentStep, totalSteps]);

  const handlePrevious = useCallback(() => {
    if (currentStep > 1) setCurrentStep(prev => prev - 1);
  }, [currentStep]);

  const handleLogDeviation = useCallback(() => {
    setShowDeviationModal(true);
  }, []);

  const submitDeviation = useCallback(() => {
    // In production, this would call api.post('/sessions/{id}/deviations', ...)
    setDeviationNote('');
    setShowDeviationModal(false);
  }, []);

  if (!step || totalSteps === 0) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--bg-void)' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Activity size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading session...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg-void)', position: 'relative' }}>
      {/* FIXED HEADER */}
      <div style={{
        padding: '12px 24px', background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0, zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {/* Customer avatar */}
          <div style={{
            width: 40, height: 40, borderRadius: '50%', background: 'var(--bg-card)',
            border: '2px solid var(--gold)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 700, fontSize: '0.85rem', color: 'var(--gold)',
          }}>
            {session.customer?.initials ?? 'C'}
          </div>
          <div>
            <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
              {session.customer?.name ?? 'Customer'}
              {session.soulskin_active && session.archetype_applied && (
                <ArchetypeBadge archetype={session.archetype_applied} size="sm" />
              )}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {session.service?.name ?? 'Service'} &middot; Score: {session.customer?.beautyScore ?? '-'}
            </div>
          </div>
          {/* Allergy warning */}
          {(session.customer?.allergies ?? []).length > 0 && (
            <span className="badge badge-rose" style={{ display: 'flex', alignItems: 'center', gap: 4, marginLeft: 8 }}>
              <AlertTriangle size={12} /> {session.customer.allergies.join(', ')}
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          {/* Step counter */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Step</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1.1rem' }}>
              {currentStep} / {totalSteps}
            </div>
          </div>
          {/* Session timer */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Timer</div>
            <div style={{
              fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1.1rem',
              color: sessionActive ? 'var(--success)' : 'var(--text-muted)',
              display: 'flex', alignItems: 'center', gap: 6,
            }}>
              <Clock size={14} /> {formatTime(sessionTimer)}
            </div>
          </div>
          {/* Pause/resume */}
          <button className={`btn ${sessionActive ? 'btn-ghost' : 'btn-teal'} btn-sm`}
            onClick={() => setSessionActive(!sessionActive)}>
            {sessionActive ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Resume</>}
          </button>
        </div>
      </div>

      {/* PROGRESS BAR */}
      <div style={{ height: 4, background: 'var(--border-subtle)', flexShrink: 0 }}>
        <motion.div
          animate={{ width: `${(completedSteps.length / totalSteps) * 100}%` }}
          style={{ height: '100%', background: 'var(--gold)', transition: 'width 0.3s ease' }}
        />
      </div>

      {/* MAIN CONTENT */}
      <div style={{ flex: 1, overflow: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
        {/* Step navigation dots */}
        <div style={{ display: 'flex', gap: 6, justifyContent: 'center' }}>
          {sopSteps.map((_s, i) => (
            <button key={i} onClick={() => setCurrentStep(i + 1)}
              style={{
                width: i + 1 === currentStep ? 28 : 10, height: 10, borderRadius: 5, border: 'none', cursor: 'pointer',
                background: completedSteps.includes(i + 1) ? 'var(--success)' : i + 1 === currentStep ? '#f44f9a' : 'var(--border-medium)',
                transition: 'all 0.2s',
              }} />
          ))}
        </div>

        {/* Current Step Card */}
        <AnimatePresence mode="wait">
          <motion.div key={currentStep} initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -40 }} transition={{ duration: 0.25 }}>
            <div className="card" style={{
              padding: '32px', maxWidth: 700, margin: '0 auto', width: '100%',
              border: step.critical ? '1px solid rgba(231,111,111,0.3)' : undefined,
              background: step.critical ? 'rgba(231,111,111,0.02)' : undefined,
            }}>
              {/* Step number + title */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: '50%',
                  background: step.critical ? 'rgba(231,111,111,0.1)' : 'rgba(244,79,154,0.1)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.1rem', fontWeight: 700,
                  color: step.critical ? 'var(--error)' : '#f44f9a',
                }}>
                  {step.step}
                </div>
                <div style={{ flex: 1 }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                    {step.critical && <AlertTriangle size={18} style={{ color: 'var(--error)' }} />}
                    {step.title}
                  </h2>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                    <Clock size={12} /> {step.duration_minutes} minutes
                    {step.critical && <span className="badge badge-rose" style={{ fontSize: '0.6rem', padding: '2px 6px', marginLeft: 4 }}>Critical</span>}
                  </div>
                </div>
              </div>

              {/* Warning */}
              {step.warning && (
                <div style={{
                  background: 'rgba(231,111,111,0.08)', border: '1px solid rgba(231,111,111,0.2)',
                  borderRadius: 'var(--radius-md)', padding: '12px 16px', marginBottom: 16,
                  fontSize: '0.85rem', color: 'var(--error)', display: 'flex', alignItems: 'center', gap: 10, fontWeight: 500,
                }}>
                  <AlertTriangle size={16} style={{ flexShrink: 0 }} /> {step.warning}
                </div>
              )}

              {/* Instructions */}
              <div style={{ marginBottom: 20 }}>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>{step.instructions}</p>
              </div>

              {/* Products needed */}
              {step.products && step.products.length > 0 && (
                <div style={{ marginBottom: 20, padding: '14px 16px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                    <Beaker size={12} /> Products Needed
                  </div>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {step.products.map(p => (
                      <span key={p} className="badge badge-teal" style={{ padding: '4px 10px', fontWeight: 600 }}>{p}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Coaching Bubble */}
              {step.ai_coaching && (
                <div style={{
                  padding: '16px', borderRadius: 'var(--radius-lg)',
                  background: 'linear-gradient(135deg, rgba(155,127,212,0.06), rgba(244,79,154,0.06))',
                  border: '1px solid rgba(155,127,212,0.15)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'rgba(155,127,212,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <MessageCircle size={12} color="#9B7FD4" />
                    </div>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#9B7FD4', textTransform: 'uppercase', letterSpacing: '0.06em' }}>AI Coaching</span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontStyle: 'italic' }}>
                    "{step.ai_coaching}"
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* SOULSKIN quick info (if active) */}
        {session.soulskin_active && archData && ArchIcon && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            style={{
              maxWidth: 700, margin: '0 auto', width: '100%', padding: '16px 20px',
              borderRadius: 'var(--radius-lg)',
              background: `linear-gradient(135deg, ${archData.color}08, ${archData.color}12)`,
              border: `1px solid ${archData.color}20`,
              display: 'flex', alignItems: 'center', gap: 16,
            }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: `${archData.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArchIcon size={18} color={archData.color} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: archData.color, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                SOULSKIN: {archData.label}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                Sensory: {session.soulskin_sensory?.aroma} &middot; {session.soulskin_sensory?.lighting}
              </div>
            </div>
            <Sparkles size={16} color={archData.color} />
          </motion.div>
        )}
      </div>

      {/* FIXED BOTTOM ACTION BAR */}
      <div style={{
        padding: '16px 24px', background: 'var(--bg-surface)', borderTop: '1px solid var(--border-subtle)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0, zIndex: 10,
      }}>
        <button className="btn btn-ghost" onClick={handlePrevious} disabled={currentStep <= 1}
          style={{ opacity: currentStep <= 1 ? 0.4 : 1, display: 'flex', alignItems: 'center', gap: 6 }}>
          <ChevronLeft size={18} /> Previous
        </button>

        <button className="btn btn-teal btn-lg" onClick={handleMarkComplete}
          style={{ minWidth: 200, fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
          <CheckCircle size={20} />
          {currentStep === totalSteps ? 'Complete Session' : 'Mark Complete'}
        </button>

        <button className="btn" onClick={handleLogDeviation}
          style={{ background: 'rgba(244,162,97,0.1)', color: 'var(--warning)', border: '1px solid rgba(244,162,97,0.3)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <FileText size={16} /> Log Deviation
        </button>
      </div>

      {/* PHOTO CAPTURE PROMPT MODAL */}
      <AnimatePresence>
        {showPhotoPrompt && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
              className="card" style={{ padding: '32px', maxWidth: 400, textAlign: 'center' }}>
              <Camera size={48} style={{ color: '#f44f9a', marginBottom: 16 }} />
              <h3 style={{ marginBottom: 8 }}>
                {currentStep === 1 ? 'Capture Before Photo' : 'Capture After Photo'}
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 24, lineHeight: 1.5 }}>
                {currentStep === 1
                  ? 'Take a baseline photo of the customer before the service begins for comparison.'
                  : 'Capture the final result to add to the customer\'s beauty passport.'}
              </p>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                <button className="btn btn-ghost" onClick={handlePhotoCaptureDone}>Skip</button>
                <button className="btn btn-primary" onClick={handlePhotoCaptureDone} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Camera size={16} /> Capture Photo
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* DEVIATION MODAL */}
      <AnimatePresence>
        {showDeviationModal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
              className="card" style={{ padding: '32px', maxWidth: 460 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <AlertTriangle size={20} style={{ color: 'var(--warning)' }} /> Log Deviation
                </h3>
                <button className="btn btn-ghost btn-sm" onClick={() => setShowDeviationModal(false)}>
                  <X size={16} />
                </button>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 16 }}>
                Record any deviation from the SOP at Step {currentStep}: {step.title}
              </p>
              <textarea
                value={deviationNote}
                onChange={e => setDeviationNote(e.target.value)}
                placeholder="Describe what was different and why..."
                style={{
                  width: '100%', minHeight: 100, padding: '12px', borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)',
                  fontSize: '0.85rem', resize: 'vertical', fontFamily: 'inherit',
                }}
              />
              <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 16 }}>
                <button className="btn btn-ghost" onClick={() => setShowDeviationModal(false)}>Cancel</button>
                <button className="btn" onClick={submitDeviation}
                  style={{ background: 'var(--warning)', color: '#fff', border: 'none' }}>
                  Save Deviation
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* SESSION COMPLETE MODAL */}
      <AnimatePresence>
        {showCompleteModal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.8, opacity: 0 }}
              className="card" style={{ padding: '48px', maxWidth: 480, textAlign: 'center' }}>
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}>
                <Award size={64} style={{ color: 'var(--gold)', marginBottom: 20 }} />
              </motion.div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8 }}>Session Complete!</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 24, lineHeight: 1.6 }}>
                {session.service?.name} for {session.customer?.name} completed successfully in {formatTime(sessionTimer)}.
              </p>
              <div style={{ display: 'flex', justifyContent: 'center', gap: 24, marginBottom: 32 }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1.25rem', color: 'var(--success)' }}>{completedSteps.length}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Steps Done</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1.25rem' }}>{formatTime(sessionTimer)}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Duration</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1.25rem', color: 'var(--success)' }}>
                    {Math.round((completedSteps.length / totalSteps) * 100)}%
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>SOP Compliance</div>
                </div>
              </div>
              {session.soulskin_active && archData && (
                <div style={{
                  padding: '12px 16px', borderRadius: 'var(--radius-md)',
                  background: `${archData.color}10`, border: `1px solid ${archData.color}25`,
                  marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                }}>
                  <Sparkles size={14} color={archData.color} />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: archData.color }}>SOULSKIN {archData.label} session recorded</span>
                </div>
              )}
              <button className="btn btn-primary btn-lg" onClick={() => setShowCompleteModal(false)} style={{ width: '100%' }}>
                Return to Dashboard
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
