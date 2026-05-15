/* Placeholder dashboard for roles that share the same structure */
import { motion } from 'framer-motion';
import { LayoutDashboard } from 'lucide-react';

interface Props {
  title: string;
  subtitle: string;
}

export default function PlaceholderDashboard({ title, subtitle }: Props) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', textAlign: 'center' }}>
      <LayoutDashboard size={48} style={{ color: 'var(--gold)', marginBottom: 16 }} />
      <h2>{title}</h2>
      <p style={{ color: 'var(--text-muted)', marginTop: 8, maxWidth: 400 }}>{subtitle}</p>
      <span className="badge badge-teal" style={{ marginTop: 16 }}>Coming in Phase 2</span>
    </motion.div>
  );
}
