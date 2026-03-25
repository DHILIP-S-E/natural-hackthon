import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { GitCompare, Check } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../../config/api';

interface CompareEntry {
  name: string;
  revenue: number;
  quality: number;
  bookings: number;
  soulskin: number;
}

const tooltipStyle = { backgroundColor: '#16161E', border: '1px solid #252530', borderRadius: '8px', fontSize: '0.75rem', color: '#fff' };

const METRIC_COLORS: Record<string, string> = {
  revenue: '#f44f9a',
  quality: '#9B7FD4',
  bookings: '#2A9D8F',
  soulskin: '#E8611A',
};

export default function CompareLocationsPage() {
  const { data: compareData = [], isLoading } = useQuery<CompareEntry[]>({
    queryKey: ['analytics-compare'],
    queryFn: () => api.get('/analytics/compare').then(r => r.data?.data),
  });

  const [selected, setSelected] = useState<Set<string> | null>(null);

  // Initialize selected set once data arrives
  React.useEffect(() => {
    if (compareData.length > 0 && selected === null) {
      setSelected(new Set(compareData.map(l => l.name)));
    }
  }, [compareData, selected]);

  const activeSelected = selected ?? new Set<string>();

  const toggleLocation = (name: string) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const filteredData = compareData.filter(l => activeSelected.has(l.name));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <GitCompare size={28} style={{ color: 'var(--violet)' }} />
          Compare Locations
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
          Side-by-side performance comparison across your network
        </p>
      </div>

      {/* Location selector */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card">
        <h4 style={{ marginBottom: 12 }}>Select Locations</h4>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {isLoading ? (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading locations...</span>
          ) : compareData.length === 0 ? (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No locations available</span>
          ) : compareData.map((loc, i) => {
            const isSelected = activeSelected.has(loc.name);
            return (
              <button
                key={i}
                onClick={() => toggleLocation(loc.name)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  padding: '8px 16px', borderRadius: 'var(--radius-full)',
                  border: `1px solid ${isSelected ? 'var(--teal)' : 'var(--border-subtle)'}`,
                  background: isSelected ? 'rgba(42,157,143,0.08)' : 'var(--bg-surface)',
                  color: isSelected ? 'var(--teal)' : 'var(--text-secondary)',
                  fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                {isSelected && <Check size={14} />}
                {loc.name}
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Revenue */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
          <TiltCard tiltIntensity={3} className="card">
            <h4 style={{ marginBottom: 16 }}>Revenue Comparison (Lakhs)</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="revenue" fill={METRIC_COLORS.revenue} radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </TiltCard>
        </motion.div>

        {/* Quality */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <TiltCard tiltIntensity={3} className="card">
            <h4 style={{ marginBottom: 16 }}>Quality Score</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis domain={[4, 5]} tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="quality" fill={METRIC_COLORS.quality} radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </TiltCard>
        </motion.div>

        {/* Bookings */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}>
          <TiltCard tiltIntensity={3} className="card">
            <h4 style={{ marginBottom: 16 }}>Total Bookings</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="bookings" fill={METRIC_COLORS.bookings} radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </TiltCard>
        </motion.div>

        {/* SOULSKIN */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <TiltCard tiltIntensity={3} className="card">
            <h4 style={{ marginBottom: 16 }}>SOULSKIN Sessions</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="soulskin" fill={METRIC_COLORS.soulskin} radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </TiltCard>
        </motion.div>
      </div>
    </div>
  );
}
