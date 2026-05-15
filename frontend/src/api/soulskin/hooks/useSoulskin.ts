import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { soulskinApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useSoulskinSession(id: string) {
  return useQuery({
    queryKey: ['soulskin', id],
    queryFn: () => soulskinApi.getById(id).then(unwrap),
    enabled: !!id,
  });
}

export function useSoulskinHistory() {
  return useQuery({
    queryKey: ['soulskin', 'me', 'history'],
    queryFn: () => soulskinApi.myHistory().then(unwrap),
    staleTime: 60_000,
  });
}

export function useStartSoulskin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: soulskinApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['soulskin'] }),
  });
}

export function useAnswerSoulskin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, answers }: {
      id: string;
      answers: { question_1_song?: string; question_2_colour?: string; question_3_word?: string };
    }) => soulskinApi.answer(id, answers).then(unwrap),
    onSuccess: (_, { id }) => qc.invalidateQueries({ queryKey: ['soulskin', id] }),
  });
}

export function useCompleteSoulskin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => soulskinApi.complete(id).then(unwrap),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['soulskin'] }),
  });
}
