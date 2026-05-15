import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useAnalyticsOverview(locationId?: string, period?: string) {
  return useQuery({
    queryKey: ['analytics', 'overview', locationId, period],
    queryFn: () => analyticsApi.overview({ location_id: locationId, period }).then(unwrap),
    staleTime: 60_000,
  });
}

export function useRevenueAnalytics(locationId?: string, period?: string) {
  return useQuery({
    queryKey: ['analytics', 'revenue', locationId, period],
    queryFn: () => analyticsApi.revenue({ location_id: locationId, period }).then(unwrap),
    staleTime: 60_000,
  });
}

export function useSoulskinAnalytics(locationId?: string) {
  return useQuery({
    queryKey: ['analytics', 'soulskin', locationId],
    queryFn: () => analyticsApi.soulskin({ location_id: locationId }).then(unwrap),
    staleTime: 60_000,
  });
}

export function useBIDashboard(locationId?: string) {
  return useQuery({
    queryKey: ['analytics', 'bi', locationId],
    queryFn: () => analyticsApi.biDashboard({ location_id: locationId }).then(unwrap),
    staleTime: 60_000,
  });
}

export function useFranchiseAnalytics(period?: string) {
  return useQuery({
    queryKey: ['analytics', 'franchise', period],
    queryFn: () => analyticsApi.franchise({ period }).then(unwrap),
    staleTime: 60_000,
  });
}
