/**
 * Feature 9: Inventory Forecasting Dashboard
 * ML demand prediction, festival calendar, WhatsApp alerts, per-salon + corporate view.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Package, AlertTriangle, Calendar, TrendingUp, RefreshCw } from 'lucide-react';
import api from '../../config/api';

interface InventoryItem {
  id: string;
  product_name: string;
  sku: string;
  category: string;
  brand: string;
  unit_of_measure: string;
  current_stock: number;
  reorder_level: number;
  cost_per_unit: number;
  average_daily_usage: number;
  days_until_stockout: number;
}

interface FestivalEvent {
  month: number;
  day: number;
  name: string;
  demand_multiplier: number;
}

const STOCK_STATUS = (item: InventoryItem): { label: string; color: string; bg: string } => {
  const days = item.days_until_stockout || 99;
  if (days <= 3) return { label: 'Critical', color: '#ef4444', bg: 'rgba(239,68,68,0.1)' };
  if (days <= 7) return { label: 'Low', color: '#f97316', bg: 'rgba(249,115,22,0.1)' };
  if (item.current_stock <= item.reorder_level) return { label: 'Reorder', color: '#eab308', bg: 'rgba(234,179,8,0.1)' };
  return { label: 'OK', color: '#22c55e', bg: 'rgba(34,197,94,0.1)' };
};

const _FESTIVAL_DEFS = [
  { month: 10, day: 2, name: 'Gandhi Jayanti', demand_multiplier: 1.3 },
  { month: 11, day: 1, name: 'Diwali Season', demand_multiplier: 2.2 },
  { month: 12, day: 25, name: 'Christmas', demand_multiplier: 1.5 },
  { month: 12, day: 31, name: "New Year's Eve", demand_multiplier: 2.0 },
  { month: 1, day: 14, name: 'Pongal / Makar Sankranti', demand_multiplier: 1.8 },
  { month: 2, day: 14, name: "Valentine's Day", demand_multiplier: 1.6 },
  { month: 3, day: 8, name: "Women's Day", demand_multiplier: 1.9 },
];

const _today = new Date();
const UPCOMING_FESTIVALS = _FESTIVAL_DEFS.map(f => {
  let d = new Date(_today.getFullYear(), f.month - 1, f.day);
  if (d <= _today) d = new Date(_today.getFullYear() + 1, f.month - 1, f.day);
  return { ...f, days_away: Math.ceil((d.getTime() - _today.getTime()) / 86_400_000) };
}).sort((a, b) => a.days_away - b.days_away).slice(0, 4);

export default function InventoryForecast() {
  const [view, setView] = useState<'salon' | 'corporate'>('salon');
  const [search, setSearch] = useState('');

  const { data: myProfile } = useQuery<{ location_id: string }>({
    queryKey: ['staff', 'me'],
    queryFn: () => api.get('/staff/me').then(r => r.data?.data),
    staleTime: 10 * 60 * 1000,
  });
  const locationId = myProfile?.location_id ?? '';

  const inventoryUrl = view === 'corporate'
    ? '/inventory?per_page=50'
    : locationId ? `/inventory?location_id=${locationId}&per_page=50` : null;

  const { data: inventoryData, refetch, isFetching } = useQuery<{ items: InventoryItem[] }>({
    queryKey: ['inventory', view, locationId],
    queryFn: async () => {
      const res = await api.get(inventoryUrl!);
      return { items: res.data?.data?.items || [] };
    },
    enabled: view === 'corporate' || !!locationId,
  });

  const items = inventoryData?.items || [];
  const filtered = items.filter(i =>
    i.product_name?.toLowerCase().includes(search.toLowerCase()) ||
    i.category?.toLowerCase().includes(search.toLowerCase())
  );

  const critical = items.filter(i => (i.days_until_stockout || 99) <= 3);
  const low = items.filter(i => { const d = i.days_until_stockout || 99; return d > 3 && d <= 7; });
  const reorder = items.filter(i => i.current_stock <= i.reorder_level && (i.days_until_stockout || 99) > 7);

  return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F', color: '#fff', fontFamily: 'DM Sans, sans-serif', padding: '24px' }}>
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
          <div>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#C9A96E', fontFamily: 'Playfair Display, serif', display: 'flex', alignItems: 'center', gap: 10 }}>
              <Package size={24} /> Inventory Forecast
            </div>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>Demand prediction · festival calendar · stock alerts</div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <div style={{ display: 'flex', background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: 2 }}>
              {(['salon', 'corporate'] as const).map(v => (
                <button key={v} onClick={() => setView(v)} style={{ padding: '6px 16px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 600, background: view === v ? '#C9A96E' : 'transparent', color: view === v ? '#0A0A0F' : 'rgba(255,255,255,0.5)' }}>
                  {v === 'salon' ? 'My Salon' : 'All 750 Salons'}
                </button>
              ))}
            </div>
            <button onClick={() => refetch()} disabled={isFetching} style={{ padding: '8px 14px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}>
              <RefreshCw size={14} style={{ animation: isFetching ? 'spin 1s linear infinite' : 'none' }} /> Refresh
            </button>
          </div>
        </div>

        {/* Alert Summary */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 24 }}>
          {[
            { label: 'Critical (< 3 days)', count: critical.length, color: '#ef4444', bg: 'rgba(239,68,68,0.08)', icon: AlertTriangle },
            { label: 'Low Stock (< 7 days)', count: low.length, color: '#f97316', bg: 'rgba(249,115,22,0.08)', icon: TrendingUp },
            { label: 'Needs Reorder', count: reorder.length, color: '#eab308', bg: 'rgba(234,179,8,0.08)', icon: Package },
          ].map(({ label, count, color, bg, icon: Icon }) => (
            <motion.div key={label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={{ padding: 20, background: bg, border: `1px solid ${color}30`, borderRadius: 14, textAlign: 'center' }}>
              <Icon size={20} style={{ color, marginBottom: 8 }} />
              <div style={{ fontSize: 32, fontWeight: 800, color }}>{count}</div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginTop: 4 }}>{label}</div>
            </motion.div>
          ))}
        </div>

        {/* Festival Demand Alerts */}
        <div style={{ padding: 20, background: 'rgba(201,169,110,0.04)', border: '1px solid rgba(201,169,110,0.15)', borderRadius: 16, marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Calendar size={16} style={{ color: '#C9A96E' }} />
            <span style={{ fontSize: 14, fontWeight: 600, color: '#C9A96E' }}>Festival Demand Alerts</span>
          </div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {UPCOMING_FESTIVALS.map(f => (
              <div key={f.name} style={{ padding: '10px 16px', background: 'rgba(255,255,255,0.04)', borderRadius: 10, border: '1px solid rgba(255,255,255,0.06)', minWidth: 160 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: '#fff', marginBottom: 4 }}>{f.name}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 6 }}>{f.days_away} days away</div>
                <div style={{ fontSize: 11, padding: '3px 8px', background: 'rgba(234,179,8,0.15)', color: '#eab308', borderRadius: 6, display: 'inline-block', fontWeight: 700 }}>
                  Demand ×{f.demand_multiplier}
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 12, fontSize: 12, color: 'rgba(255,255,255,0.3)' }}>
            Weekly WhatsApp alerts sent to managers 14 days before each festival. Admins can add regional festivals in System Settings.
          </div>
        </div>

        {/* Inventory Table */}
        <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.06)', overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 14, fontWeight: 600, color: '#C9A96E' }}>
              {view === 'salon' ? 'Salon Inventory' : 'Network Inventory (All 750 Salons)'}
            </span>
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search products..."
              style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, color: '#fff', fontSize: 13, outline: 'none', width: 200 }}
            />
          </div>

          {filtered.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center', color: 'rgba(255,255,255,0.3)', fontSize: 13 }}>
              {items.length === 0 ? 'No inventory data yet. Products will appear here once logged.' : 'No products match your search.'}
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  {['Product', 'Category', 'Stock', 'Reorder Level', 'Days Left', 'Daily Usage', 'Status'].map(h => (
                    <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, color: 'rgba(255,255,255,0.35)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map(item => {
                  const status = STOCK_STATUS(item);
                  return (
                    <motion.tr key={item.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.02)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <td style={{ padding: '12px 16px', fontSize: 13, color: '#fff', fontWeight: 500 }}>{item.product_name}</td>
                      <td style={{ padding: '12px 16px', fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>{item.category}</td>
                      <td style={{ padding: '12px 16px', fontSize: 13, color: '#fff', fontWeight: 600 }}>{item.current_stock} {item.unit_of_measure}</td>
                      <td style={{ padding: '12px 16px', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>{item.reorder_level} {item.unit_of_measure}</td>
                      <td style={{ padding: '12px 16px', fontSize: 13, color: status.color, fontWeight: 600 }}>{item.days_until_stockout ?? '—'} days</td>
                      <td style={{ padding: '12px 16px', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>{item.average_daily_usage ?? 0} {item.unit_of_measure}/day</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 8, background: status.bg, color: status.color, fontWeight: 700 }}>{status.label}</span>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
