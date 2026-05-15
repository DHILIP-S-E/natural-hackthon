import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useParams, useSearchParams } from 'react-router-dom'
import api from '../../config/api'

const schema = z.object({
  hair_type: z.string().optional(),
  hair_texture: z.string().optional(),
  scalp_condition: z.string().optional(),
  skin_type: z.string().optional(),
  known_allergies: z.string().optional(),
  product_sensitivities: z.string().optional(),
  visit_goal: z.string().optional(),
  budget_preference: z.string().optional(),
  health_conditions: z.string().optional(),
  is_pregnant: z.boolean().default(false),
  is_breastfeeding: z.boolean().default(false),
  allergy_declaration_signed: z.boolean().refine(v => v === true, {
    message: 'You must sign the allergy declaration to proceed',
  }),
})

type FormData = z.infer<typeof schema>

const DEFAULT_OPTIONS = {
  steps: ['Hair & Scalp', 'Skin', 'Allergies', 'Visit Intent', 'Health & Sign'],
  hair_types: ['Straight', 'Wavy', 'Curly', 'Coily'],
  scalp_conditions: ['Normal', 'Oily', 'Dry', 'Sensitive'],
  skin_types: ['Oily', 'Dry', 'Combination', 'Normal', 'Sensitive'],
  visit_goals: ['Maintain current look', 'Try something new', 'Special occasion', 'Repair & restore'],
  budgets: ['Budget', 'Standard', 'Premium'],
}

function OptionGrid({ options, selected, onSelect }: { options: string[]; selected?: string; onSelect: (v: string) => void }) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {options.map(opt => (
        <button
          key={opt}
          type="button"
          onClick={() => onSelect(opt)}
          className={`py-2 px-3 rounded-xl text-sm border transition-all
            ${selected === opt
              ? 'border-[#C9A96E] bg-[#C9A96E]/10 text-[#C9A96E] font-medium'
              : 'border-white/10 bg-white/5 text-gray-300 hover:border-white/30'}`}
        >
          {opt}
        </button>
      ))}
    </div>
  )
}

export default function ConsultationForm() {
  const { bookingId } = useParams<{ bookingId: string }>()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const [step, setStep] = useState(0)

  const { data: opts } = useQuery({
    queryKey: ['config', 'consultation-options'],
    queryFn: () => api.get('/config/consultation-options').then(r => r.data?.data),
    staleTime: Infinity,
  })
  const options = opts ?? DEFAULT_OPTIONS
  const STEPS = options.steps
  const HAIR_TYPES = options.hair_types
  const SCALP_CONDITIONS = options.scalp_conditions
  const SKIN_TYPES = options.skin_types
  const VISIT_GOALS = options.visit_goals
  const BUDGETS = options.budgets

  const { data: bookingInfo } = useQuery({
    queryKey: ['consultation-info', bookingId],
    queryFn: () => api.get(`/consultation/booking/${bookingId}/info`).then(r => r.data.data),
    enabled: !!bookingId,
    retry: false,
  })
  const [done, setDone] = useState(false)
  const [result, setResult] = useState<any>(null)

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { is_pregnant: false, is_breastfeeding: false, allergy_declaration_signed: false },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) => api.post('/consultation/submit', {
      booking_id: bookingId,
      token,
      ...data,
      known_allergies: data.known_allergies?.split(',').map(s => s.trim()).filter(Boolean) ?? [],
      product_sensitivities: data.product_sensitivities?.split(',').map(s => s.trim()).filter(Boolean) ?? [],
      health_conditions: data.health_conditions?.split(',').map(s => s.trim()).filter(Boolean) ?? [],
    }).then(r => r.data.data),
    onSuccess: (res) => {
      setResult(res)
      setDone(true)
    },
  })

  const vals = watch()

  if (done && result) {
    const risk = result.allergy_check?.risk_level ?? 'LOW'
    const riskColor = risk === 'BLOCK' ? 'text-red-400' : risk === 'HIGH' ? 'text-orange-400' : risk === 'CAUTION' ? 'text-yellow-400' : 'text-emerald-400'
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center p-4">
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="max-w-md w-full bg-white/5 border border-white/10 rounded-2xl p-8 text-center space-y-4"
        >
          <div className="text-5xl">💆</div>
          <h2 className="text-xl font-bold text-white">All set! Your stylist has been briefed.</h2>
          <p className="text-gray-400 text-sm">Your consultation is complete. We'll tailor your session just for you.</p>
          {result.allergy_check?.risk_level && result.allergy_check.risk_level !== 'LOW' && (
            <div className="bg-white/5 rounded-xl p-4 text-left">
              <p className="text-xs text-gray-500 mb-1">Allergy assessment</p>
              <p className={`text-sm font-bold ${riskColor}`}>{risk} — {result.allergy_check.reason ?? 'See stylist for details'}</p>
              {result.allergy_check.safe_alternative && (
                <p className="text-xs text-gray-400 mt-1">💡 {result.allergy_check.safe_alternative}</p>
              )}
            </div>
          )}
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="text-[#C9A96E] text-2xl font-bold mb-1">Pre-Visit Consultation</div>
          {bookingInfo ? (
            <div className="mt-2 space-y-0.5">
              <p className="text-white font-medium text-sm">{bookingInfo.customer_name || 'Welcome!'}</p>
              <p className="text-gray-400 text-xs">{bookingInfo.service_name} · {bookingInfo.location_name}</p>
              {bookingInfo.scheduled_at && (
                <p className="text-gray-500 text-xs">{new Date(bookingInfo.scheduled_at).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</p>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">2 minutes to personalise your experience</p>
          )}
        </div>

        {/* Progress */}
        <div className="flex gap-1">
          {STEPS.map((s, i) => (
            <div key={s} className={`h-1 flex-1 rounded-full transition-colors
              ${i <= step ? 'bg-[#C9A96E]' : 'bg-white/10'}`} />
          ))}
        </div>
        <p className="text-xs text-gray-500 text-center">{STEPS[step]}</p>

        <form onSubmit={handleSubmit(data => mutation.mutate(data))}>
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-5"
            >
              {step === 0 && (
                <>
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Hair type</label>
                    <OptionGrid options={HAIR_TYPES} selected={vals.hair_type} onSelect={v => setValue('hair_type', v)} />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Scalp condition</label>
                    <OptionGrid options={SCALP_CONDITIONS} selected={vals.scalp_condition} onSelect={v => setValue('scalp_condition', v)} />
                  </div>
                </>
              )}

              {step === 1 && (
                <div>
                  <label className="text-xs text-gray-400 mb-2 block">Skin type</label>
                  <OptionGrid options={SKIN_TYPES} selected={vals.skin_type} onSelect={v => setValue('skin_type', v)} />
                </div>
              )}

              {step === 2 && (
                <>
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Known allergies (comma-separated)</label>
                    <textarea
                      {...register('known_allergies')}
                      placeholder="e.g. ammonia, PPD, fragrance"
                      className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm text-white placeholder-gray-600 resize-none h-20 focus:border-[#C9A96E] outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Product sensitivities</label>
                    <textarea
                      {...register('product_sensitivities')}
                      placeholder="e.g. sulphates, parabens"
                      className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm text-white placeholder-gray-600 resize-none h-20 focus:border-[#C9A96E] outline-none"
                    />
                  </div>
                </>
              )}

              {step === 3 && (
                <>
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Visit goal</label>
                    <OptionGrid options={VISIT_GOALS} selected={vals.visit_goal} onSelect={v => setValue('visit_goal', v)} />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Budget preference</label>
                    <OptionGrid options={BUDGETS} selected={vals.budget_preference} onSelect={v => setValue('budget_preference', v)} />
                  </div>
                </>
              )}

              {step === 4 && (
                <>
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Health conditions (optional)</label>
                    <textarea
                      {...register('health_conditions')}
                      placeholder="e.g. diabetes, thyroid condition"
                      className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm text-white placeholder-gray-600 resize-none h-16 focus:border-[#C9A96E] outline-none"
                    />
                  </div>
                  <div className="flex items-center gap-3">
                    <input type="checkbox" id="pregnant" {...register('is_pregnant')} className="accent-[#C9A96E] w-4 h-4" />
                    <label htmlFor="pregnant" className="text-sm text-gray-300">I am currently pregnant</label>
                  </div>
                  <div className="flex items-center gap-3">
                    <input type="checkbox" id="bf" {...register('is_breastfeeding')} className="accent-[#C9A96E] w-4 h-4" />
                    <label htmlFor="bf" className="text-sm text-gray-300">I am breastfeeding</label>
                  </div>

                  {/* Allergy declaration */}
                  <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4 space-y-3">
                    <p className="text-xs text-orange-200">
                      By ticking below, I declare that I have disclosed all known allergies and sensitivities.
                      I understand that undisclosed allergies may pose a health risk. I consent to this information
                      being shared with my stylist and stored in my Beauty Passport.
                    </p>
                    <div className="flex items-start gap-3">
                      <input type="checkbox" id="sign" {...register('allergy_declaration_signed')} className="accent-[#C9A96E] w-4 h-4 mt-0.5" />
                      <label htmlFor="sign" className="text-sm text-orange-100 font-medium">
                        I confirm and sign this allergy declaration
                      </label>
                    </div>
                    {errors.allergy_declaration_signed && (
                      <p className="text-xs text-red-400">{errors.allergy_declaration_signed.message}</p>
                    )}
                  </div>
                </>
              )}
            </motion.div>
          </AnimatePresence>

          {/* Nav buttons */}
          <div className="flex gap-3 mt-6">
            {step > 0 && (
              <button
                type="button"
                onClick={() => setStep(s => s - 1)}
                className="flex-1 py-3 border border-white/10 rounded-xl text-sm text-gray-300 hover:border-white/30 transition-colors"
              >
                Back
              </button>
            )}
            {step < STEPS.length - 1 ? (
              <button
                type="button"
                onClick={() => setStep(s => s + 1)}
                className="flex-1 py-3 bg-[#C9A96E] text-black rounded-xl text-sm font-semibold hover:bg-[#b8935a] transition-colors"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={mutation.isPending}
                className="flex-1 py-3 bg-[#C9A96E] text-black rounded-xl text-sm font-semibold hover:bg-[#b8935a] transition-colors disabled:opacity-50"
              >
                {mutation.isPending ? 'Submitting…' : 'Submit Consultation'}
              </button>
            )}
          </div>

          {mutation.isError && (
            <p className="text-center text-sm text-red-400 mt-2">
              {(mutation.error as any)?.response?.data?.detail ?? 'Submission failed. Please try again.'}
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
