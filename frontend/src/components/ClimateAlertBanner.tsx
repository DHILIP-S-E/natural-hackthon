import { useState } from 'react';
import { Sun, AlertTriangle, X } from 'lucide-react';

interface Props {
  city: string;
  uvIndex: number;
  humidity: number;
  aqi: number;
  weatherCondition: string;
}

export default function ClimateAlertBanner({ city, uvIndex, humidity, aqi, weatherCondition }: Props) {
  const [dismissed, setDismissed] = useState(false);

  const highUV = uvIndex > 8;
  const highAQI = aqi > 200;

  if (dismissed || (!highUV && !highAQI)) return null;

  const alertMessages: string[] = [];
  if (highUV) {
    alertMessages.push(`High UV in ${city} today (${uvIndex}) — recommend UV-protective services`);
  }
  if (highAQI) {
    alertMessages.push(`Poor air quality in ${city} (AQI ${aqi}) — recommend deep-cleansing & barrier treatments`);
  }

  return (
    <div
      style={{
        background: 'linear-gradient(135deg, #C9A96E 0%, #D4B87A 100%)',
        borderRadius: 'var(--radius-md)',
        padding: '14px 20px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        position: 'relative',
        boxShadow: 'var(--shadow-md)',
        marginBottom: 'var(--space-md)',
      }}
    >
      {/* Icon */}
      <div
        style={{
          flexShrink: 0,
          width: 36,
          height: 36,
          borderRadius: 'var(--radius-full)',
          background: 'rgba(255, 255, 255, 0.25)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {highUV ? <Sun size={20} color="#1A1A24" /> : <AlertTriangle size={20} color="#1A1A24" />}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.8rem',
            fontWeight: 600,
            color: '#1A1A24',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            marginBottom: '4px',
          }}
        >
          Climate Alert — {weatherCondition}
        </div>
        {alertMessages.map((msg, i) => (
          <div
            key={i}
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.85rem',
              fontWeight: 500,
              color: '#1A1A24',
              lineHeight: 1.5,
            }}
          >
            {msg}
          </div>
        ))}
        <div style={{ marginTop: '10px' }}>
          <button
            style={{
              background: 'var(--teal)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              padding: '6px 16px',
              fontSize: '0.8rem',
              fontWeight: 600,
              fontFamily: 'var(--font-body)',
              cursor: 'pointer',
              transition: 'background var(--transition-fast)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--teal-dim)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--teal)')}
          >
            View Recommendations
          </button>
        </div>
      </div>

      {/* Dismiss button */}
      <button
        onClick={() => setDismissed(true)}
        aria-label="Dismiss alert"
        style={{
          flexShrink: 0,
          background: 'rgba(255, 255, 255, 0.2)',
          border: 'none',
          borderRadius: 'var(--radius-full)',
          width: 28,
          height: 28,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          color: '#1A1A24',
          transition: 'background var(--transition-fast)',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.4)')}
        onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)')}
      >
        <X size={16} />
      </button>
    </div>
  );
}
