import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";
import LoadingState from "./LoadingState.jsx";

export default function AdminRoute() {
  const { bootstrapping, isAdmin } = useAuth();

  if (bootstrapping) {
    return <LoadingState label="Checking permissions" />;
  }

  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
