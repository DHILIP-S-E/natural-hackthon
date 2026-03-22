import { motion } from 'framer-motion';

export function Background3D() {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden', pointerEvents: 'none' }}>
      
      {/* Mesh gradients */}
      <motion.div 
        animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 0] }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        style={{ position: 'absolute', top: '-20%', left: '-10%', width: '70vw', height: '70vw', borderRadius: '50%', background: 'radial-gradient(circle, var(--rose-glow) 0%, transparent 60%)', filter: 'blur(100px)' }}
      />
      <motion.div 
        animate={{ scale: [1, 1.5, 1], rotate: [0, -90, 0], x: [0, 100, 0] }}
        transition={{ duration: 50, repeat: Infinity, ease: "linear" }}
        style={{ position: 'absolute', top: '10%', right: '-10%', width: '80vw', height: '80vw', borderRadius: '50%', background: 'radial-gradient(circle, var(--teal-glow) 0%, transparent 60%)', filter: 'blur(120px)' }}
      />
      
      {/* Floating 3D geometries */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ y: `${Math.random() * 100}vh`, x: `${Math.random() * 100}vw`, rotateX: Math.random() * 360, rotateY: Math.random() * 360 }}
          animate={{
            y: [`${Math.random() * 100}vh`, `${Math.random() * 100}vh`],
            x: [`${Math.random() * 100}vw`, `${Math.random() * 100}vw`],
            rotateX: [0, 360, 0],
            rotateY: [0, -360, 0],
            rotateZ: [0, 180, 0],
          }}
          transition={{ duration: 60 + Math.random() * 40, repeat: Infinity, ease: "linear" }}
          style={{
            position: 'absolute',
            width: 150 + Math.random() * 300,
            height: 150 + Math.random() * 300,
            background: 'linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.0))',
            backdropFilter: 'blur(15px)',
            border: '1px solid var(--border-subtle)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.05)',
            borderRadius: i % 3 === 0 ? '50%' : i % 3 === 1 ? '20px' : '30% 70% 70% 30% / 30% 30% 70% 70%',
            transformStyle: 'preserve-3d',
            perspective: '1500px',
            opacity: 0.6
          }}
        />
      ))}
      
      {/* Grain overlay for premium texture */}
      <div style={{ position: 'absolute', inset: 0, opacity: 0.25, backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`, mixBlendMode: 'multiply' }} />
    </div>
  );
}
