import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { queueApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useQueue(locationId: string) {
  return useQuery({
    queryKey: ['queue', locationId],
    queryFn: () => queueApi.list(locationId).then(unwrap),
    enabled: !!locationId,
    refetchInterval: 15_000,
  });
}

export function useWaitEstimate(locationId: string) {
  return useQuery({
    queryKey: ['queue', locationId, 'estimate'],
    queryFn: () => queueApi.estimate(locationId).then(unwrap),
    enabled: !!locationId,
    refetchInterval: 30_000,
  });
}

export function useAddToQueue() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: queueApi.add,
    onSuccess: (_, vars) => qc.invalidateQueries({ queryKey: ['queue', vars.location_id] }),
  });
}

export function useUpdateQueueStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      queueApi.updateStatus(id, status).then(unwrap),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['queue'] }),
  });
}
