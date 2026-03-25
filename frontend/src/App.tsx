import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardLayout } from './components/layout/Sidebar';
import ProtectedRoute from './components/layout/ProtectedRoute';
import InstallPrompt from './components/ui/InstallPrompt';
import { lazy, Suspense } from 'react';

// Public pages (keep eagerly loaded — they're the entry points)
import LandingPage from './pages/public/LandingPage';
import LoginPage from './pages/public/LoginPage';
import RegisterPage from './pages/public/RegisterPage';

// Lazy-loaded pages
const ManagerDashboard = lazy(() => import('./pages/manager/ManagerDashboard'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const CustomerDashboard = lazy(() => import('./pages/customer/CustomerDashboard'));
const StylistDashboard = lazy(() => import('./pages/stylist/StylistDashboard'));
const FranchiseDashboard = lazy(() => import('./pages/franchise/FranchiseDashboard'));
const RegionalDashboard = lazy(() => import('./pages/regional/RegionalDashboard'));

const QueueManagement = lazy(() => import('./pages/manager/QueueManagement'));
const TrendIntelligence = lazy(() => import('./pages/manager/TrendIntelligence'));
const TeamManagement = lazy(() => import('./pages/manager/TeamManagement'));
const QualityDashboard = lazy(() => import('./pages/manager/QualityDashboard'));
const FeedbackPage = lazy(() => import('./pages/manager/FeedbackPage'));
const SOPManagement = lazy(() => import('./pages/manager/SOPManagement'));
const SoulskinAnalytics = lazy(() => import('./pages/manager/SoulskinAnalytics'));

const CustomerBookings = lazy(() => import('./pages/customer/CustomerBookings'));
const BookNew = lazy(() => import('./pages/customer/BookNew'));
const BeautyPassport = lazy(() => import('./pages/customer/BeautyPassport'));
const BeautyJourney = lazy(() => import('./pages/customer/BeautyJourney'));
const HomecarePage = lazy(() => import('./pages/customer/HomecarePage'));

const StylistPerformance = lazy(() => import('./pages/stylist/StylistPerformance'));
const LiveSession = lazy(() => import('./pages/stylist/LiveSession'));
const StylistCustomers = lazy(() => import('./pages/stylist/StylistCustomers'));
const StylistTraining = lazy(() => import('./pages/stylist/StylistTraining'));

const SoulskinFlow = lazy(() => import('./pages/soulskin/SoulskinFlow'));
const ARMirrorPage = lazy(() => import('./pages/mirror/ARMirrorPage'));
const BIDashboard = lazy(() => import('./pages/analytics/BIDashboard'));
const PlaceholderDashboard = lazy(() => import('./pages/shared/PlaceholderDashboard'));

const LocationsPage = lazy(() => import('./pages/locations/LocationsPage'));
const LocationDetailPage = lazy(() => import('./pages/locations/LocationDetailPage'));
const CompareLocationsPage = lazy(() => import('./pages/locations/CompareLocationsPage'));

const UsersPage = lazy(() => import('./pages/admin/UsersPage'));
const AIEnginePage = lazy(() => import('./pages/admin/AIEnginePage'));
const SystemConfigPage = lazy(() => import('./pages/admin/SystemConfigPage'));
const RBACPage = lazy(() => import('./pages/admin/RBACPage'));

const AlertsHubPage = lazy(() => import('./pages/manager/AlertsHubPage'));
const LocationSettingsPage = lazy(() => import('./pages/manager/LocationSettingsPage'));

const CustomerProfilePage = lazy(() => import('./pages/customer/CustomerProfilePage'));

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
});

function PageLoader() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '50vh', color: 'var(--text-muted)' }}>
      Loading...
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Customer routes */}
            <Route element={<ProtectedRoute allowedRoles={['customer']}><DashboardLayout /></ProtectedRoute>}>
              <Route path="/app/dashboard" element={<CustomerDashboard />} />
              <Route path="/app/passport" element={<BeautyPassport />} />
              <Route path="/app/mirror" element={<ARMirrorPage />} />
              <Route path="/app/soulskin" element={<SoulskinFlow />} />
              <Route path="/app/book" element={<BookNew />} />
              <Route path="/app/bookings" element={<CustomerBookings />} />
              <Route path="/app/bookings/:id" element={<CustomerBookings />} />
              <Route path="/app/journey" element={<BeautyJourney />} />
              <Route path="/app/homecare" element={<HomecarePage />} />
              <Route path="/app/profile" element={<CustomerProfilePage />} />
            </Route>

            {/* Stylist routes */}
            <Route element={<ProtectedRoute allowedRoles={['stylist']}><DashboardLayout /></ProtectedRoute>}>
              <Route path="/stylist/dashboard" element={<StylistDashboard />} />
              <Route path="/stylist/session/:id" element={<LiveSession />} />
              <Route path="/stylist/soulskin/:id" element={<SoulskinFlow />} />
              <Route path="/stylist/customers" element={<StylistCustomers />} />
              <Route path="/stylist/customers/:id" element={<StylistCustomers />} />
              <Route path="/stylist/performance" element={<StylistPerformance />} />
              <Route path="/stylist/training" element={<StylistTraining />} />
            </Route>

            {/* Salon Manager routes */}
            <Route element={<ProtectedRoute allowedRoles={['salon_manager']}><DashboardLayout /></ProtectedRoute>}>
              <Route path="/manager/dashboard" element={<ManagerDashboard />} />
              <Route path="/manager/today" element={<ManagerDashboard />} />
              <Route path="/manager/team" element={<TeamManagement />} />
              <Route path="/manager/team/:id" element={<TeamManagement />} />
              <Route path="/manager/bookings" element={<CustomerBookings />} />
              <Route path="/manager/bookings/:id" element={<CustomerBookings />} />
              <Route path="/manager/queue" element={<QueueManagement />} />
              <Route path="/manager/quality" element={<QualityDashboard />} />
              <Route path="/manager/quality/sessions/:id" element={<QualityDashboard />} />
              <Route path="/manager/soulskin" element={<SoulskinAnalytics />} />
              <Route path="/manager/sops" element={<SOPManagement />} />
              <Route path="/manager/sops/:id" element={<SOPManagement />} />
              <Route path="/manager/trends" element={<TrendIntelligence />} />
              <Route path="/manager/reports" element={<BIDashboard />} />
              <Route path="/manager/feedback" element={<FeedbackPage />} />
              <Route path="/manager/alerts" element={<AlertsHubPage />} />
              <Route path="/manager/settings" element={<LocationSettingsPage />} />
            </Route>

            {/* Franchise Owner routes */}
            <Route element={<ProtectedRoute allowedRoles={['franchise_owner']}><DashboardLayout /></ProtectedRoute>}>
              <Route path="/franchise/dashboard" element={<FranchiseDashboard />} />
              <Route path="/franchise/locations" element={<LocationsPage scope="franchise" />} />
              <Route path="/franchise/locations/:id" element={<LocationDetailPage />} />
              <Route path="/franchise/revenue" element={<BIDashboard />} />
              <Route path="/franchise/quality" element={<QualityDashboard />} />
              <Route path="/franchise/staff" element={<TeamManagement />} />
              <Route path="/franchise/compare" element={<CompareLocationsPage />} />
              <Route path="/franchise/reports" element={<BIDashboard />} />
            </Route>

            {/* Regional Manager routes */}
            <Route element={<ProtectedRoute allowedRoles={['regional_manager']}><DashboardLayout /></ProtectedRoute>}>
              <Route path="/regional/dashboard" element={<RegionalDashboard />} />
              <Route path="/regional/map" element={<LocationsPage scope="regional" />} />
              <Route path="/regional/locations" element={<LocationsPage scope="regional" />} />
              <Route path="/regional/locations/:id" element={<LocationDetailPage />} />
              <Route path="/regional/revenue" element={<BIDashboard />} />
              <Route path="/regional/quality" element={<QualityDashboard />} />
              <Route path="/regional/staff" element={<TeamManagement />} />
              <Route path="/regional/trends" element={<TrendIntelligence />} />
              <Route path="/regional/compare" element={<CompareLocationsPage />} />
              <Route path="/regional/reports" element={<BIDashboard />} />
            </Route>

            {/* Super Admin routes */}
            <Route element={<ProtectedRoute allowedRoles={['super_admin']}><DashboardLayout /></ProtectedRoute>}>
              <Route path="/admin/dashboard" element={<AdminDashboard />} />
              <Route path="/admin/map" element={<LocationsPage scope="admin" />} />
              <Route path="/admin/locations" element={<LocationsPage scope="admin" />} />
              <Route path="/admin/locations/:id" element={<LocationDetailPage />} />
              <Route path="/admin/users" element={<UsersPage />} />
              <Route path="/admin/users/:id" element={<UsersPage />} />
              <Route path="/admin/revenue" element={<BIDashboard />} />
              <Route path="/admin/quality" element={<QualityDashboard />} />
              <Route path="/admin/trends" element={<TrendIntelligence />} />
              <Route path="/admin/ai" element={<AIEnginePage />} />
              <Route path="/admin/soulskin" element={<SoulskinAnalytics />} />
              <Route path="/admin/bi" element={<BIDashboard />} />
              <Route path="/admin/training" element={<PlaceholderDashboard title="Admin: Training" subtitle="Network-wide Training intelligence across all locations." />} />
              <Route path="/admin/config" element={<SystemConfigPage />} />
              <Route path="/admin/rbac" element={<RBACPage />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
        <InstallPrompt />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
