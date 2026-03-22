import { motion } from 'framer-motion';

export function Logo3D({ size = 120 }: { size?: number }) {
  return (
    <div style={{ width: size, height: size, perspective: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <motion.div
        animate={{ rotateY: [0, 360], rotateX: [15, -15, 15] }}
        transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
        style={{ width: '100%', height: '100%', position: 'relative', transformStyle: 'preserve-3d' }}
      >
        {/* Ring 1 - Vertical Orbit */}
        <motion.div 
          animate={{ rotateZ: [0, 360] }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          style={{ position: 'absolute', inset: 0, border: '4px solid var(--gold)', borderRadius: '50%', transform: 'rotateY(75deg) translateZ(0px)', boxShadow: '0 0 20px var(--gold-glow), inset 0 0 20px var(--gold-glow)' }} 
        />
        {/* Ring 2 - Horizontal Orbit */}
        <motion.div 
          animate={{ rotateZ: [360, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          style={{ position: 'absolute', inset: '-10%', border: '2px solid var(--violet)', borderRadius: '50%', transform: 'rotateX(75deg) translateZ(0px)', boxShadow: '0 0 15px var(--violet-glow)' }} 
        />
        {/* Core Jewel */}
        <div style={{ position: 'absolute', inset: '22%', background: 'linear-gradient(135deg, var(--gold), var(--rose))', borderRadius: '30%', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: 'translateZ(10px)', boxShadow: '0 10px 40px rgba(0,0,0,0.3), inset 0 2px 10px rgba(255,255,255,0.6)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.4)' }}>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: size * 0.45, fontWeight: 900, color: '#fff', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>A</span>
        </div>
      </motion.div>
    </div>
  );
}
