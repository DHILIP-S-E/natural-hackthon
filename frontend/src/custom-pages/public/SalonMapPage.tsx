/**
 * Feature 3: Smart Salon Map — public, no login required.
 * Google Maps with live availability pins, busy badge, multi-mode routing.
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Search, Navigation, Phone, Clock, Users, Zap, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const MAPS_KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY || '';

interface Salon {
  id: string;
  name: string;
  city: string;
  address: string;
  phone: string;
  lat: number;
  lng: number;
  is_active: boolean;
  services_available: string[];
  staff_on_duty: number;
  is_busy: boolean;
  busy_label: string;
  open_time: string;
  close_time: string;
  rating: number;
}

export default function SalonMapPage() {
  const mapRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapInstance = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markersRef = useRef<any[]>([]);

  const [salons, setSalons] = useState<Salon[]>([]);
  const [filtered, setFiltered] = useState<Salon[]>([]);
  const [serviceFilters, setServiceFilters] = useState<string[]>(['All']);
  const [selected, setSelected] = useState<Salon | null>(null);
  const [search, setSearch] = useState('');
  const [serviceFilter, setServiceFilter] = useState('All');
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mapsLoaded, setMapsLoaded] = useState(false);
  const [routeMode, setRouteMode] = useState<'DRIVING' | 'TRANSIT' | 'WALKING' | 'BICYCLING'>('DRIVING');

  // Load Google Maps script
  useEffect(() => {
    if ((window as any).google?.maps) { setMapsLoaded(true); return; }
    if (!MAPS_KEY) { setMapsLoaded(true); return; }
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${MAPS_KEY}&libraries=places`;
    script.async = true;
    script.onload = () => setMapsLoaded(true);
    document.head.appendChild(script);
  }, []);

  // Fetch service filters from config
  useEffect(() => {
    axios.get(`${API_BASE}/config/service-filters`).then(res => {
      const filters = res.data?.data?.filters;
      if (Array.isArray(filters)) setServiceFilters(filters);
    }).catch(() => {});
  }, []);

  // Fetch salons
  useEffect(() => {
    setLoading(true);
    setError(null);
    axios.get(`${API_BASE}/locations?per_page=100`).then(res => {
      const data = res.data?.data?.locations || [];
      const enriched: Salon[] = data
        .filter((loc: any) => loc.latitude && loc.longitude)
        .map((loc: any) => ({
          id: loc.id,
          name: loc.name,
          city: loc.city || '',
          address: loc.address || loc.city || '',
          phone: loc.phone || '',
          lat: parseFloat(loc.latitude),
          lng: parseFloat(loc.longitude),
          is_active: loc.is_active !== false,
          services_available: loc.services_available || [],
          staff_on_duty: loc.staff_on_duty ?? null,
          is_busy: loc.is_busy ?? false,
          busy_label: loc.busy_label || (loc.is_busy ? 'Busy today' : 'Walk-in friendly'),
          open_time: loc.operating_hours?.Monday?.open || '',
          close_time: loc.operating_hours?.Monday?.close || '',
          rating: loc.average_rating ?? null,
        }));
      setSalons(enriched);
      setFiltered(enriched);
    }).catch(() => {
      setError('Unable to load salon locations. Please try again later.');
    }).finally(() => setLoading(false));
  }, []);

  // Get user location
  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      pos => setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => setUserLocation({ lat: 13.0827, lng: 80.2707 })
    );
  }, []);

  // Initialize map
  useEffect(() => {
    if (!mapsLoaded || !mapRef.current || !(window as any).google?.maps) return;
    const center = userLocation || { lat: 13.0827, lng: 80.2707 };
    mapInstance.current = new (window as any).google.maps.Map(mapRef.current, {
      center,
      zoom: 12,
      styles: [
        { featureType: 'all', elementType: 'geometry', stylers: [{ color: '#1a1a2e' }] },
        { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#0f0f23' }] },
        { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#2d2d4e' }] },
        { featureType: 'poi', stylers: [{ visibility: 'off' }] },
        { featureType: 'all', elementType: 'labels.text.fill', stylers: [{ color: '#C9A96E' }] },
      ],
    });
  }, [mapsLoaded, userLocation]);

  // Place markers
  useEffect(() => {
    const g = (window as any).google;
    if (!mapInstance.current || !g?.maps) return;
    markersRef.current.forEach(m => m.setMap(null));
    markersRef.current = [];

    filtered.forEach(salon => {
      const marker = new g.maps.Marker({
        position: { lat: salon.lat, lng: salon.lng },
        map: mapInstance.current!,
        title: salon.name,
        icon: {
          path: g.maps.SymbolPath.CIRCLE,
          scale: salon.is_busy ? 10 : 8,
          fillColor: salon.is_busy ? '#ef4444' : '#22c55e',
          fillOpacity: 1,
          strokeColor: '#C9A96E',
          strokeWeight: 2,
        },
      });
      marker.addListener('click', () => setSelected(salon));
      markersRef.current.push(marker);
    });
  }, [filtered, mapsLoaded]);

  // Filter salons
  useEffect(() => {
    let result = salons;
    if (search) {
      result = result.filter(s =>
        s.name.toLowerCase().includes(search.toLowerCase()) ||
        s.city.toLowerCase().includes(search.toLowerCase())
      );
    }
    if (serviceFilter !== 'All') {
      result = result.filter(s => s.services_available.some(sv =>
        sv.toLowerCase().includes(serviceFilter.toLowerCase())
      ));
    }
    setFiltered(result);
  }, [search, serviceFilter, salons]);

  const openDirections = useCallback((salon: Salon) => {
    const dest = `${salon.lat},${salon.lng}`;
    const origin = userLocation ? `${userLocation.lat},${userLocation.lng}` : '';
    const modes: Record<string, string> = {
      DRIVING: 'driving', TRANSIT: 'transit', WALKING: 'walking', BICYCLING: 'bicycling',
    };
    const url = `https://www.google.com/maps/dir/?api=1&destination=${dest}&origin=${origin}&travelmode=${modes[routeMode]}`;
    window.open(url, '_blank');
  }, [userLocation, routeMode]);

  return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', color: '#fff', fontFamily: 'DM Sans, sans-serif' }}>
      {/* Header */}
      <div style={{ background: 'rgba(201,169,110,0.08)', borderBottom: '1px solid rgba(201,169,110,0.15)', padding: '16px 24px', display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ width: 36, height: 36, borderRadius: 8, background: 'linear-gradient(135deg, #C9A96E, #8B6914)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <MapPin size={18} color="#fff" />
        </div>
        <div>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#C9A96E', fontFamily: 'Playfair Display, serif' }}>Find a Naturals Salon</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)' }}>{filtered.length} salons near you</div>
        </div>
      </div>

      {/* Search + Filters */}
      <div style={{ padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'rgba(255,255,255,0.4)' }} />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by city or salon name..."
            style={{ width: '100%', padding: '10px 12px 10px 36px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(201,169,110,0.2)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }}>
          {serviceFilters.map(f => (
            <button key={f} onClick={() => setServiceFilter(f)} style={{ padding: '6px 14px', borderRadius: 20, border: 'none', cursor: 'pointer', whiteSpace: 'nowrap', fontSize: 12, fontWeight: 600, background: serviceFilter === f ? '#C9A96E' : 'rgba(255,255,255,0.06)', color: serviceFilter === f ? '#0A0A0F' : 'rgba(255,255,255,0.6)', transition: 'all 0.2s' }}>
              {f}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', height: 'calc(100vh - 180px)' }}>
        {/* Sidebar: Salon List */}
        <div style={{ width: 340, overflowY: 'auto', borderRight: '1px solid rgba(255,255,255,0.06)' }}>
          {loading ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'rgba(255,255,255,0.4)' }}>Loading salons...</div>
          ) : error ? (
            <div style={{ padding: 24, textAlign: 'center', color: '#ef4444', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
              <AlertCircle size={32} style={{ opacity: 0.6 }} />
              <div style={{ fontSize: 13 }}>{error}</div>
            </div>
          ) : filtered.length === 0 ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'rgba(255,255,255,0.4)', fontSize: 13 }}>
              No salons found matching your search.
            </div>
          ) : filtered.map(salon => (
            <motion.div
              key={salon.id}
              whileHover={{ backgroundColor: 'rgba(201,169,110,0.06)' }}
              onClick={() => { setSelected(salon); mapInstance.current?.panTo({ lat: salon.lat, lng: salon.lng }); }}
              style={{ padding: '14px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)', cursor: 'pointer', background: selected?.id === salon.id ? 'rgba(201,169,110,0.08)' : 'transparent', borderLeft: selected?.id === salon.id ? '3px solid #C9A96E' : '3px solid transparent' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#fff' }}>{salon.name}</div>
                <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 10, background: salon.is_busy ? 'rgba(239,68,68,0.15)' : 'rgba(34,197,94,0.15)', color: salon.is_busy ? '#ef4444' : '#22c55e', fontWeight: 600 }}>
                  {salon.busy_label}
                </span>
              </div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', marginBottom: 6 }}>{salon.address}</div>
              <div style={{ display: 'flex', gap: 12, fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
                {salon.staff_on_duty !== null && (
                  <span><Users size={10} style={{ marginRight: 3 }} />{salon.staff_on_duty} staff on duty</span>
                )}
                {salon.rating !== null && <span>★ {salon.rating.toFixed(1)}</span>}
              </div>
              {salon.services_available.length > 0 && (
                <div style={{ display: 'flex', gap: 4, marginTop: 8, flexWrap: 'wrap' }}>
                  {salon.services_available.slice(0, 3).map(sv => (
                    <span key={sv} style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(201,169,110,0.1)', color: '#C9A96E', borderRadius: 4 }}>{sv}</span>
                  ))}
                  {salon.services_available.length > 3 && (
                    <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.35)' }}>+{salon.services_available.length - 3} more</span>
                  )}
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Map */}
        <div style={{ flex: 1, position: 'relative' }}>
          <div ref={mapRef} style={{ width: '100%', height: '100%', background: '#1a1a2e' }}>
            {!MAPS_KEY && (
              <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'rgba(255,255,255,0.4)' }}>
                <MapPin size={48} style={{ opacity: 0.3 }} />
                <div style={{ fontSize: 14 }}>Add VITE_GOOGLE_MAPS_KEY to .env to enable the map</div>
                <div style={{ fontSize: 12, opacity: 0.6 }}>{filtered.length} salons loaded — select one from the list</div>
              </div>
            )}
          </div>

          {/* Selected Salon Detail Panel */}
          {selected && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ position: 'absolute', bottom: 16, left: '50%', transform: 'translateX(-50%)', width: '90%', maxWidth: 480, background: 'rgba(10,10,15,0.96)', border: '1px solid rgba(201,169,110,0.3)', borderRadius: 16, padding: 20, backdropFilter: 'blur(20px)' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: '#C9A96E' }}>{selected.name}</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginTop: 2 }}>{selected.address}</div>
                </div>
                <button onClick={() => setSelected(null)} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer', fontSize: 18 }}>✕</button>
              </div>

              <div style={{ display: 'flex', gap: 16, marginBottom: 14, fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>
                {selected.open_time && selected.close_time && (
                  <span><Clock size={12} style={{ marginRight: 4 }} />{selected.open_time} – {selected.close_time}</span>
                )}
                {selected.staff_on_duty !== null && (
                  <span><Users size={12} style={{ marginRight: 4 }} />{selected.staff_on_duty} on duty</span>
                )}
                {selected.rating !== null && <span>★ {selected.rating.toFixed(1)}</span>}
              </div>

              {/* Route mode selector */}
              <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
                {[{ mode: 'DRIVING', label: '🚗 Drive' }, { mode: 'TRANSIT', label: '🚌 Transit' }, { mode: 'WALKING', label: '🚶 Walk' }, { mode: 'BICYCLING', label: '🚲 Bike' }].map(({ mode, label }) => (
                  <button key={mode} onClick={() => setRouteMode(mode as any)} style={{ flex: 1, padding: '6px 4px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 11, fontWeight: 600, background: routeMode === mode ? '#C9A96E' : 'rgba(255,255,255,0.08)', color: routeMode === mode ? '#0A0A0F' : 'rgba(255,255,255,0.6)' }}>
                    {label}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => openDirections(selected)} style={{ flex: 1, padding: '10px 16px', background: 'linear-gradient(135deg, #C9A96E, #8B6914)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: 'pointer', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                  <Navigation size={14} /> Get Directions
                </button>
                {selected.phone && (
                  <a href={`tel:${selected.phone}`} style={{ padding: '10px 16px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}>
                    <Phone size={14} /> Call
                  </a>
                )}
                <a href="/app/book" style={{ padding: '10px 16px', background: 'rgba(201,169,110,0.1)', border: '1px solid rgba(201,169,110,0.3)', borderRadius: 10, color: '#C9A96E', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600 }}>
                  <Zap size={14} /> Book
                </a>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
