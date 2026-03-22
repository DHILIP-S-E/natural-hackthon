import { motion } from 'framer-motion';

import { Sparkles } from 'lucide-react';

export function InlineSparkle() {
  return (
    <motion.span
      animate={{ rotate: 360, scale: [1, 1.1, 1] }}
      transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2px 6px',
        borderRadius: '12px',
        background: 'linear-gradient(135deg, rgba(231,111,111,0.1), rgba(42,157,143,0.1))',
        border: '1px solid var(--border-subtle)',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        color: 'var(--gold)',
        marginLeft: '6px'
      }}
    >
      <Sparkles size={11} style={{ transform: 'translateZ(5px)' }} strokeWidth={2.5} />
    </motion.span>
  );
}
