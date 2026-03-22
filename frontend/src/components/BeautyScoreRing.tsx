interface Props {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export default function BeautyScoreRing({ score, size = 100, strokeWidth = 6 }: Props) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 81) return 'var(--gold)';
    if (s >= 61) return 'var(--teal)';
    if (s >= 41) return 'var(--warning)';
    return 'var(--error)';
  };

  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="var(--border-subtle)" strokeWidth={strokeWidth}
        />
        {/* Score arc */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={getColor(score)} strokeWidth={strokeWidth}
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease-out' }}
        />
      </svg>
      <span className="score-value" style={{ color: getColor(score), fontSize: size * 0.22 }}>
        {score}
      </span>
    </div>
  );
}
