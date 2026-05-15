import { useQuery } from '@tanstack/react-query';
import { servicesApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useServices(category?: string) {
  return useQuery({
    queryKey: ['services', category ?? 'all'],
    queryFn: () => servicesApi.list({ category, is_active: true }).then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useService(id: string) {
  return useQuery({
    queryKey: ['services', id],
    queryFn: () => servicesApi.getById(id).then(unwrap),
    enabled: !!id,
  });
}

export function useServiceCategories() {
  return useQuery({
    queryKey: ['services', 'categories'],
    queryFn: () => servicesApi.categories().then(unwrap),
    staleTime: 10 * 60_000,
  });
}
