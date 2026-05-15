import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { mirrorApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useMirrorHistory(customerId: string) {
  return useQuery({
    queryKey: ['mirror', 'history', customerId],
    queryFn: () => mirrorApi.history(customerId).then(unwrap),
    enabled: !!customerId,
    staleTime: 60_000,
  });
}

export function useMirrorStyles(category?: string) {
  return useQuery({
    queryKey: ['mirror', 'styles', category],
    queryFn: () => mirrorApi.styles({ category }).then(unwrap),
    staleTime: 10 * 60_000,
  });
}

export function useTryOn() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: mirrorApi.tryOn,
    onSuccess: (_, vars) => qc.invalidateQueries({ queryKey: ['mirror', 'history', vars.customer_id] }),
  });
}
