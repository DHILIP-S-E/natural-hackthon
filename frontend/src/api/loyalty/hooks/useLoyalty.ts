import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { loyaltyApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useLoyaltyProfile() {
  return useQuery({
    queryKey: ['loyalty', 'me'],
    queryFn: () => loyaltyApi.me().then(unwrap),
    staleTime: 60_000,
  });
}

export function useLoyaltyTransactions(limit = 20) {
  return useQuery({
    queryKey: ['loyalty', 'transactions', limit],
    queryFn: () => loyaltyApi.transactions({ limit }).then(unwrap),
    staleTime: 30_000,
  });
}

export function useRedeemPoints() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (points: number) => loyaltyApi.redeem(points).then(unwrap),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['loyalty'] }),
  });
}
