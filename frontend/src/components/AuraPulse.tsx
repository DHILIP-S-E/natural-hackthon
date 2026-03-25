import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, X, TrendingUp, Activity, Sparkles, MessageSquare } from 'lucide-react';

const MOCK_INSIGHTS = [
  { id: 1, type: 'trend', text: "Trend 'Copper Balayage' detected rising +14% in Mumbai.", icon: <TrendingUp size={14} /> },
  { id: 2, type: 'health', text: "AURA Alert: Humidity in your area is high (82%). Use sealant.", icon: <Sparkles size={14} /> },
  { id: 3, type: 'quality', text: "Operational Health: Service consistency is at 94% today.", icon: <Activity size={14} /> },
  { id: 4, type: 'tip', text: "AURA Tip: Your face shape is best suited for layered waves.", icon: <MessageSquare size={14} /> },
];

export default function AuraPulse() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ position: 'fixed', bottom: 30, right: 30, zIndex: 1000 }}>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            style={{
              position: 'absolute', bottom: 80, right: 0,
              width: 320, background: 'rgba(26, 26, 36, 0.95)',
              backdropFilter: 'blur(12px)', border: '1px solid rgba(244, 79, 154, 0.3)',
              borderRadius: '24px', padding: '24px', color: 'white',
              boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Brain size={20} style={{ color: '#f44f9a' }} />
                <span style={{ fontWeight: 800, fontSize: '1rem', letterSpacing: '0.05em' }}>AURA AI PULSE</span>
              </div>
              <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {MOCK_INSIGHTS.map((insight, i) => (
                <motion.div
                  key={insight.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  style={{
                    display: 'flex', gap: 12, padding: '12px',
                    background: 'rgba(255,255,255,0.05)', borderRadius: '12px',
                    fontSize: '0.85rem', lineHeight: 1.4,
                  }}
                >
                  <div style={{ color: '#f44f9a', marginTop: 2 }}>{insight.icon}</div>
                  <div>{insight.text}</div>
                </motion.div>
              ))}
            </div>

            <div style={{ marginTop: 20, textAlign: 'center', fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              • Live Intelligence Syncing •
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: 64, height: 64, borderRadius: '50%',
          background: 'linear-gradient(135deg, #f44f9a 0%, #9b7fd4 100%)',
          border: 'none', color: 'white', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 8px 24px rgba(244, 79, 154, 0.4)',
          position: 'relative',
        }}
      >
        <Brain size={28} />
        <motion.div
          animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0, 0.6] }}
          transition={{ repeat: Infinity, duration: 2 }}
          style={{
            position: 'absolute', inset: 0, borderRadius: '50%',
            border: '2px solid #f44f9a',
          }}
        />
        <div style={{
          position: 'absolute', top: -4, right: -4,
          width: 20, height: 20, borderRadius: '50%',
          background: '#f44f9a', border: '2px solid white',
          fontSize: '10px', fontWeight: 900, display: 'flex',
          alignItems: 'center', justifyContent: 'center',
        }}>4</div>
      </motion.button>
    </div>
  );
}
