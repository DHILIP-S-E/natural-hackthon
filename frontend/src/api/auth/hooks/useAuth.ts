import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../index';
import { unwrap } from '../../base/unwrap';
import { useAuthStore, getRoleRedirect } from '../../../stores/authStore';

export function useMe() {
  const { isAuthenticated } = useAuthStore();
  return useQuery({
    queryKey: ['me'],
    queryFn: () => authApi.me().then(unwrap),
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5,
  });
}

export function useLogin() {
  const { login } = useAuthStore();
  const navigate = useNavigate();
  const qc = useQueryClient();

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password).then(unwrap),
    onSuccess: ({ access_token, user }) => {
      login(access_token, user);
      qc.setQueryData(['me'], user);
      navigate(getRoleRedirect(user.role), { replace: true });
    },
  });
}

export function useLogout() {
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  const qc = useQueryClient();

  return () => {
    logout();
    qc.clear();
    navigate('/login', { replace: true });
  };
}
