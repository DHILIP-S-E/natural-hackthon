import { useQuery } from '@tanstack/react-query';
import { trendsApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useTrends(params?: { category?: string; trajectory?: string }) {
  return useQuery({
    queryKey: ['trends', params],
    queryFn: () => trendsApi.list(params).then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useTrendRadar(locationId?: string) {
  return useQuery({
    queryKey: ['trends', 'radar', locationId],
    queryFn: () => trendsApi.radar({ location_id: locationId }).then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useTrendForecast(serviceCategory?: string) {
  return useQuery({
    queryKey: ['trends', 'forecast', serviceCategory],
    queryFn: () => trendsApi.forecast({ service_category: serviceCategory }).then(unwrap),
    staleTime: 5 * 60_000,
  });
}
