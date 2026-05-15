import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { trainingApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useMyTrainingRecords() {
  return useQuery({
    queryKey: ['training', 'me'],
    queryFn: () => trainingApi.myRecords().then(unwrap),
    staleTime: 5 * 60_000,
  });
}

export function useTrainingGaps(staffId: string) {
  return useQuery({
    queryKey: ['training', 'gaps', staffId],
    queryFn: () => trainingApi.gaps(staffId).then(unwrap),
    enabled: !!staffId,
    staleTime: 5 * 60_000,
  });
}

export function useCreateTraining() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: trainingApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['training'] }),
  });
}

export function useCompleteTraining() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { score?: number; passed: boolean } }) =>
      trainingApi.complete(id, data).then(unwrap),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['training'] }),
  });
}
