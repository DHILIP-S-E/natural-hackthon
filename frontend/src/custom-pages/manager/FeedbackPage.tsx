import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { MessageSquare, Star, ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react';
import api from '../../config/api';

const SENTIMENT_STYLE: Record<string, { bg: string; color: string; icon: React.ReactNode }> = {
  positive: { bg: 'rgba(82,183,136,0.1)', color: 'var(--success)', icon: <ThumbsUp size={12} /> },
  neutral: { bg: 'rgba(244,162,97,0.1)', color: 'var(--warning)', icon: <MessageSquare size={12} /> },
  negative: { bg: 'rgba(231,111,111,0.1)', color: 'var(--error)', icon: <ThumbsDown size={12} /> },
};

function deriveSentiment(rating: number): string {
  if (rating >= 4) return 'positive';
  if (rating >= 3) return 'neutral';
  return 'negative';
}

export default function FeedbackPage() {
  const { data: feedbackData, isLoading } = useQuery({
    queryKey: ['feedback'],
    queryFn: () => api.get('/feedback/?per_page=30').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.feedback || [];
    }),
  });

  const feedback = feedbackData || [];
  const avgRating = feedback.length > 0
    ? (feedback.reduce((s: number, f: any) => s + (f.overall_rating || 0), 0) / feedback.length).toFixed(1)
    : '0';
  const positiveRate = feedback.length > 0
    ? Math.round(feedback.filter((f: any) => (f.overall_rating || 0) >= 4).length / feedback.length * 100)
    : 0;
  const soulskinRated = feedback.filter((f: any) => f.soulskin_rating || f.soulskin_session_id).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: 12 }}>
          <MessageSquare size={28} style={{ color: 'var(--teal)' }} /> Feedback
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          {feedback.length} reviews · {avgRating} avg · {positiveRate}% positive
        </p>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-md)' }}>
        {[
          { label: 'Avg Rating', value: avgRating, icon: <Star size={16} />, color: 'var(--gold)' },
          { label: 'Total Reviews', value: feedback.length.toString(), icon: <MessageSquare size={16} />, color: 'var(--teal)' },
          { label: 'Positive %', value: `${positiveRate}%`, icon: <ThumbsUp size={16} />, color: 'var(--success)' },
          { label: 'SOULSKIN Rated', value: soulskinRated.toString(), icon: <Sparkles size={16} />, color: 'var(--violet)' },
        ].map((k, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="kpi-card" style={{ borderLeft: `3px solid ${k.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: k.color }}>{k.icon}<span className="kpi-label">{k.label}</span></div>
            <span className="kpi-value" style={{ fontSize: '1.3rem' }}>{k.value}</span>
          </motion.div>
        ))}
      </div>

      {/* Feedback list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
        {isLoading ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>Loading feedback...</div>
        ) : feedback.length === 0 ? (
          <div className="card" style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No feedback received yet
          </div>
        ) : feedback.map((f: any, i: number) => {
          const overall = f.overall_rating || 0;
          const sentiment = f.sentiment || deriveSentiment(overall);
          const sent = SENTIMENT_STYLE[sentiment] || SENTIMENT_STYLE.neutral;
          const dateStr = f.created_at ? new Date(f.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) : '';
          const soulskinScore = f.soulskin_rating || null;

          return (
            <motion.div key={f.id || i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
              className="card" style={{ padding: '16px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{f.customer_name || 'Customer'}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {f.service_name || 'Service'} · {dateStr}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ display: 'flex', gap: 2 }}>
                    {Array.from({ length: 5 }).map((_, j) => (
                      <Star key={j} size={12} style={{ color: j < overall ? 'var(--gold)' : 'var(--border-subtle)', fill: j < overall ? 'var(--gold)' : 'none' }} />
                    ))}
                  </div>
                  {soulskinScore && <span className="badge badge-violet" style={{ padding: '1px 6px', fontSize: '0.6rem' }}>✨ {soulskinScore}</span>}
                  <span className="badge" style={{ background: sent.bg, color: sent.color, display: 'flex', alignItems: 'center', gap: 3, padding: '2px 8px' }}>
                    {sent.icon} {sentiment}
                  </span>
                </div>
              </div>
              {f.comment && (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>"{f.comment}"</p>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
