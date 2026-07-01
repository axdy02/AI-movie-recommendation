import {
  BarChart3,
  Clock3,
  Film,
  Gauge,
  HeartHandshake,
  Home,
  LibraryBig,
  LogOut,
  PlusCircle,
  Shield,
  Sparkles,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";
import { cx } from "../utils/formatters.js";

const userLinks = [
  { to: "/dashboard", label: "Dashboard", icon: Gauge },
  { to: "/movies", label: "Movies", icon: Film },
  { to: "/recommendations", label: "Recommendations", icon: Sparkles },
  { to: "/watch-history", label: "Watch History", icon: Clock3 },
  { to: "/preferences", label: "Preferences", icon: HeartHandshake },
];

const adminLinks = [
  { to: "/admin", label: "Admin Home", icon: Shield },
  { to: "/admin/movies/new", label: "Add Movie", icon: PlusCircle },
  { to: "/admin/movies", label: "Manage Movies", icon: LibraryBig },
  { to: "/admin/analytics", label: "Analytics", icon: BarChart3 },
];

export default function AppShell() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="app-shell-grid min-h-screen bg-ink text-white">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r border-white/10 bg-panel/95 px-5 py-6 backdrop-blur-xl lg:block">
        <NavLink to="/dashboard" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-signal to-violetSignal">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-signal">
              RecSys
            </p>
            <p className="text-lg font-semibold">Movie AI</p>
          </div>
        </NavLink>

        <nav className="mt-9 space-y-2">
          <ShellLink to="/" label="Landing" icon={Home} />
          {userLinks.map((link) => (
            <ShellLink key={link.to} {...link} />
          ))}
        </nav>

        {isAdmin ? (
          <div className="mt-8">
            <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Admin
            </p>
            <nav className="space-y-2">
              {adminLinks.map((link) => (
                <ShellLink key={link.to} {...link} />
              ))}
            </nav>
          </div>
        ) : null}

        <div className="absolute bottom-6 left-5 right-5 rounded-lg border border-white/10 bg-white/[0.04] p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-signal/15 text-signal">
              {user?.full_name?.[0] || user?.email?.[0] || "U"}
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{user?.full_name || "User"}</p>
              <p className="truncate text-xs text-slate-400">{user?.email}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/10 hover:text-white"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-20 border-b border-white/10 bg-ink/80 px-4 py-3 backdrop-blur-xl lg:hidden">
          <div className="flex items-center justify-between gap-3">
            <NavLink to="/dashboard" className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-signal" />
              <span className="font-semibold">Movie AI</span>
            </NavLink>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-white/10 p-2 text-slate-300"
              aria-label="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
          <nav className="mt-3 flex gap-2 overflow-x-auto pb-1">
            {[...userLinks, ...(isAdmin ? adminLinks : [])].map((link) => (
              <MobileLink key={link.to} {...link} />
            ))}
          </nav>
        </header>

        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function ShellLink({ to, label, icon: Icon }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cx(
          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition",
          isActive
            ? "bg-signal/15 text-white"
            : "text-slate-400 hover:bg-white/[0.06] hover:text-white",
        )
      }
    >
      <Icon className="h-4 w-4" />
      {label}
    </NavLink>
  );
}

function MobileLink({ to, label, icon: Icon }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cx(
          "flex shrink-0 items-center gap-2 rounded-lg border px-3 py-2 text-xs",
          isActive
            ? "border-signal/40 bg-signal/15 text-white"
            : "border-white/10 bg-white/[0.03] text-slate-400",
        )
      }
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </NavLink>
  );
}
