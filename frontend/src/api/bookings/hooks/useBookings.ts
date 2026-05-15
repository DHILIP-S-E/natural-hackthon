import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { bookingsApi } from '../index';
import { unwrap } from '../../base/unwrap';

export function useMyBookings() {
  return useQuery({
    queryKey: ['bookings', 'me'],
    queryFn: () => bookingsApi.myBookings().then(unwrap),
    staleTime: 30_000,
  });
}

export function useBooking(id: string) {
  return useQuery({
    queryKey: ['bookings', id],
    queryFn: () => bookingsApi.getById(id).then(unwrap),
    enabled: !!id,
  });
}

export function useAvailableSlots(params: {
  location_id: string; service_id: string; date: string; stylist_id?: string;
}, enabled = true) {
  return useQuery({
    queryKey: ['slots', params],
    queryFn: () => bookingsApi.getAvailableSlots(params).then(unwrap),
    enabled: enabled && !!params.location_id && !!params.service_id && !!params.date,
  });
}

export function useCreateBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: bookingsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bookings'] }),
  });
}

export function useCancelBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bookingsApi.cancel(id).then(unwrap),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bookings'] }),
  });
}
