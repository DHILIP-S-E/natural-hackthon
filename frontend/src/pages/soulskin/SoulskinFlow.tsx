import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Heart, ArrowRight, Music, Palette, MessageSquare, ChevronRight } from 'lucide-react';
import ArchetypeBadge from '../../components/ArchetypeBadge';
import type { Archetype } from '../../types';
import { ARCHETYPES } from '../../types';
import api from '../../config/api';

const QUESTIONS = [
  { key: 'song', emoji: '\uD83C\uDFB5', question: 'What song describes your life right now?', placeholder: 'e.g. Kesariya, Shape of You, Numb...', icon: <Music size={24} /> },
  { key: 'colour', emoji: '\uD83C\uDFA8', question: 'What colour matches your mood today?', placeholder: 'e.g. Gold, Grey, Red, Blue...', icon: <Palette size={24} /> },
  { key: 'word', emoji: '\uD83D\uDCAC', question: 'One word you want to FEEL when you leave?', placeholder: 'e.g. Free, Bold, Peace, Alive...', icon: <MessageSquare size={24} /> },
];

const READINGS: Record<Archetype, {
  reading: string;
  reason: string;
  protocol: { primary: string; why: string };
  sensory: { aroma: string; lighting: string; music: string };
  script: { opening: string; closing: string };
  monologue: string;
}> = {
  phoenix: {
    reading: "You are standing at the edge of something ending. You are not afraid of the fire. You are ready to rise \u2014 remade, brighter, unstoppable.",
    reason: "Bold colours and fierce energy \u2014 that's the Phoenix. Transformation through fire.",
    protocol: { primary: 'Bold Hair Color \u2014 Vivid copper or fiery red', why: 'Phoenix needs outward transformation. Visible. Dramatic.' },
    sensory: { aroma: 'Black Pepper + Patchouli', lighting: 'Warm amber 2700K rising to bright 5000K', music: 'Cinematic build \u2192 Empowerment anthems' },
    script: { opening: "Red. Bold. You know exactly what you want.", closing: "That's not just colour. That's courage made visible." },
    monologue: "Look at yourself. This is what it looks like when someone rises from the fire.",
  },
  river: {
    reading: "You are in flow. Something is shifting inside you \u2014 not dramatic, but deep. Like a river changing course.",
    reason: "Blue tones and fluid energy \u2014 the River. Change through steady movement.",
    protocol: { primary: 'Balayage with cool-tone highlights', why: 'River needs subtle shift. Natural. Flowing.' },
    sensory: { aroma: 'Eucalyptus + Lavender', lighting: 'Cool blue-white 4000K \u2192 Warm 3000K', music: 'Acoustic flow \u2192 Ambient' },
    script: { opening: "Something is shifting for you. Let's let that come through today.", closing: "That transition in your hair? It mirrors the one inside you." },
    monologue: "You came in as one version of you. You're leaving as the next.",
  },
  moon: {
    reading: "You are in a quiet phase. You need softness and gentle reflection. The moon doesn't roar \u2014 it glows.",
    reason: "Soft tones and introspective energy \u2014 the Moon. Rest. Gentle care.",
    protocol: { primary: 'Gentle scalp treatment + nourishing mask', why: 'Moon needs care, not change. Softness. Silence.' },
    sensory: { aroma: 'Chamomile + Vanilla', lighting: 'Dim warm 2200K throughout', music: 'Silence or soft piano' },
    script: { opening: "Let's just make this a quiet, healing time for you.", closing: "You came in needing softness. I hope you found it." },
    monologue: "Sometimes the bravest thing is to be still.",
  },
  bloom: {
    reading: "You are in full bloom. Something new is opening inside you \u2014 a celebration, a beginning, a joy that has been waiting.",
    reason: "Gold and warm energy \u2014 the Bloom. Growth. Joy. Celebration.",
    protocol: { primary: 'Balayage with honey gold highlights', why: 'Bloom needs warmth and light. Celebratory.' },
    sensory: { aroma: 'Bergamot + Cedarwood', lighting: 'Warm amber 2700K \u2192 Natural 4000K', music: 'Contemplative \u2192 Empowered' },
    script: { opening: "Gold \u2014 what a beautiful choice. Let's make that energy visible.", closing: "Look at that glow. That's the Bloom in you." },
    monologue: "You are ready to be seen. Not for anyone else. For yourself.",
  },
  storm: {
    reading: "You carry weight today. Tension, change, or turbulence. You need grounding, not stimulation. The storm will pass.",
    reason: "Grey tones and heavy energy \u2014 the Storm. Grounding. Peace.",
    protocol: { primary: 'Deep conditioning + extended head massage', why: 'Storm needs grounding. Physical relief. Minimal change.' },
    sensory: { aroma: 'Sandalwood + Frankincense', lighting: 'Warm dim 2200K constant', music: 'Rain sounds \u2192 Silence' },
    script: { opening: "Let's make this chair your safe space today.", closing: "You came in carrying a storm. You're leaving lighter." },
    monologue: "You don't need to explain anything. You just need to breathe.",
  },
};

// Simple deterministic archetype from answers
function determineArchetype(song: string, colour: string, word: string): Archetype {
  const c = (colour ?? '').toLowerCase();
  const w = (word ?? '').toLowerCase();
  if (c.includes('red') || c.includes('orange') || w.includes('bold') || w.includes('fire') || w.includes('strong')) return 'phoenix';
  if (c.includes('blue') || c.includes('teal') || c.includes('aqua') || w.includes('flow') || w.includes('change')) return 'river';
  if (c.includes('purple') || c.includes('silver') || c.includes('white') || w.includes('peace') || w.includes('quiet') || w.includes('calm')) return 'moon';
  if (c.includes('gold') || c.includes('yellow') || c.includes('warm') || w.includes('free') || w.includes('joy') || w.includes('happy') || w.includes('alive')) return 'bloom';
  if (c.includes('grey') || c.includes('gray') || c.includes('black') || c.includes('dark') || w.includes('ground') || w.includes('rest')) return 'storm';
  const hash = (song + colour + word).split('').reduce((a, b) => a + b.charCodeAt(0), 0);
  const types: Archetype[] = ['phoenix', 'river', 'moon', 'bloom', 'storm'];
  return types[hash % 5];
}

export default function SoulskinFlow() {
  const [step, setStep] = useState(0); // 0=intro, 1-3=questions, 4=reveal, 5=reading
  const [answers, setAnswers] = useState({ song: '', colour: '', word: '' });
  const [archetype, setArchetype] = useState<Archetype | null>(null);
  const [currentInput, setCurrentInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Mutation: create a SOULSKIN session
  const createSessionMutation = useMutation({
    mutationFn: (data: { song: string; colour: string; word: string }) =>
      api.post('/soulskin/sessions', data).then(r => r.data?.data),
    onSuccess: (data) => {
      if (data?.id) setSessionId(data.id);
    },
  });

  // Mutation: generate the reading from the backend
  const generateReadingMutation = useMutation({
    mutationFn: (id: string) =>
      api.post(`/soulskin/sessions/${id}/generate`).then(r => r.data?.data),
  });

  const handleAnswer = () => {
    const keys = ['song', 'colour', 'word'] as const;
    if (step >= 1 && step <= 3) {
      const updatedAnswers = { ...answers, [keys[step - 1]]: currentInput };
      setAnswers(updatedAnswers);
      setCurrentInput('');
      if (step === 3) {
        // Determine archetype client-side (instant, no waiting)
        const result = determineArchetype(updatedAnswers.song, updatedAnswers.colour, currentInput);
        setArchetype(result);
        setStep(4);

        // Persist session to API in the background
        createSessionMutation.mutate(
          { song: updatedAnswers.song, colour: updatedAnswers.colour, word: currentInput },
          {
            onSuccess: (data) => {
              // If API returns an archetype, prefer it
              if (data?.archetype && data.archetype !== result) {
                setArchetype(data.archetype);
              }
            },
          }
        );
      } else {
        setStep(step + 1);
      }
    }
  };

  const handleRevealReading = () => {
    setStep(5);
    // Request backend-generated reading if we have a session
    if (sessionId) {
      generateReadingMutation.mutate(sessionId);
    }
  };

  // Use API-generated reading if available, otherwise fall back to local data
  const activeReading = archetype
    ? (generateReadingMutation.data || READINGS[archetype])
    : null;

  return (
    <div style={{ minHeight: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 'var(--space-xl)' }}>
      <AnimatePresence mode="wait">
        {/* INTRO */}
        {step === 0 && (
          <motion.div key="intro" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ maxWidth: 500 }}>
            <Sparkles size={48} style={{ color: 'var(--violet)', marginBottom: 24 }} />
            <h1 className="soulskin-text-glow" style={{ fontFamily: 'var(--font-display)', color: 'var(--violet)', fontSize: '2rem', marginBottom: 16 }}>SOULSKIN</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', lineHeight: 1.8, marginBottom: 8, fontStyle: 'italic' }}>
              "People don't visit salons to change their hair.<br />They visit when something in their life is changing."
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 32 }}>
              Answer 3 simple questions. We'll read your soul \u2014 and design your entire experience around what you actually need today.
            </p>
            <button className="btn btn-violet btn-lg" onClick={() => setStep(1)}>
              <Heart size={18} /> Begin Your Reading
            </button>
          </motion.div>
        )}

        {/* QUESTIONS 1-3 */}
        {step >= 1 && step <= 3 && (
          <motion.div key={`q-${step}`} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -30 }} transition={{ duration: 0.4 }}
            style={{ maxWidth: 500, width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 32 }}>
              {[1, 2, 3].map(s => (
                <div key={s} style={{ width: s === step ? 32 : 8, height: 8, borderRadius: 4, background: s < step ? 'var(--violet)' : s === step ? 'var(--violet)' : 'var(--border-subtle)', transition: 'all 0.3s' }} />
              ))}
            </div>

            <div style={{ color: 'var(--violet)', marginBottom: 20 }}>{QUESTIONS[step - 1].icon}</div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: 8 }}>
              {QUESTIONS[step - 1].emoji} {QUESTIONS[step - 1].question}
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 32 }}>There are no wrong answers. Just truth.</p>

            <div style={{ position: 'relative' }}>
              <input
                className="input"
                value={currentInput}
                onChange={e => setCurrentInput(e.target.value)}
                placeholder={QUESTIONS[step - 1].placeholder}
                onKeyDown={e => e.key === 'Enter' && currentInput && handleAnswer()}
                autoFocus
                style={{ fontSize: '1.1rem', padding: '14px 50px 14px 18px', textAlign: 'center', borderColor: 'var(--violet)', background: 'rgba(155,127,212,0.04)' }}
              />
              {currentInput && (
                <button onClick={handleAnswer} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'var(--violet)', border: 'none', borderRadius: '50%', width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                  <ArrowRight size={16} color="white" />
                </button>
              )}
            </div>
          </motion.div>
        )}

        {/* REVEAL */}
        {step === 4 && archetype && (
          <motion.div key="reveal" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.6 }}
            style={{ maxWidth: 500 }}>
            <motion.div
              animate={{ boxShadow: [`0 0 0px transparent`, `0 0 60px ${ARCHETYPES[archetype].color}44`, `0 0 20px ${ARCHETYPES[archetype].color}22`] }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{ width: 120, height: 120, borderRadius: '50%', background: `${ARCHETYPES[archetype].color}15`, border: `3px solid ${ARCHETYPES[archetype].color}`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px', fontSize: '3rem' }}>
              {ARCHETYPES[archetype].emoji}
            </motion.div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: 8 }}>Your archetype is...</p>
            <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', color: ARCHETYPES[archetype].color, marginBottom: 8 }}>
              {ARCHETYPES[archetype].name}
            </h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 32 }}>Element: {ARCHETYPES[archetype].element}</p>

            <button className="btn btn-lg" style={{ background: ARCHETYPES[archetype].color, color: 'white' }}
              onClick={handleRevealReading}>
              Read My Soul <ChevronRight size={18} />
            </button>
          </motion.div>
        )}

        {/* FULL READING */}
        {step === 5 && archetype && activeReading && (
          <motion.div key="reading" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            style={{ maxWidth: 600, width: '100%', textAlign: 'left' }}>
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <ArchetypeBadge archetype={archetype} size="lg" />
            </div>

            {/* Soul Reading */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="card" style={{ background: `${ARCHETYPES[archetype].color}08`, borderColor: `${ARCHETYPES[archetype].color}30`, marginBottom: 16 }}>
              <h4 style={{ color: ARCHETYPES[archetype].color, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Heart size={16} /> Your Soul Reading
              </h4>
              <p style={{ fontSize: '1rem', fontStyle: 'italic', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                "{activeReading.reading}"
              </p>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 12 }}>
                {activeReading.reason}
              </p>
            </motion.div>

            {/* Service Protocol */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
              className="card" style={{ marginBottom: 16 }}>
              <h4 style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>\u2702\uFE0F Recommended Treatment</h4>
              <div style={{ background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', padding: 14 }}>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{activeReading.protocol.primary}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{activeReading.protocol.why}</div>
              </div>
            </motion.div>

            {/* Sensory Environment */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}
              className="card" style={{ marginBottom: 16 }}>
              <h4 style={{ marginBottom: 12 }}>\uD83C\uDF3F Your Sensory Environment</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                {[
                  { label: 'Aroma', value: activeReading.sensory.aroma, icon: '\uD83C\uDF3F' },
                  { label: 'Lighting', value: activeReading.sensory.lighting, icon: '\uD83D\uDCA1' },
                  { label: 'Music', value: activeReading.sensory.music, icon: '\uD83C\uDFB5' },
                ].map((s, i) => (
                  <div key={i} style={{ background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', padding: 12, textAlign: 'center' }}>
                    <div style={{ fontSize: '1.2rem', marginBottom: 4 }}>{s.icon}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 2 }}>{s.label}</div>
                    <div style={{ fontSize: '0.75rem' }}>{s.value}</div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Mirror Monologue */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}
              className="card" style={{ background: `${ARCHETYPES[archetype].color}05`, borderColor: `${ARCHETYPES[archetype].color}25`, textAlign: 'center' }}>
              <h4 style={{ marginBottom: 12, color: ARCHETYPES[archetype].color }}>\uD83E\uDE9E Mirror Monologue</h4>
              <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', fontStyle: 'italic', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                "{activeReading.monologue}"
              </p>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 12 }}>
                \u2014 Read to you at the mirror reveal, after your transformation
              </p>
            </motion.div>

            {/* Answers recap */}
            <div style={{ marginTop: 24, display: 'flex', gap: 8, justifyContent: 'center' }}>
              <span style={{ fontSize: '0.75rem', background: 'var(--bg-card)', padding: '4px 12px', borderRadius: 'var(--radius-full)', color: 'var(--text-muted)' }}>\uD83C\uDFB5 {answers.song}</span>
              <span style={{ fontSize: '0.75rem', background: 'var(--bg-card)', padding: '4px 12px', borderRadius: 'var(--radius-full)', color: 'var(--text-muted)' }}>\uD83C\uDFA8 {answers.colour}</span>
              <span style={{ fontSize: '0.75rem', background: 'var(--bg-card)', padding: '4px 12px', borderRadius: 'var(--radius-full)', color: 'var(--text-muted)' }}>\uD83D\uDCAC {answers.word}</span>
            </div>

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <button className="btn btn-ghost" onClick={() => { setStep(0); setAnswers({ song: '', colour: '', word: '' }); setArchetype(null); setSessionId(null); }}>
                Start Over
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
