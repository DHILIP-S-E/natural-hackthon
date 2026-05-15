export type Archetype = 'phoenix' | 'river' | 'moon' | 'bloom' | 'storm';

export interface ArchetypeInfo {
  name: string;
  emoji: string;
  color: string;
  element: string;
  description: string;
}

export const ARCHETYPES: Record<Archetype, ArchetypeInfo> = {
  phoenix: { name: 'Phoenix', emoji: '🔥', color: '#E8611A', element: 'Fire', description: 'You are standing at the edge of something ending. You are not afraid of the fire.' },
  river: { name: 'River', emoji: '🌊', color: '#4A9FD4', element: 'Water', description: 'You are in flow. Something is shifting inside you.' },
  moon: { name: 'Moon', emoji: '🌙', color: '#7B68C8', element: 'Light', description: 'You are in a quiet phase. You need softness and gentle reflection.' },
  bloom: { name: 'Bloom', emoji: '🌸', color: '#E8A87C', element: 'Earth', description: 'You are growing. Something new is opening inside you.' },
  storm: { name: 'Storm', emoji: '⛈️', color: '#6B8FA6', element: 'Air', description: 'You carry weight today. You need grounding, not stimulation.' },
};

export interface SoulskinSession {
  id: string;
  booking_id?: string;
  customer_id: string;
  question_1_song?: string;
  question_2_colour?: string;
  question_3_word?: string;
  archetype?: Archetype;
  soul_reading?: string;
  archetype_reason?: string;
  service_protocol?: Record<string, string>;
  colour_direction?: Record<string, string>;
  sensory_environment?: unknown;
  touch_protocol?: unknown;
  custom_formula?: unknown;
  stylist_script?: Record<string, string>;
  mirror_monologue?: string;
  private_life_note?: string;
  look_created?: string;
  session_completed: boolean;
}
