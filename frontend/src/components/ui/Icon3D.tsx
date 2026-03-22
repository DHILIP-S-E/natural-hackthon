import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface Icon3DProps {
  children: ReactNode;
  color?: string;
  glowColor?: string;
  size?: 'sm' | 'md' | 'lg';
  delay?: number;
}

export function Icon3D({ children, color = 'var(--gold)', glowColor = 'var(--gold-glow)', size = 'md', delay = 0 }: Icon3DProps) {
  const sizeMap = { sm: '32px', md: '48px', lg: '64px' };
  
  return (
    <motion.div
      initial={{ y: 0, rotateY: 0 }}
      animate={{ 
        y: [0, -6, 0]
      }}
      transition={{ 
        duration: 3 + Math.random(), 
        repeat: Infinity, 
        ease: "easeInOut",
        delay 
      }}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: sizeMap[size],
        height: sizeMap[size],
        borderRadius: '16px',
        backgroundColor: 'var(--bg-elevated)',
        border: '1px solid var(--border-subtle)',
        boxShadow: `0 4px 20px ${glowColor}, inset 0 2px 5px rgba(255,255,255,0.7)`,
        color: color,
        transformStyle: 'preserve-3d',
        perspective: '1000px',
        background: 'linear-gradient(145deg, var(--bg-card), var(--bg-surface))'
      }}
      whileHover={{ 
        scale: 1.1,
        rotateZ: 5,
        boxShadow: `0 12px 30px ${glowColor}`
      }}
    >
      <motion.div 
        initial={{ rotateY: 0 }}
        whileHover={{ rotateY: 360 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        style={{ transform: 'translateZ(15px)', display: 'flex' }}
      >
        {children}
      </motion.div>
    </motion.div>
  );
}
