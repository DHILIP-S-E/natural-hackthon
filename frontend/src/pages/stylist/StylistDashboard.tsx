import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar, Clock, CheckCircle, Play, Pause,
  AlertTriangle, Sparkles, Star, BookOpen, Timer, ChevronRight
} from 'lucide-react';
import ArchetypeBadge from '../../components/ArchetypeBadge';
import api from '../../config/api';

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  completed: { color: 'var(--success)', label: 'Done' },
  in_progress: { color: 'var(--warning)', label: 'Active' },
  confirmed: { color: 'var(--teal)', label: 'Upcoming' },
};

export default function StylistDashboard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [timerActive, setTimerActive] = useState(false);
  const [timerValue, setTimerValue] = useState(300);
  const [showSoulskin, setShowSoulskin] = useState(false);

  const { data: bookingsData } = useQuery({
    queryKey: ['bookings', 'today', 'stylist'],
    queryFn: () => api.get('/bookings/today').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.bookings || d?.items || [];
    }),
  });

  const { data: staffData } = useQuery({
    queryKey: ['staff', 'me', 'performance'],
    queryFn: () => api.get('/staff/me/performance').then(r => r.data?.data),
  });

  // Map API bookings to schedule format
  const bookings = Array.isArray(bookingsData) ? bookingsData : [];
  const todaySchedule = bookings.map((b: any) => ({
    time: b.scheduled_time || new Date(b.scheduled_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', hour12: true }),
    customer: b.customer_name || b.customer?.name || 'Unknown',
    service: b.service_name || b.service?.name || 'Service',
    status: b.status || 'confirmed',
    archetype: b.archetype || b.customer?.archetype,
  }));

  // Find the active (in_progress) booking
  const activeBooking = bookings.find((b: any) => b.status === 'in_progress');
  const currentBooking = activeBooking ? {
    customer: activeBooking.customer_name || activeBooking.customer?.name || 'Unknown',
    service: activeBooking.service_name || activeBooking.service?.name || 'Service',
    archetype: activeBooking.archetype || activeBooking.customer?.archetype,
    allergies: activeBooking.allergies || activeBooking.customer?.allergies || [],
    hairType: activeBooking.hair_type || activeBooking.customer?.hair_type || '',
    beautyScore: activeBooking.beauty_score || activeBooking.customer?.beauty_score || 0,
  } : null;

  const sopSteps = activeBooking?.sop_steps || activeBooking?.currentSop || [];
  const soulskinOverlay = activeBooking?.soulskin_overlay || activeBooking?.soulskinOverlay || null;
  const hasActiveSession = currentBooking !== null && sopSteps.length > 0;

  // Derive performance stats from bookings or use API staff data
  const performanceStats = staffData || {
    completed: bookings.filter((b: any) => b.status === 'completed').length,
    active: bookings.filter((b: any) => b.status === 'in_progress').length,
    upcoming: bookings.filter((b: any) => b.status === 'confirmed').length,
    rating: 0,
  };

  const step = hasActiveSession ? sopSteps[currentStep - 1] : null;
  const progress = hasActiveSession ? ((currentStep - 1) / sopSteps.length) * 100 : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem' }}>Stylist Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            {performanceStats.completed} completed, {performanceStats.active} active, {performanceStats.upcoming} upcoming
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <span className="badge badge-success">On Floor</span>
          <span className="badge badge-violet">{'\u2728'} SOULSKIN Certified</span>
        </div>
      </div>

      {/* Main grid: SOP guidance + Schedule */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-lg)' }}>
        {/* LIVE SOP GUIDANCE */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {hasActiveSession && currentBooking && step ? (
            <>
              {/* Current client header */}
              <div style={{ padding: '16px 20px', background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--bg-card)', border: '2px solid var(--gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', color: 'var(--gold)' }}>
                    {(currentBooking.customer ?? '').split(' ').map((n: string) => n[0]).join('')}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                      {currentBooking.customer} {currentBooking.archetype && <ArchetypeBadge archetype={currentBooking.archetype} size="sm" />}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {currentBooking.service}{currentBooking.hairType ? ` \u00B7 ${currentBooking.hairType} hair` : ''}{currentBooking.beautyScore ? ` \u00B7 Score: ${currentBooking.beautyScore}` : ''}
                    </div>
                  </div>
                </div>
                {currentBooking.allergies?.length > 0 && (
                  <span className="badge badge-rose" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <AlertTriangle size={12} /> {currentBooking.allergies[0]} Allergy
                  </span>
                )}
              </div>

              {/* Progress bar */}
              <div style={{ padding: '0 20px', marginTop: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>
                  <span>Step {currentStep} of {sopSteps.length}</span>
                  <span>{Math.round(progress)}% complete</span>
                </div>
                <div style={{ height: 4, background: 'var(--border-subtle)', borderRadius: 2 }}>
                  <motion.div animate={{ width: `${progress}%` }} style={{ height: '100%', background: 'var(--gold)', borderRadius: 2 }} />
                </div>
              </div>

              {/* Step cards */}
              <div style={{ padding: '16px 20px' }}>
                <AnimatePresence mode="wait">
                  <motion.div key={currentStep} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
                    style={{ background: step.critical ? 'rgba(231,111,111,0.04)' : 'var(--bg-surface)', border: `1px solid ${step.critical ? 'var(--rose)' : 'var(--border-subtle)'}`, borderRadius: 'var(--radius-lg)', padding: 20 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {step.critical && <AlertTriangle size={16} style={{ color: 'var(--rose)' }} />}
                        Step {step.step}: {step.title}
                      </h4>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Clock size={12} /> {step.duration} min
                      </span>
                    </div>

                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.6 }}>{step.instructions}</p>

                    {step.warning && (
                      <div style={{ background: 'rgba(231,111,111,0.1)', border: '1px solid var(--rose)', borderRadius: 'var(--radius-md)', padding: '8px 12px', marginBottom: 12, fontSize: '0.8rem', color: 'var(--rose)', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <AlertTriangle size={14} /> {step.warning}
                      </div>
                    )}

                    {step.products && (
                      <div style={{ marginBottom: 12 }}>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Products needed:</span>
                        <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                          {step.products.map((p: string) => <span key={p} className="badge badge-teal" style={{ padding: '2px 8px' }}>{p}</span>)}
                        </div>
                      </div>
                    )}

                    {step.timer && (
                      <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', padding: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <Timer size={20} style={{ color: timerActive ? 'var(--warning)' : 'var(--text-muted)' }} />
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '1.5rem', fontWeight: 700, color: timerActive ? 'var(--warning)' : 'var(--text-secondary)' }}>
                            {Math.floor(timerValue / 60)}:{String(timerValue % 60).padStart(2, '0')}
                          </span>
                        </div>
                        <button className={`btn ${timerActive ? 'btn-ghost' : 'btn-teal'} btn-sm`}
                          onClick={() => setTimerActive(!timerActive)}>
                          {timerActive ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Start</>}
                        </button>
                      </div>
                    )}

                    <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                      {currentStep > 1 && <button className="btn btn-ghost btn-sm" onClick={() => { setCurrentStep(s => s - 1); setTimerActive(false); setTimerValue(sopSteps[currentStep - 2]?.timerSeconds || 300); }}>Back</button>}
                      <button className="btn btn-primary btn-sm" onClick={() => { if (currentStep < sopSteps.length) { setCurrentStep(s => s + 1); setTimerActive(false); setTimerValue(sopSteps[currentStep]?.timerSeconds || 300); } }}>
                        {currentStep === sopSteps.length ? <><CheckCircle size={14} /> Complete</> : <>Next Step <ChevronRight size={14} /></>}
                      </button>
                    </div>
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Step navigation dots */}
              <div style={{ padding: '0 20px 16px', display: 'flex', gap: 6, justifyContent: 'center' }}>
                {sopSteps.map((_s: any, i: number) => (
                  <button key={i} onClick={() => setCurrentStep(i + 1)}
                    style={{ width: i + 1 === currentStep ? 24 : 8, height: 8, borderRadius: 4, border: 'none', cursor: 'pointer', background: i + 1 < currentStep ? 'var(--success)' : i + 1 === currentStep ? 'var(--gold)' : 'var(--border-medium)', transition: 'all 0.2s' }} />
                ))}
              </div>

              {/* SOULSKIN overlay toggle */}
              {soulskinOverlay && (
                <div style={{ borderTop: '1px solid var(--border-subtle)', padding: '16px 20px' }}>
                  <button className="btn btn-ghost" style={{ width: '100%', justifyContent: 'space-between', color: 'var(--violet)' }}
                    onClick={() => setShowSoulskin(!showSoulskin)}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Sparkles size={16} /> SOULSKIN Guidance{soulskinOverlay.archetype ? ` \u2014 ${soulskinOverlay.archetype.toUpperCase()}` : ''}
                    </span>
                    <ChevronRight size={16} style={{ transform: showSoulskin ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }} />
                  </button>

                  <AnimatePresence>
                    {showSoulskin && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                        style={{ overflow: 'hidden', marginTop: 12 }}>
                        <div style={{ background: 'rgba(155,127,212,0.05)', border: '1px solid rgba(155,127,212,0.2)', borderRadius: 'var(--radius-lg)', padding: 16 }}>
                          <p style={{ fontSize: '0.85rem', color: 'var(--violet)', fontStyle: 'italic', marginBottom: 16 }}>"{soulskinOverlay.note}"</p>

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>{'\uD83C\uDF3F'} Aromatherapy</div>
                              <div style={{ fontSize: '0.8rem' }}>{soulskinOverlay.sensory?.aroma}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>{'\uD83D\uDCA1'} Lighting</div>
                              <div style={{ fontSize: '0.8rem' }}>{soulskinOverlay.sensory?.lighting}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>{'\uD83C\uDFB5'} Music Arc</div>
                              <div style={{ fontSize: '0.8rem' }}>{soulskinOverlay.sensory?.music}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>{'\u270B'} Touch</div>
                              <div style={{ fontSize: '0.8rem' }}>{soulskinOverlay.touch?.pressure} pressure</div>
                            </div>
                          </div>

                          {soulskinOverlay.script && (
                            <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', padding: 12 }}>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>{'\uD83D\uDCAC'} Say This:</div>
                              <p style={{ fontSize: '0.8rem', fontStyle: 'italic', color: 'var(--text-secondary)' }}>"{soulskinOverlay.script.opening}"</p>
                              {soulskinOverlay.script.doNotSay?.length > 0 && (
                                <div style={{ fontSize: '0.7rem', color: 'var(--rose)', marginTop: 8 }}>
                                  {'\u274C'} Don't say: {soulskinOverlay.script.doNotSay.join(' \u00B7 ')}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </>
          ) : (
            <div style={{ padding: '48px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
              <BookOpen size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
              <h4 style={{ marginBottom: 8, fontWeight: 600, color: 'var(--text-secondary)' }}>No Active Session</h4>
              <p style={{ fontSize: '0.85rem' }}>SOP guidance will appear here when you start a booking.</p>
            </div>
          )}
        </div>

        {/* TODAY'S SCHEDULE */}
        <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Calendar size={18} /> Today's Schedule</h4>
          </div>
          <div style={{ flex: 1 }}>
            {todaySchedule.length === 0 ? (
              <div style={{ padding: '32px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                <Calendar size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
                <p style={{ fontSize: '0.85rem' }}>No bookings scheduled for today.</p>
              </div>
            ) : (
              todaySchedule.map((s: any, i: number) => {
                const st = STATUS_MAP[s.status] || { color: 'var(--text-muted)', label: s.status };
                return (
                  <div key={i} style={{
                    padding: '12px 20px', borderBottom: '1px solid var(--border-subtle)',
                    background: s.status === 'in_progress' ? 'rgba(201,169,110,0.04)' : 'transparent',
                    borderLeft: s.status === 'in_progress' ? '3px solid var(--gold)' : '3px solid transparent',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.time}</span>
                      <span style={{ fontSize: '0.65rem', fontWeight: 600, color: st.color }}>{st.label}</span>
                    </div>
                    <div style={{ marginTop: 4 }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6 }}>
                        {s.customer}
                        {s.archetype && <ArchetypeBadge archetype={s.archetype} size="sm" showLabel={false} />}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{s.service}</div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Stats */}
          <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-surface)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <div><span style={{ color: 'var(--success)', fontWeight: 600 }}>{performanceStats.completed}</span> <span style={{ color: 'var(--text-muted)' }}>done</span></div>
              <div><span style={{ color: 'var(--warning)', fontWeight: 600 }}>{performanceStats.active}</span> <span style={{ color: 'var(--text-muted)' }}>active</span></div>
              <div><span style={{ color: 'var(--teal)', fontWeight: 600 }}>{performanceStats.upcoming}</span> <span style={{ color: 'var(--text-muted)' }}>upcoming</span></div>
              {performanceStats.rating > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Star size={12} style={{ color: 'var(--gold)' }} /><span style={{ fontWeight: 600 }}>{performanceStats.rating}</span></div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
