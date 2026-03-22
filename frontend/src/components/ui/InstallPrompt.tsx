import { useInstallPrompt } from '../../hooks/useInstallPrompt';
import { motion, AnimatePresence } from 'framer-motion';

export default function InstallPrompt() {
  const { canInstall, install, dismiss } = useInstallPrompt();

  return (
    <AnimatePresence>
      {canInstall && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          style={{
            position: 'fixed', bottom: '5rem', left: '1rem', right: '1rem',
            background: 'var(--surface-2)', border: '1px solid var(--accent-gold)',
            borderRadius: '1rem', padding: '1.25rem', zIndex: 9999,
            display: 'flex', alignItems: 'center', gap: '1rem',
            boxShadow: '0 -4px 20px rgba(201, 169, 110, 0.2)',
            maxWidth: '480px', margin: '0 auto',
          }}
        >
          <div style={{ fontSize: '2rem' }}>✨</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
              Install AURA
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Instant access to your Beauty Passport
            </div>
          </div>
          <button className="btn btn-primary" onClick={install} style={{ padding: '0.5rem 1rem' }}>
            Install
          </button>
          <button onClick={dismiss} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem' }}>
            ✕
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
