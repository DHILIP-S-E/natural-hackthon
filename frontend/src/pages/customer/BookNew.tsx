import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Clock, MapPin, Search, Star, ChevronRight, CheckCircle, Loader2 } from 'lucide-react';
import api from '../../config/api';

const CATEGORIES = ['All', 'Hair', 'Skin', 'Nail', 'Makeup', 'Wellness'];

export default function BookNew() {
  const [step, setStep] = useState(1); // 1=service, 2=location/time, 3=confirm
  const [search, setSearch] = useState('');
  const [selectedCat, setSelectedCat] = useState('All');
  const [selectedService, setSelectedService] = useState<any>(null);
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedLocationId, setSelectedLocationId] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [bookingSuccess, setBookingSuccess] = useState(false);

  // Fetch services from API
  const { data: apiServices, isLoading: servicesLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => api.get('/services').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.services || d?.items || [];
    }),
  });

  // Fetch locations from API
  const { data: apiLocations, isLoading: locationsLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: () => api.get('/locations').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.locations || d?.items || [];
    }),
  });

  // Map API services to the shape the UI expects
  const SERVICES = (apiServices || []).map((s: any) => ({
    id: s.id,
    name: s.name,
    category: s.category || 'Other',
    duration: s.duration_minutes ?? s.duration ?? 30,
    price: Number(s.base_price ?? s.price) || 0,
    rating: s.rating ?? 4.5,
    tags: s.tags || [],
  }));

  // Map API locations to the shape the UI expects
  const LOCATIONS = (apiLocations || []).filter((l: any) => l.is_active !== false).map((l: any) => ({
    id: l.id,
    name: l.name || l.code || '',
  }));

  // Booking submission mutation
  const bookingMutation = useMutation({
    mutationFn: (data: any) => api.post('/bookings', data).then(r => r.data),
    onSuccess: () => {
      setBookingSuccess(true);
    },
  });

  const filtered = SERVICES.filter((s: any) => {
    if (selectedCat !== 'All' && s.category.toLowerCase() !== selectedCat.toLowerCase()) return false;
    if (search && !(s.name ?? '').toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  // Build ISO datetime from date + time selection
  const buildScheduledAt = () => {
    if (!selectedDate || !selectedTime) return '';
    // Parse time like "2:00 PM" to 24h
    const [time, period] = selectedTime.split(' ');
    const [hStr, mStr] = time.split(':');
    let hours = parseInt(hStr);
    if (period === 'PM' && hours !== 12) hours += 12;
    if (period === 'AM' && hours === 12) hours = 0;
    return `${selectedDate}T${String(hours).padStart(2, '0')}:${mStr}:00`;
  };

  const handleConfirmBooking = () => {
    if (!selectedService) return;

    const bookingData = {
      service_id: selectedService.id,
      location_id: selectedLocationId || undefined,
      scheduled_at: buildScheduledAt(),
      base_price: selectedService.price,
      source: 'app',
    };

    bookingMutation.mutate(bookingData);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)', maxWidth: 700, margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.75rem' }}>Book a Service</h1>

      {/* Progress */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        {['Select Service', 'Choose Time', 'Confirm'].map((s, i) => (
          <div key={i} style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ height: 4, background: step > i ? 'var(--gold)' : 'var(--border-subtle)', borderRadius: 2, marginBottom: 6, transition: 'background 0.3s' }} />
            <span style={{ fontSize: '0.7rem', color: step > i ? 'var(--gold)' : 'var(--text-muted)' }}>{s}</span>
          </div>
        ))}
      </div>

      {step === 1 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div style={{ position: 'relative', marginBottom: 16 }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: 'var(--text-muted)' }} />
            <input className="input" placeholder="Search services..." value={search} onChange={e => setSearch(e.target.value)}
              style={{ paddingLeft: 36 }} />
          </div>
          <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
            {CATEGORIES.map(c => (
              <button key={c} onClick={() => setSelectedCat(c)}
                className={`btn ${selectedCat === c ? 'btn-teal' : 'btn-ghost'} btn-sm`}>{c}</button>
            ))}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {servicesLoading && !apiServices ? (
              [...Array(4)].map((_, i) => (
                <div key={i} className="card" style={{ padding: '14px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ width: 150, height: 16, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4, marginBottom: 6 }} />
                    <div style={{ width: 200, height: 12, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} />
                  </div>
                  <div style={{ width: 60, height: 16, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 4 }} />
                </div>
              ))
            ) : filtered.length === 0 ? (
              <div className="card" style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No services found.
              </div>
            ) : filtered.map((s: any) => (
              <div key={s.id} onClick={() => { setSelectedService(s); setStep(2); }}
                className="card" style={{ padding: '14px 18px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                    {s.name}
                    {s.tags?.map((t: string) => <span key={t} className="badge badge-gold" style={{ padding: '1px 6px', fontSize: '0.6rem' }}>{t}</span>)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2, display: 'flex', gap: 10 }}>
                    <span><Clock size={10} /> {s.duration} min</span>
                    <span><Star size={10} /> {s.rating}</span>
                    <span>{s.category}</span>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--gold)' }}>₹{(Number(s.price) || 0).toLocaleString()}</span>
                  <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {step === 2 && selectedService && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <div className="card" style={{ marginBottom: 16, padding: '12px 18px', background: 'var(--bg-surface)' }}>
            <div style={{ fontWeight: 600 }}>{selectedService.name}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{selectedService.duration} min · ₹{selectedService.price}</div>
          </div>
          <h4 style={{ marginBottom: 12 }}>Choose Location</h4>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
            {locationsLoading && !apiLocations ? (
              [...Array(3)].map((_, i) => (
                <div key={i} style={{ width: 100, height: 36, background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', borderRadius: 'var(--radius-sm)' }} />
              ))
            ) : LOCATIONS.length === 0 ? (
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No locations available.</span>
            ) : LOCATIONS.map((l: any) => (
              <button key={l.id} onClick={() => { setSelectedLocation(l.name); setSelectedLocationId(l.id); }}
                className={`btn ${selectedLocation === l.name ? 'btn-teal' : 'btn-ghost'}`}><MapPin size={12} /> {l.name}</button>
            ))}
          </div>
          <h4 style={{ marginBottom: 12 }}>Choose Date & Time</h4>
          <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
            <input type="date" className="input" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} style={{ flex: 1 }} />
            <select className="input" value={selectedTime} onChange={e => setSelectedTime(e.target.value)} style={{ flex: 1 }}>
              <option value="">Select time</option>
              {['10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM'].map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost" onClick={() => setStep(1)}>Back</button>
            <button className="btn btn-primary" disabled={!selectedLocation || !selectedDate || !selectedTime}
              onClick={() => setStep(3)}>Continue</button>
          </div>
        </motion.div>
      )}

      {step === 3 && selectedService && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          {bookingSuccess ? (
            <div className="card" style={{ padding: '48px 24px', textAlign: 'center' }}>
              <CheckCircle size={48} style={{ color: 'var(--success)', marginBottom: 16 }} />
              <h3 style={{ marginBottom: 8 }}>Booking Confirmed!</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
                Your {selectedService.name} at Naturals {selectedLocation} has been booked for {selectedDate} at {selectedTime}.
              </p>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
                <a href="/app/bookings" className="btn btn-primary">View My Bookings</a>
                <button className="btn btn-ghost" onClick={() => { setStep(1); setSelectedService(null); setSelectedLocation(''); setSelectedLocationId(''); setSelectedDate(''); setSelectedTime(''); setBookingSuccess(false); }}>
                  Book Another
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="card" style={{ marginBottom: 16 }}>
                <h4 style={{ marginBottom: 16 }}>Booking Summary</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {[
                    { label: 'Service', value: selectedService.name },
                    { label: 'Location', value: `Naturals ${selectedLocation}` },
                    { label: 'Date', value: selectedDate },
                    { label: 'Time', value: selectedTime },
                    { label: 'Duration', value: `${selectedService.duration} min` },
                    { label: 'Price', value: `₹${(Number(selectedService.price) || 0).toLocaleString()}` },
                  ].map((r, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{r.label}</span>
                      <span style={{ fontWeight: 500, fontSize: '0.85rem' }}>{r.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {bookingMutation.isError && (
                <div style={{ marginBottom: 16, padding: '12px 16px', background: 'rgba(231,111,111,0.08)', border: '1px solid rgba(231,111,111,0.2)', borderRadius: 'var(--radius-md)', color: 'var(--error)', fontSize: '0.85rem' }}>
                  Failed to create booking. Please try again.
                </div>
              )}

              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-ghost" onClick={() => setStep(2)} disabled={bookingMutation.isPending}>Back</button>
                <button
                  className="btn btn-primary"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
                  onClick={handleConfirmBooking}
                  disabled={bookingMutation.isPending}
                >
                  {bookingMutation.isPending ? (
                    <>
                      <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> Booking...
                    </>
                  ) : (
                    <>Confirm Booking · ₹{(Number(selectedService.price) || 0).toLocaleString()}</>
                  )}
                </button>
              </div>
            </>
          )}
        </motion.div>
      )}
    </div>
  );
}
