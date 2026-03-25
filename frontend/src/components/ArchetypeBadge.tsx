import type { Archetype } from '../types';
import { ARCHETYPES } from '../types';

interface Props {
  archetype: Archetype;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export default function ArchetypeBadge({ archetype, size = 'md', showLabel = true }: Props) {
  const info = ARCHETYPES[archetype];
  if (!info) return null;

  const sizes = { sm: { fontSize: '0.65rem', padding: '2px 8px' }, md: { fontSize: '0.75rem', padding: '4px 12px' }, lg: { fontSize: '0.85rem', padding: '6px 16px' } };

  return (
    <span
      className={`badge archetype-${archetype}`}
      style={sizes[size]}
    >
      {info.emoji} {showLabel && info.name}
    </span>
  );
}
