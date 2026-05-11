import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../lib/api'

const STATUS_CONFIG = {
  quiet:    { label: 'Walk-in friendly', color: '#34d399', bg: 'bg-emerald-500/10 border-emerald-500/20', icon: '🟢' },
  moderate: { label: 'Moderately busy',  color: '#f59e0b', bg: 'bg-amber-500/10 border-amber-500/20',   icon: '🟡' },
  busy:     { label: 'Busy today',       color: '#f87171', bg: 'bg-red-500/10 border-red-500/20',       icon: '🔴' },
}

const DAYS_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

function HeatmapCell({ value }: { value: number }) {
  const opacity = Math.max(0.08, value / 100)
  return (
    <div
      className="h-6 rounded-sm transition-all"
      style={{ backgroundColor: `rgba(201, 169, 110, ${opacity})` }}
      title={`${value}% busy`}
    />
  )
}

function NotifyModal({ locationId, onClose }: { locationId: string; onClose: () => void }) {
  const [phone, setPhone] = useState('')
  const [sent, setSent] = useState(false)

  const submit = async () => {
    await api.post('/wait-time/notify-when-ready', { location_id: locationId, phone, queue_position: 1 })
    setSent(true)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        exit={{ scale: 0.95 }}
        onClick={e => e.stopPropagation()}
        className="bg-[#0F0F1A] border border-white/10 rounded-2xl p-6 max-w-sm w-full space-y-4"
      >
        {sent ? (
          <div className="text-center space-y-2">
            <div className="text-4xl">✅</div>
            <h3 className="text-white font-semibold">We'll WhatsApp you!</h3>
            <p className="text-gray-400 text-sm">You can wait outside. We'll alert you 10 minutes before your turn.</p>
            <button onClick={onClose} className="w-full py-2 bg-[#C9A96E] text-black rounded-xl text-sm font-medium">Done</button>
          </div>
        ) : (
          <>
            <h3 className="text-white font-semibold">Get WhatsApp Alert</h3>
            <p className="text-gray-400 text-sm">We'll send you a WhatsApp message when you're 10 minutes from your turn.</p>
            <input
              value={phone}
              onChange={e => setPhone(e.target.value)}
              placeholder="+91 98765 43210"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm outline-none focus:border-[#C9A96E]"
            />
            <div className="flex gap-3">
              <button onClick={onClose} className="flex-1 py-2 border border-white/10 rounded-xl text-sm text-gray-400">Cancel</button>
              <button
                onClick={submit}
                disabled={!phone.trim()}
                className="flex-1 py-2 bg-[#C9A96E] text-black rounded-xl text-sm font-medium disabled:opacity-40"
              >
                Notify Me
              </button>
            </div>
          </>
        )}
      </motion.div>
    </motion.div>
  )
}

export default function WaitTimeDisplay() {
  const { locationId } = useParams<{ locationId: string }>()
  const [showNotify, setShowNotify] = useState(false)
  const [selectedService, setSelectedService] = useState('')

  const { data: waitData, isLoading } = useQuery({
    queryKey: ['waittime', locationId, selectedService],
    queryFn: () => api.get(`/wait-time/location/${locationId}`, {
      params: selectedService ? { service: selectedService } : {},
    }).then(r => r.data.data),
    enabled: !!locationId,
    refetchInterval: 60_000, // live update every minute
  })

  const { data: heatmapData } = useQuery({
    queryKey: ['waittime', 'heatmap', locationId],
    queryFn: () => api.get(`/wait-time/location/${locationId}/heatmap`).then(r => r.data.data),
    enabled: !!locationId,
  })

  const status = (waitData?.status ?? 'quiet') as keyof typeof STATUS_CONFIG
  const config = STATUS_CONFIG[status]
  const wait = waitData?.predicted_wait_minutes ?? 0
  const heatmap = heatmapData?.heatmap ?? {}
  const quietSlots = heatmapData?.quietest_slots ?? []

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white p-4 max-w-lg mx-auto space-y-6">
      {/* Live wait card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`border rounded-2xl p-6 text-center space-y-4 ${config.bg}`}
      >
        <div className="text-4xl">{config.icon}</div>
        {isLoading ? (
          <div className="h-16 animate-pulse bg-white/10 rounded-xl" />
        ) : (
          <>
            <div>
              <div className="text-5xl font-bold" style={{ color: config.color }}>
                {wait > 0 ? `${wait}` : '0'}
                {wait > 0 && <span className="text-2xl font-normal text-gray-400 ml-1">min</span>}
              </div>
              <div className="text-white font-medium mt-1">{waitData?.display_text ?? 'Checking…'}</div>
            </div>
            <div className="flex justify-center gap-6 text-xs text-gray-400">
              <span>Active: {waitData?.active_sessions ?? 0}</span>
              <span>Queue: {waitData?.queue_depth ?? 0}</span>
              <span>Stylists: {waitData?.available_stylists ?? 0}</span>
            </div>
            <div
              className="inline-block px-4 py-1.5 rounded-full text-sm font-medium border"
              style={{ color: config.color, borderColor: `${config.color}40` }}
            >
              {config.label}
            </div>
          </>
        )}

        {/* Service filter */}
        <div className="flex flex-wrap gap-2 justify-center pt-2">
          {['Hair Cut', 'Hair Colour', 'Facial', 'Manicure'].map(s => (
            <button
              key={s}
              onClick={() => setSelectedService(s === selectedService ? '' : s)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors
                ${selectedService === s ? 'border-[#C9A96E] bg-[#C9A96E]/10 text-[#C9A96E]' : 'border-white/10 text-gray-400 hover:border-white/30'}`}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Notify button */}
        {wait > 5 && (
          <button
            onClick={() => setShowNotify(true)}
            className="w-full py-3 bg-[#C9A96E] text-black rounded-xl text-sm font-semibold hover:bg-[#b8935a] transition-colors"
          >
            WhatsApp me when it's my turn
          </button>
        )}
      </motion.div>

      {/* Heatmap */}
      {Object.keys(heatmap).length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
          <h2 className="text-sm font-semibold text-[#C9A96E]">Weekly Busy Hours</h2>
          <div className="overflow-x-auto">
            <div className="min-w-[480px]">
              {/* Hour headers */}
              <div className="grid gap-1 mb-1" style={{ gridTemplateColumns: '36px repeat(12, 1fr)' }}>
                <div />
                {HOURS.map(h => (
                  <div key={h} className="text-center text-[10px] text-gray-600">
                    {h === 12 ? '12p' : h < 12 ? `${h}a` : `${h - 12}p`}
                  </div>
                ))}
              </div>
              {DAYS_SHORT.map(day => {
                const dayData = heatmap[day] ?? {}
                return (
                  <div key={day} className="grid gap-1 mb-1" style={{ gridTemplateColumns: '36px repeat(12, 1fr)' }}>
                    <div className="text-[10px] text-gray-500 flex items-center">{day}</div>
                    {HOURS.map(h => (
                      <HeatmapCell key={h} value={dayData[h] ?? 0} />
                    ))}
                  </div>
                )
              })}
            </div>
          </div>

          {quietSlots.length > 0 && (
            <div className="border-t border-white/10 pt-3">
              <p className="text-xs text-gray-400 mb-2">Quietest slots this week:</p>
              <div className="flex flex-wrap gap-2">
                {quietSlots.map((slot: string) => (
                  <span key={slot} className="text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-3 py-1 rounded-full">
                    {slot}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <AnimatePresence>
        {showNotify && locationId && (
          <NotifyModal locationId={locationId} onClose={() => setShowNotify(false)} />
        )}
      </AnimatePresence>
    </div>
  )
}
