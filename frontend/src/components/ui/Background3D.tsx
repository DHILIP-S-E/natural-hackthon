import { motion } from 'framer-motion';

export function Background3D() {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden', pointerEvents: 'none' }}>

      {/* Mesh gradients — GPU-friendly (no backdrop-filter) */}
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

      {/* Static decorative shapes — no animations, no backdrop-filter */}
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: `${15 + i * 18}%`,
            left: `${10 + i * 17}%`,
            width: 150 + i * 40,
            height: 150 + i * 40,
            background: 'linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.0))',
            border: '1px solid var(--border-subtle)',
            borderRadius: i % 3 === 0 ? '50%' : i % 3 === 1 ? '20px' : '30% 70% 70% 30% / 30% 30% 70% 70%',
            opacity: 0.4,
          }}
        />
      ))}

      {/* Grain overlay for premium texture */}
      <div style={{ position: 'absolute', inset: 0, opacity: 0.25, backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`, mixBlendMode: 'multiply' }} />
    </div>
  );
}
