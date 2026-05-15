import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { customersApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useMyProfile() {
  return useQuery({
    queryKey: ['customers', 'me'],
    queryFn: () => customersApi.me().then(unwrap),
    staleTime: 60_000,
  });
}

export function useCustomer(id: string) {
  return useQuery({
    queryKey: ['customers', id],
    queryFn: () => customersApi.getById(id).then(unwrap),
    enabled: !!id,
  });
}

export function useBeautyPassport(customerId: string) {
  return useQuery({
    queryKey: ['passport', customerId],
    queryFn: () => customersApi.passport(customerId).then(unwrap),
    enabled: !!customerId,
    staleTime: 60_000,
  });
}

export function useNextBestActions(customerId: string) {
  return useQuery({
    queryKey: ['next-best', customerId],
    queryFn: () => customersApi.nextBestActions(customerId).then(unwrap),
    enabled: !!customerId,
    staleTime: 120_000,
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: customersApi.updateProfile,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['customers', 'me'] }),
  });
}
