/**
 * Feature 2: Skin Tone AI Bot
 * Hybrid: server-first analysis + browser MediaPipe live preview while uploading.
 * Results saved to Beauty Passport automatically.
 */
import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Upload, Sparkles, CheckCircle, AlertCircle, RefreshCw, Save } from 'lucide-react';
import api from '../../config/api';

interface SkinAnalysis {
  skin_tone: string;
  undertone: string;
  skin_type: string;
  face_shape: string;
  fitzpatrick_scale: number;
  recommended_hair_colors: string[];
  avoid_hair_colors: string[];
  recommended_lip_shades: string[];
  recommended_skincare_services: string[];
  recommended_eye_makeup: string;
  products_to_avoid_ingredients: string[];
  personalized_message: string;
  confidence_score: number;
  _dev_mode?: boolean;
}

const TONE_COLORS: Record<string, string> = {
  Fair: '#F5D5B8',
  Medium: '#D4956A',
  Dusky: '#A0674B',
  Deep: '#6B3A2A',
};

const UNDERTONE_COLORS: Record<string, string> = {
  Warm: '#E8A87C',
  Cool: '#A8C5D8',
  Neutral: '#C4A882',
};

type Step = 'capture' | 'preview' | 'analyzing' | 'result';

export default function SkinToneBot() {
  const [step, setStep] = useState<Step>('capture');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<SkinAnalysis | null>(null);
  const [savedToPassport, setSavedToPassport] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setCameraActive(true);
      }
    } catch {
      setError('Camera access denied. Please use the upload option instead.');
    }
  }, []);

  const stopCamera = useCallback(() => {
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach(t => t.stop());
    setCameraActive(false);
  }, []);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d')?.drawImage(videoRef.current, 0, 0);
    canvas.toBlob(blob => {
      if (!blob) return;
      const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });
      setImageFile(file);
      setImagePreview(canvas.toDataURL('image/jpeg'));
      setStep('preview');
      stopCamera();
    }, 'image/jpeg', 0.92);
  }, [stopCamera]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = ev => {
      setImagePreview(ev.target?.result as string);
      setStep('preview');
    };
    reader.readAsDataURL(file);
  };

  const analyzeImage = async () => {
    if (!imageFile) return;
    setStep('analyzing');
    setError(null);

    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('save_to_passport', 'true');

    try {
      const res = await api.post('/skin-tone/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000,
      });
      const data = res.data?.data;
      setAnalysis(data.analysis);
      setSavedToPassport(data.saved_to_passport);
      setStep('result');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Analysis failed. Please try again.');
      setStep('preview');
    }
  };

  const reset = () => {
    setStep('capture');
    setImageFile(null);
    setImagePreview(null);
    setAnalysis(null);
    setError(null);
    setSavedToPassport(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', color: '#fff', fontFamily: 'DM Sans, sans-serif', padding: '24px 16px' }}>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32, textAlign: 'center' }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#C9A96E', fontFamily: 'Playfair Display, serif', marginBottom: 8 }}>Skin Tone AI Bot</div>
          <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)' }}>Upload a selfie → get personalized beauty recommendations</div>
        </motion.div>

        <AnimatePresence mode="wait">
          {/* Step 1: Capture */}
          {step === 'capture' && (
            <motion.div key="capture" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {/* Camera Preview */}
              <div style={{ position: 'relative', borderRadius: 16, overflow: 'hidden', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(201,169,110,0.2)', marginBottom: 16, minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <video ref={videoRef} style={{ width: '100%', maxHeight: 400, objectFit: 'cover', display: cameraActive ? 'block' : 'none' }} autoPlay playsInline muted />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
                {!cameraActive && (
                  <div style={{ textAlign: 'center', padding: 40 }}>
                    <Camera size={48} style={{ color: 'rgba(201,169,110,0.4)', marginBottom: 16 }} />
                    <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.4)' }}>Camera off — take a selfie or upload a photo</div>
                  </div>
                )}
                {/* MediaPipe placeholder overlay — in production, MediaPipe FaceMesh shows real-time guide */}
                {cameraActive && (
                  <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
                    <div style={{ width: 200, height: 260, border: '2px solid rgba(201,169,110,0.6)', borderRadius: '50%', boxShadow: '0 0 0 4px rgba(201,169,110,0.1)' }} />
                  </div>
                )}
              </div>

              {error && (
                <div style={{ padding: 12, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, color: '#ef4444', fontSize: 13, marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
                  <AlertCircle size={16} /> {error}
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {!cameraActive ? (
                  <button onClick={startCamera} style={{ padding: '14px 20px', background: 'linear-gradient(135deg, #C9A96E, #8B6914)', border: 'none', borderRadius: 12, color: '#fff', fontWeight: 700, cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                    <Camera size={18} /> Use Camera
                  </button>
                ) : (
                  <button onClick={capturePhoto} style={{ padding: '14px 20px', background: 'linear-gradient(135deg, #C9A96E, #8B6914)', border: 'none', borderRadius: 12, color: '#fff', fontWeight: 700, cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                    📸 Capture
                  </button>
                )}
                <button onClick={() => fileInputRef.current?.click()} style={{ padding: '14px 20px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(201,169,110,0.3)', borderRadius: 12, color: '#C9A96E', fontWeight: 700, cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  <Upload size={18} /> Upload Photo
                </button>
                <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileUpload} />
              </div>

              <div style={{ marginTop: 16, padding: 12, background: 'rgba(255,255,255,0.03)', borderRadius: 10, fontSize: 12, color: 'rgba(255,255,255,0.4)', textAlign: 'center' }}>
                🔒 Your photo is analysed securely and not stored on our servers. Results are saved only to your Beauty Passport.
              </div>
            </motion.div>
          )}

          {/* Step 2: Preview */}
          {step === 'preview' && imagePreview && (
            <motion.div key="preview" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <img src={imagePreview} alt="Preview" style={{ width: '100%', maxHeight: 400, objectFit: 'cover', borderRadius: 16, marginBottom: 16, border: '1px solid rgba(201,169,110,0.2)' }} />
              {error && (
                <div style={{ padding: 12, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, color: '#ef4444', fontSize: 13, marginBottom: 16 }}>
                  {error}
                </div>
              )}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <button onClick={analyzeImage} style={{ padding: '14px 20px', background: 'linear-gradient(135deg, #C9A96E, #8B6914)', border: 'none', borderRadius: 12, color: '#fff', fontWeight: 700, cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  <Sparkles size={18} /> Analyse My Skin
                </button>
                <button onClick={reset} style={{ padding: '14px 20px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: '#fff', cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  <RefreshCw size={18} /> Retake
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Analyzing */}
          {step === 'analyzing' && (
            <motion.div key="analyzing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ textAlign: 'center', padding: '60px 20px' }}>
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} style={{ display: 'inline-block', marginBottom: 24 }}>
                <Sparkles size={48} style={{ color: '#C9A96E' }} />
              </motion.div>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#C9A96E', marginBottom: 8 }}>Analysing your skin tone...</div>
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>Gemini Vision is mapping your skin tone, undertone, and face shape</div>
            </motion.div>
          )}

          {/* Step 4: Results */}
          {step === 'result' && analysis && (
            <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {/* Saved badge */}
              {savedToPassport && (
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ padding: '10px 16px', background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.3)', borderRadius: 10, color: '#22c55e', fontSize: 13, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Save size={16} /> Results saved to your Beauty Passport
                </motion.div>
              )}

              {/* Tone + Undertone */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                <div style={{ padding: 20, background: 'rgba(255,255,255,0.03)', borderRadius: 14, border: '1px solid rgba(201,169,110,0.15)', textAlign: 'center' }}>
                  <div style={{ width: 48, height: 48, borderRadius: '50%', background: TONE_COLORS[analysis.skin_tone] || '#D4956A', margin: '0 auto 12px', border: '3px solid rgba(201,169,110,0.4)' }} />
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#fff', marginBottom: 4 }}>{analysis.skin_tone}</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>Skin Tone · Fitzpatrick {analysis.fitzpatrick_scale}</div>
                </div>
                <div style={{ padding: 20, background: 'rgba(255,255,255,0.03)', borderRadius: 14, border: '1px solid rgba(201,169,110,0.15)', textAlign: 'center' }}>
                  <div style={{ width: 48, height: 48, borderRadius: '50%', background: UNDERTONE_COLORS[analysis.undertone] || '#C4A882', margin: '0 auto 12px', border: '3px solid rgba(201,169,110,0.4)' }} />
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#fff', marginBottom: 4 }}>{analysis.undertone}</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>Undertone · {analysis.face_shape} Face</div>
                </div>
              </div>

              {/* Personalized Message */}
              <div style={{ padding: 16, background: 'rgba(201,169,110,0.06)', border: '1px solid rgba(201,169,110,0.2)', borderRadius: 12, marginBottom: 16 }}>
                <div style={{ fontSize: 13, color: '#C9A96E', lineHeight: 1.6 }}>✨ {analysis.personalized_message}</div>
              </div>

              {/* Recommendations Grid */}
              {[
                { label: '✅ Recommended Hair Colours', items: analysis.recommended_hair_colors, color: '#22c55e', bg: 'rgba(34,197,94,0.08)' },
                { label: '❌ Avoid Hair Colours', items: analysis.avoid_hair_colors, color: '#ef4444', bg: 'rgba(239,68,68,0.08)' },
                { label: '💄 Lip Shades', items: analysis.recommended_lip_shades, color: '#ec4899', bg: 'rgba(236,72,153,0.08)' },
                { label: '💆 Skincare Services', items: analysis.recommended_skincare_services, color: '#C9A96E', bg: 'rgba(201,169,110,0.08)' },
              ].map(({ label, items, color, bg }) => (
                <div key={label} style={{ padding: 16, background: bg, borderRadius: 12, marginBottom: 12 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color, marginBottom: 10 }}>{label}</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {(items || []).map(item => (
                      <span key={item} style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(255,255,255,0.06)', borderRadius: 6, color: '#fff' }}>{item}</span>
                    ))}
                  </div>
                </div>
              ))}

              {/* Eye Makeup */}
              {analysis.recommended_eye_makeup && (
                <div style={{ padding: 14, background: 'rgba(255,255,255,0.03)', borderRadius: 12, marginBottom: 16 }}>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 4 }}>👁 Eye Makeup</div>
                  <div style={{ fontSize: 13, color: '#fff' }}>{analysis.recommended_eye_makeup}</div>
                </div>
              )}

              {analysis._dev_mode && (
                <div style={{ padding: 10, background: 'rgba(255,193,7,0.08)', borderRadius: 8, fontSize: 11, color: 'rgba(255,193,7,0.7)', marginBottom: 12 }}>
                  ⚠️ Dev mode: AI provider not configured. Showing sample analysis.
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 8 }}>
                <button onClick={reset} style={{ padding: '12px 20px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: '#fff', cursor: 'pointer', fontSize: 14, fontWeight: 600 }}>
                  Try Another Photo
                </button>
                <a href="/app/book" style={{ padding: '12px 20px', background: 'linear-gradient(135deg, #C9A96E, #8B6914)', borderRadius: 12, color: '#fff', fontSize: 14, fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                  Book Recommended Service
                </a>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
