/**
 * Feature 15: Voice-Activated Stylist Assistant
 * Button-press activation (never always-on). Multi-language support.
 * Web Speech API → backend intent parsing → spoken response.
 */
import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Volume2, Globe, MessageSquare, Loader } from 'lucide-react';
import api from '../../config/api';
import { useAuthStore } from '../../stores/authStore';

interface VoiceResponse {
  transcript: string;
  intent: string;
  entities: Record<string, string | null>;
  spoken_response: string;
  language: string;
  language_name: string;
}

const LANGUAGES = [
  { code: 'en-IN', api_code: 'en', label: 'English' },
  { code: 'ta-IN', api_code: 'ta', label: 'Tamil' },
  { code: 'te-IN', api_code: 'te', label: 'Telugu' },
  { code: 'hi-IN', api_code: 'hi', label: 'Hindi' },
  { code: 'kn-IN', api_code: 'kn', label: 'Kannada' },
  { code: 'ml-IN', api_code: 'ml', label: 'Malayalam' },
];

const INTENT_LABELS: Record<string, string> = {
  client_history: '🧴 Client History',
  technique_steps: '📋 Technique Guide',
  staff_availability: '👥 Staff Availability',
  product_info: '🧪 Product Info',
  booking_info: '📅 Booking Info',
  general: '💬 General Query',
};

const EXAMPLE_QUERIES = [
  '"Hey AURA, what colour was used on this client last time?"',
  '"Show me the steps for Balayage"',
  '"Is Priya free at 4 PM today?"',
  '"What products does this client prefer?"',
];

export default function VoiceAssistant() {
  const { user } = useAuthStore();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState<VoiceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedLang, setSelectedLang] = useState(LANGUAGES[0]);
  const [history, setHistory] = useState<VoiceResponse[]>([]);
  const [speechSupported, setSpeechSupported] = useState(true);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
      setSpeechSupported(false);
    }
  }, []);

  const startListening = useCallback(() => {
    if (!speechSupported) return;
    setError(null);
    setTranscript('');
    setResponse(null);

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = selectedLang.code;
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const current = event.results[event.results.length - 1];
      setTranscript(current[0].transcript);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setError(`Mic error: ${event.error}. Try again.`);
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  }, [speechSupported, selectedLang]);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  const handleMicButton = useCallback(() => {
    if (isListening) {
      stopListening();
      // Auto-submit when mic is released
      setTimeout(() => {
        if (transcript) submitQuery();
      }, 100);
    } else {
      startListening();
    }
  }, [isListening, transcript, startListening, stopListening]);

  const submitQuery = useCallback(async () => {
    if (!transcript.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.post('/voice/query', {
        transcript: transcript.trim(),
        stylist_language: selectedLang.api_code,
        location_id: null,
        active_booking_id: null,
      });

      const data = res.data?.data as VoiceResponse;
      setResponse(data);
      setHistory(prev => [data, ...prev].slice(0, 10));

      // Speak the response
      if ('speechSynthesis' in window && data.spoken_response) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(data.spoken_response);
        utterance.lang = selectedLang.code;
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        synthesisRef.current = utterance;
        window.speechSynthesis.speak(utterance);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Query failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [transcript, selectedLang]);

  const stopSpeaking = () => {
    window.speechSynthesis?.cancel();
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', color: '#fff', fontFamily: 'DM Sans, sans-serif', padding: '24px 16px' }}>
      <div style={{ maxWidth: 640, margin: '0 auto' }}>
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32, textAlign: 'center' }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#C9A96E', fontFamily: 'Playfair Display, serif', marginBottom: 8 }}>
            Hey AURA
          </div>
          <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)' }}>Hands-free AI assistant — press and speak</div>
        </motion.div>

        {/* Language Selector */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap', justifyContent: 'center' }}>
          {LANGUAGES.map(lang => (
            <button key={lang.code} onClick={() => setSelectedLang(lang)} style={{ padding: '6px 14px', borderRadius: 20, border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 600, background: selectedLang.code === lang.code ? '#C9A96E' : 'rgba(255,255,255,0.06)', color: selectedLang.code === lang.code ? '#0A0A0F' : 'rgba(255,255,255,0.6)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <Globe size={11} /> {lang.label}
            </button>
          ))}
        </div>

        {/* Main Mic Button */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 32 }}>
          {!speechSupported && (
            <div style={{ padding: 12, background: 'rgba(255,193,7,0.1)', border: '1px solid rgba(255,193,7,0.3)', borderRadius: 10, color: '#ffc107', fontSize: 13, marginBottom: 16, textAlign: 'center' }}>
              Voice recognition not supported in this browser. Use Chrome for best experience.
            </div>
          )}

          <motion.button
            onMouseDown={startListening}
            onMouseUp={() => { stopListening(); setTimeout(() => { if (transcript) submitQuery(); }, 200); }}
            onTouchStart={startListening}
            onTouchEnd={() => { stopListening(); setTimeout(() => { if (transcript) submitQuery(); }, 200); }}
            onClick={speechSupported ? undefined : () => {}}
            disabled={!speechSupported || loading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{ width: 120, height: 120, borderRadius: '50%', border: 'none', cursor: speechSupported ? 'pointer' : 'not-allowed', background: isListening ? 'linear-gradient(135deg, #ef4444, #b91c1c)' : 'linear-gradient(135deg, #C9A96E, #8B6914)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: isListening ? '0 0 40px rgba(239,68,68,0.5)' : '0 0 30px rgba(201,169,110,0.3)', position: 'relative' }}
          >
            {isListening ? <MicOff size={40} color="#fff" /> : <Mic size={40} color="#fff" />}
            {isListening && (
              <motion.div
                animate={{ scale: [1, 1.4, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                style={{ position: 'absolute', inset: -12, borderRadius: '50%', border: '2px solid rgba(239,68,68,0.4)' }}
              />
            )}
          </motion.button>

          <div style={{ marginTop: 16, fontSize: 13, color: isListening ? '#ef4444' : 'rgba(255,255,255,0.4)', fontWeight: 600 }}>
            {loading ? 'Processing...' : isListening ? 'Listening... Release to send' : 'Hold to speak'}
          </div>
        </div>

        {/* Live Transcript */}
        <AnimatePresence>
          {transcript && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} style={{ padding: 16, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
                <MessageSquare size={11} /> You said:
              </div>
              <div style={{ fontSize: 15, color: '#fff', fontStyle: 'italic' }}>"{transcript}"</div>
              {!isListening && !loading && (
                <button onClick={submitQuery} style={{ marginTop: 10, padding: '8px 16px', background: 'rgba(201,169,110,0.15)', border: '1px solid rgba(201,169,110,0.3)', borderRadius: 8, color: '#C9A96E', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                  Send Query →
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: 'center', padding: 20, color: 'rgba(255,255,255,0.4)' }}>
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }} style={{ display: 'inline-block' }}>
              <Loader size={24} />
            </motion.div>
            <div style={{ marginTop: 8, fontSize: 13 }}>AURA is thinking...</div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ padding: 12, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, color: '#ef4444', fontSize: 13, marginBottom: 16 }}>
            {error}
          </div>
        )}

        {/* Response */}
        <AnimatePresence>
          {response && !loading && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} style={{ padding: 20, background: 'rgba(201,169,110,0.06)', border: '1px solid rgba(201,169,110,0.25)', borderRadius: 14, marginBottom: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: 12, color: '#C9A96E', fontWeight: 600 }}>{INTENT_LABELS[response.intent] || '💬 Response'}</span>
                <button onClick={stopSpeaking} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.4)', display: 'flex', alignItems: 'center', gap: 4, fontSize: 11 }}>
                  <Volume2 size={12} /> Stop
                </button>
              </div>
              <div style={{ fontSize: 15, color: '#fff', lineHeight: 1.6 }}>{response.spoken_response}</div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Example Queries */}
        {!transcript && !response && (
          <div style={{ padding: 20, background: 'rgba(255,255,255,0.02)', borderRadius: 14, border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 12, fontWeight: 600 }}>Try saying:</div>
            {EXAMPLE_QUERIES.map(q => (
              <div key={q} style={{ fontSize: 13, color: 'rgba(255,255,255,0.55)', padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{q}</div>
            ))}
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div style={{ marginTop: 24 }}>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.35)', marginBottom: 12, fontWeight: 600 }}>Recent Queries</div>
            {history.slice(0, 5).map((h, i) => (
              <div key={i} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: 10, marginBottom: 8, borderLeft: '3px solid rgba(201,169,110,0.3)' }}>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', marginBottom: 4 }}>{h.transcript}</div>
                <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)' }}>{h.spoken_response.slice(0, 100)}...</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
