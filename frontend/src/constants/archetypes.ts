import { Flame, Waves, Moon, Flower2, CloudLightning } from 'lucide-react';

export const ARCH_DATA: Record<string, { icon: typeof Flame; color: string; label: string }> = {
  phoenix: { icon: Flame, color: '#E8611A', label: 'Phoenix' },
  river: { icon: Waves, color: '#4A9FD4', label: 'River' },
  moon: { icon: Moon, color: '#7B68C8', label: 'Moon' },
  bloom: { icon: Flower2, color: '#E8A87C', label: 'Bloom' },
  storm: { icon: CloudLightning, color: '#6B8FA6', label: 'Storm' },
};
