import { useMutation, useQuery } from '@tanstack/react-query';
import { agentsApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useQualityScore(bookingId: string) {
  return useQuery({
    queryKey: ['agents', 'quality-score', bookingId],
    queryFn: () => agentsApi.qualityScore(bookingId).then(unwrap),
    enabled: !!bookingId,
  });
}

export function useAttritionRisk() {
  return useQuery({
    queryKey: ['agents', 'attrition-risk'],
    queryFn: () => agentsApi.attritionRisk().then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useTrendRadar(locationId?: string) {
  return useQuery({
    queryKey: ['agents', 'trend-radar', locationId],
    queryFn: () => agentsApi.trendRadar(locationId).then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useForecasting(locationId?: string, days = 30) {
  return useQuery({
    queryKey: ['agents', 'forecast', locationId, days],
    queryFn: () => agentsApi.forecast({ location_id: locationId, days }).then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useChatbot() {
  return useMutation({
    mutationFn: agentsApi.chatbot,
  });
}
