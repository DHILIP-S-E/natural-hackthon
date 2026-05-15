import { useQuery } from '@tanstack/react-query';
import { staffApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useStaff(locationId?: string) {
  return useQuery({
    queryKey: ['staff', locationId ?? 'all'],
    queryFn: () => staffApi.list({ location_id: locationId }).then(unwrap),
    staleTime: 30_000,
  });
}

export function useStaffMember(id: string) {
  return useQuery({
    queryKey: ['staff', id],
    queryFn: () => staffApi.getById(id).then(unwrap),
    enabled: !!id,
  });
}

export function useMyStaffProfile() {
  return useQuery({
    queryKey: ['staff', 'me'],
    queryFn: () => staffApi.me().then(unwrap),
    staleTime: 60_000,
  });
}

export function useAttritionRisk() {
  return useQuery({
    queryKey: ['staff', 'attrition-risk'],
    queryFn: () => staffApi.attritionRisk().then(unwrap),
    staleTime: 5 * 60_000,
  });
}
