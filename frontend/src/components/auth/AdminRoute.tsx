import ProtectedRoute from './ProtectedRoute';

interface Props {
  children: React.ReactNode;
}

export default function AdminRoute({ children }: Props) {
  return (
    <ProtectedRoute allowedRoles={['super_admin']}>
      {children}
    </ProtectedRoute>
  );
}
