import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { qualityApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useQualityAssessments(params?: { location_id?: string; stylist_id?: string }) {
  return useQuery({
    queryKey: ['quality', params],
    queryFn: () => qualityApi.list(params).then(unwrap),
    staleTime: 30_000,
  });
}

export function useQualityAssessment(id: string) {
  return useQuery({
    queryKey: ['quality', id],
    queryFn: () => qualityApi.getById(id).then(unwrap),
    enabled: !!id,
  });
}

export function useCreateQualityAssessment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: qualityApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['quality'] }),
  });
}

export function useReviewQualityAssessment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { manager_rating: number; notes?: string } }) =>
      qualityApi.review(id, data).then(unwrap),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['quality'] }),
  });
}
