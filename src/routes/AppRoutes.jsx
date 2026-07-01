import { Navigate, Route, Routes } from "react-router-dom";

import AdminRoute from "../components/AdminRoute.jsx";
import AppShell from "../components/AppShell.jsx";
import ProtectedRoute from "../components/ProtectedRoute.jsx";
import AdminAddMoviePage from "../pages/AdminAddMoviePage.jsx";
import AdminAnalyticsPage from "../pages/AdminAnalyticsPage.jsx";
import AdminDashboardPage from "../pages/AdminDashboardPage.jsx";
import AdminManageMoviesPage from "../pages/AdminManageMoviesPage.jsx";
import AllMoviesPage from "../pages/AllMoviesPage.jsx";
import DashboardPage from "../pages/DashboardPage.jsx";
import LandingPage from "../pages/LandingPage.jsx";
import LoginPage from "../pages/LoginPage.jsx";
import MovieDetailsPage from "../pages/MovieDetailsPage.jsx";
import RecommendationsPage from "../pages/RecommendationsPage.jsx";
import RegisterPage from "../pages/RegisterPage.jsx";
import UserPreferencesPage from "../pages/UserPreferencesPage.jsx";
import WatchHistoryPage from "../pages/WatchHistoryPage.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/movies" element={<AllMoviesPage />} />
          <Route path="/movies/:movieId" element={<MovieDetailsPage />} />
          <Route path="/watch-history" element={<WatchHistoryPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/preferences" element={<UserPreferencesPage />} />

          <Route element={<AdminRoute />}>
            <Route path="/admin" element={<AdminDashboardPage />} />
            <Route path="/admin/movies/new" element={<AdminAddMoviePage />} />
            <Route path="/admin/movies" element={<AdminManageMoviesPage />} />
            <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
