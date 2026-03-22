import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardLayout } from './components/layout/Sidebar';
import ProtectedRoute from './components/layout/ProtectedRoute';
import InstallPrompt from './components/ui/InstallPrompt';

// Public pages
import LandingPage from './pages/public/LandingPage';
import LoginPage from './pages/public/LoginPage';
import RegisterPage from './pages/public/RegisterPage';

// Dashboards
import ManagerDashboard from './pages/manager/ManagerDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';
import CustomerDashboard from './pages/customer/CustomerDashboard';
import StylistDashboard from './pages/stylist/StylistDashboard';
import FranchiseDashboard from './pages/franchise/FranchiseDashboard';
import RegionalDashboard from './pages/regional/RegionalDashboard';

// Manager pages
import QueueManagement from './pages/manager/QueueManagement';
import TrendIntelligence from './pages/manager/TrendIntelligence';
import TeamManagement from './pages/manager/TeamManagement';
import QualityDashboard from './pages/manager/QualityDashboard';
import FeedbackPage from './pages/manager/FeedbackPage';
import SOPManagement from './pages/manager/SOPManagement';
import SoulskinAnalytics from './pages/manager/SoulskinAnalytics';

// Customer pages
import CustomerBookings from './pages/customer/CustomerBookings';
import BookNew from './pages/customer/BookNew';
import BeautyPassport from './pages/customer/BeautyPassport';
import BeautyJourney from './pages/customer/BeautyJourney';
import HomecarePage from './pages/customer/HomecarePage';

// Stylist pages
import StylistPerformance from './pages/stylist/StylistPerformance';
import LiveSession from './pages/stylist/LiveSession';
import StylistCustomers from './pages/stylist/StylistCustomers';
import StylistTraining from './pages/stylist/StylistTraining';

// Shared / Feature pages
import SoulskinFlow from './pages/soulskin/SoulskinFlow';
import ARMirrorPage from './pages/mirror/ARMirrorPage';
import BIDashboard from './pages/analytics/BIDashboard';
import PlaceholderDashboard from './pages/shared/PlaceholderDashboard';

// Location pages
import LocationsPage from './pages/locations/LocationsPage';
import LocationDetailPage from './pages/locations/LocationDetailPage';
import CompareLocationsPage from './pages/locations/CompareLocationsPage';

// Admin pages (additional)
import UsersPage from './pages/admin/UsersPage';
import AIEnginePage from './pages/admin/AIEnginePage';
import SystemConfigPage from './pages/admin/SystemConfigPage';
import RBACPage from './pages/admin/RBACPage';

// Manager pages (additional)
import AlertsHubPage from './pages/manager/AlertsHubPage';
import LocationSettingsPage from './pages/manager/LocationSettingsPage';

// Customer pages (additional)
import CustomerProfilePage from './pages/customer/CustomerProfilePage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
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
        <InstallPrompt />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
