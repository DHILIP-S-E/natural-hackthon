import { useQuery } from '@tanstack/react-query';
import { locationsApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useLocations(activeOnly = true) {
  return useQuery({
    queryKey: ['locations', activeOnly],
    queryFn: () => locationsApi.list({ is_active: activeOnly }).then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useLocation(id: string) {
  return useQuery({
    queryKey: ['locations', id],
    queryFn: () => locationsApi.getById(id).then(unwrap),
    enabled: !!id,
  });
}

export function useNearbyLocations(lat: number, lng: number, radiusKm = 10) {
  return useQuery({
    queryKey: ['locations', 'nearby', lat, lng, radiusKm],
    queryFn: () => locationsApi.nearby({ lat, lng, radius_km: radiusKm }).then(unwrap),
    enabled: !!lat && !!lng,
    staleTime: 5 * 60_000,
  });
}

export function useLocationAnalytics(id: string, period?: string) {
  return useQuery({
    queryKey: ['locations', id, 'analytics', period],
    queryFn: () => locationsApi.analytics(id, period).then(unwrap),
    enabled: !!id,
    staleTime: 60_000,
  });
}
