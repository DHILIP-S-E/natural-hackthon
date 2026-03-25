import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  BookOpen, Award, Download, Clock, Star, CheckCircle,
  Lock, Sparkles, Target, Activity, Trophy
} from 'lucide-react';
import api from '../../config/api';

type SkillLevel = 'L1' | 'L2' | 'L3';

interface TrainingModule {
  id: string;
  name: string;
  type: string;
  level: SkillLevel;
  duration_hours: number;
  status: 'completed' | 'in_progress' | 'available' | 'locked';
  progress?: number;
  score?: number;
  certificate_url?: string;
  completed_date?: string;
  includes_soulskin: boolean;
}

const LEVEL_COLORS: Record<SkillLevel, string> = { L1: 'var(--teal)', L2: 'var(--gold)', L3: '#f44f9a' };


export default function StylistTraining() {
  const [showAllCompleted, setShowAllCompleted] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['stylist-training'],
    queryFn: async () => {
      const res = await api.get('/stylists/me/training');
      return res.data.data;
    },
    retry: false,
  });

  const learningPath: { level: SkillLevel; label: string; modules: number; completed: number }[] = data?.learning_path ?? [
    { level: 'L1', label: 'Foundation', modules: 0, completed: 0 },
    { level: 'L2', label: 'Advanced', modules: 0, completed: 0 },
    { level: 'L3', label: 'Expert', modules: 0, completed: 0 },
  ];
  const completedTrainings: TrainingModule[] = data?.completed ?? [];
  const availableCourses: TrainingModule[] = data?.available ?? [];
  const soulskinScore: number | null = data?.soulskin_score ?? null;
  const stylistName: string = data?.stylist_name ?? '';
  const stylistLevel: string = data?.current_level ?? '';
  const hasSoulskin: boolean = completedTrainings.some(t => t.includes_soulskin);

  const completedList = showAllCompleted ? completedTrainings : completedTrainings.slice(0, 5);
  const totalHours = completedTrainings.reduce((sum, t) => sum + t.duration_hours, 0);
  const avgScore = completedTrainings.length > 0 ? Math.round(completedTrainings.reduce((sum, t) => sum + (t.score ?? 0), 0) / completedTrainings.length) : 0;

  if (isLoading && !data) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Activity size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
          <p>Loading training data...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Training</p>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>My Learning Path</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
            {stylistName || 'My Training'}{stylistLevel ? ` \u00B7 Level ${stylistLevel}` : ''}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <span className="badge badge-success" style={{ fontWeight: 600 }}>{completedTrainings.length} Completed</span>
          {hasSoulskin && <span className="badge badge-violet" style={{ fontWeight: 600 }}>SOULSKIN Certified</span>}
        </div>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Courses Done', value: String(completedTrainings.length), icon: <CheckCircle size={16} />, color: 'var(--success)' },
          { label: 'Total Hours', value: String(totalHours), icon: <Clock size={16} />, color: 'var(--teal)' },
          { label: 'Avg Score', value: `${avgScore}%`, icon: <Star size={16} />, color: 'var(--gold)' },
          { label: 'Current Level', value: stylistLevel || '-', icon: <Trophy size={16} />, color: '#f44f9a' },
        ].map((k, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${k.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: k.color }}>{k.icon}<span className="kpi-label">{k.label}</span></div>
            <span className="kpi-value" style={{ fontSize: '1.3rem' }}>{k.value}</span>
          </motion.div>
        ))}
      </div>

      {/* Learning Path Visualization */}
      <div className="card" style={{ padding: '24px' }}>
        <h4 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Target size={16} style={{ color: '#f44f9a' }} /> Learning Path
        </h4>
        <div style={{ display: 'flex', gap: 0, alignItems: 'center' }}>
          {learningPath.map((level, i) => {
            const pct = level.modules > 0 ? Math.round((level.completed / level.modules) * 100) : 0;
            const isComplete = pct === 100;
            const isCurrent = pct > 0 && pct < 100;
            return (
              <div key={level.level} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
                {/* Connector */}
                {i > 0 && (
                  <div style={{
                    position: 'absolute', left: -50, top: 24, width: 100, height: 3,
                    background: learningPath[i - 1].completed === learningPath[i - 1].modules ? LEVEL_COLORS[level.level] : 'var(--border-subtle)',
                    zIndex: 0,
                  }} />
                )}
                {/* Circle */}
                <motion.div initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ delay: i * 0.15 }}
                  style={{
                    width: 48, height: 48, borderRadius: '50%', zIndex: 1,
                    background: isComplete ? LEVEL_COLORS[level.level] : isCurrent ? 'var(--bg-surface)' : 'var(--bg-surface)',
                    border: `3px solid ${isComplete ? LEVEL_COLORS[level.level] : isCurrent ? LEVEL_COLORS[level.level] : 'var(--border-medium)'}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: isComplete ? '#fff' : isCurrent ? LEVEL_COLORS[level.level] : 'var(--text-muted)',
                    fontWeight: 700, fontSize: '0.85rem',
                  }}>
                  {isComplete ? <CheckCircle size={20} /> : level.level}
                </motion.div>
                <div style={{ marginTop: 8, textAlign: 'center' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.8rem', color: isCurrent ? LEVEL_COLORS[level.level] : 'var(--text-primary)' }}>{level.label}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{level.completed}/{level.modules} modules</div>
                  {isCurrent && (
                    <div style={{ marginTop: 6, height: 4, width: 80, background: 'var(--border-subtle)', borderRadius: 2, margin: '6px auto 0' }}>
                      <div style={{ width: `${pct}%`, height: '100%', background: LEVEL_COLORS[level.level], borderRadius: 2 }} />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* SOULSKIN Certification Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        style={{
          padding: '28px', borderRadius: 'var(--radius-lg)',
          background: 'linear-gradient(135deg, rgba(155,127,212,0.08), rgba(123,104,200,0.15))',
          border: '1px solid rgba(155,127,212,0.25)',
        }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 'var(--radius-lg)',
            background: 'rgba(155,127,212,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Sparkles size={28} color="#9B7FD4" />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#9B7FD4', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
              SOULSKIN Certification Program
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 4 }}>Certified SOULSKIN Coach</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              Master the art of emotional archetype mapping and soul-aligned beauty experiences. Integrate SOULSKIN into every service.
            </p>
          </div>
          <div style={{ textAlign: 'center', minWidth: 80 }}>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: '#9B7FD4', fontFamily: 'var(--font-mono)' }}>{soulskinScore != null ? `${soulskinScore}%` : '-'}</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Your Score</div>
            <CheckCircle size={16} style={{ color: 'var(--success)', marginTop: 4 }} />
          </div>
        </div>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 'var(--space-lg)' }}>
        {/* Completed Trainings */}
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Award size={16} /> Completed Trainings
            </h4>
            <span className="badge badge-success" style={{ fontWeight: 600 }}>{completedTrainings.length} certificates</span>
          </div>
          {/* Table-like list */}
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', padding: '8px 20px', display: 'grid', gridTemplateColumns: '2fr 1fr 0.5fr 0.5fr 0.5fr', gap: 8, borderBottom: '1px solid var(--border-subtle)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            <span>Course</span><span>Type</span><span>Level</span><span>Score</span><span></span>
          </div>
          {completedList.map((t, i) => (
            <motion.div key={t.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
              style={{ padding: '10px 20px', display: 'grid', gridTemplateColumns: '2fr 1fr 0.5fr 0.5fr 0.5fr', gap: 8, alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', fontSize: '0.8rem' }}>
              <div>
                <span style={{ fontWeight: 500 }}>{t.name}</span>
                {t.includes_soulskin && <Sparkles size={10} style={{ color: '#9B7FD4', marginLeft: 6 }} />}
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{t.completed_date} &middot; {t.duration_hours}h</div>
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.type}</span>
              <span className="badge" style={{
                fontSize: '0.6rem', padding: '2px 6px', fontWeight: 700,
                background: `${LEVEL_COLORS[t.level]}15`, color: LEVEL_COLORS[t.level],
              }}>{t.level}</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: (t.score ?? 0) >= 90 ? 'var(--success)' : 'var(--text-primary)' }}>{t.score}%</span>
              <button className="btn btn-ghost btn-sm" style={{ padding: 4 }} title="Download Certificate">
                <Download size={14} />
              </button>
            </motion.div>
          ))}
          {completedTrainings.length > 5 && (
            <div style={{ padding: '12px 20px', textAlign: 'center' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowAllCompleted(!showAllCompleted)}>
                {showAllCompleted ? 'Show Less' : `Show All ${completedTrainings.length} Courses`}
              </button>
            </div>
          )}
        </div>

        {/* Available Courses */}
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <BookOpen size={16} /> Available Courses
            </h4>
          </div>
          {availableCourses.map((course, i) => {
            const isLocked = course.status === 'locked';
            const isInProgress = course.status === 'in_progress';
            return (
              <motion.div key={course.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}
                style={{
                  padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)',
                  opacity: isLocked ? 0.5 : 1,
                }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {isLocked ? <Lock size={14} style={{ color: 'var(--text-muted)' }} /> : <BookOpen size={14} style={{ color: LEVEL_COLORS[course.level] }} />}
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{course.name}</span>
                  </div>
                  <span className="badge" style={{
                    fontSize: '0.6rem', padding: '2px 6px', fontWeight: 700,
                    background: `${LEVEL_COLORS[course.level]}15`, color: LEVEL_COLORS[course.level],
                  }}>{course.level}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {course.type} &middot; {course.duration_hours} hours
                  </span>
                  {isInProgress && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 60, height: 4, background: 'var(--border-subtle)', borderRadius: 2 }}>
                        <div style={{ width: `${course.progress}%`, height: '100%', background: LEVEL_COLORS[course.level], borderRadius: 2 }} />
                      </div>
                      <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: LEVEL_COLORS[course.level] }}>{course.progress}%</span>
                    </div>
                  )}
                  {!isLocked && !isInProgress && (
                    <button className="btn btn-teal btn-sm">Enroll</button>
                  )}
                  {isLocked && (
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Complete L2 first</span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
