import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { moodApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useMoodHistory(customerId: string) {
  return useQuery({
    queryKey: ['mood', 'history', customerId],
    queryFn: () => moodApi.history(customerId).then(unwrap),
    enabled: !!customerId,
    staleTime: 60_000,
  });
}

export function useLatestMood(customerId: string) {
  return useQuery({
    queryKey: ['mood', 'latest', customerId],
    queryFn: () => moodApi.latest(customerId).then(unwrap),
    enabled: !!customerId,
    staleTime: 30_000,
  });
}

export function useDetectMood() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: moodApi.detect,
    onSuccess: (_, vars) => qc.invalidateQueries({ queryKey: ['mood', 'latest', vars.customer_id] }),
  });
}
