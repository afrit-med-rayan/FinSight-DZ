import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import useAuthStore from '../store/authStore';
import client from '../api/client';
import {
  Home,
  List,
  LogOut,
  TrendingUp,
  PiggyBank,
  Bell,
  Brain,
} from 'lucide-react';

const Layout = () => {
  const { user, logout, selectedAccountId, setSelectedAccount } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);

  // ── On mount: load user's first account and store its ID ──────────────────
  useEffect(() => {
    if (!selectedAccountId) {
      client.get('/accounts/me').then((res) => {
        if (res.data?.length > 0) {
          setSelectedAccount(res.data[0].id);
        }
      }).catch(() => {});
    }
  }, []);

  // ── Poll unread insight count every 60 s ──────────────────────────────────
  useEffect(() => {
    if (!selectedAccountId) return;
    const load = () =>
      client
        .get(`/insights/unread-count?account_id=${selectedAccountId}`)
        .then((r) => setUnreadCount(r.data.count))
        .catch(() => {});
    load();
    const interval = setInterval(load, 60_000);
    return () => clearInterval(interval);
  }, [selectedAccountId]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard',     path: '/',             icon: Home },
    { name: 'Transactions',  path: '/transactions', icon: List },
    { name: 'Insights',      path: '/insights',     icon: TrendingUp, badge: unreadCount },
    { name: 'Budgets',       path: '/budgets',      icon: PiggyBank },
    { name: 'Prévisions IA', path: '/predictions',  icon: Brain },
  ];

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* ── Sidebar ─────────────────────────────────────────────────────── */}
      <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-100 dark:border-gray-700">
          <h1 className="text-2xl font-bold text-blue-900 dark:text-white tracking-tight">
            FinSight <span className="text-blue-500">DZ</span>
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">Tableau de bord financier</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.path === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center justify-between px-4 py-2.5 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <span className="flex items-center gap-3">
                  <Icon className="w-5 h-5" />
                  <span className="font-medium text-sm">{item.name}</span>
                </span>
                {item.badge > 0 && (
                  <span
                    className={`text-xs font-bold px-1.5 py-0.5 rounded-full ${
                      isActive
                        ? 'bg-white/30 text-white'
                        : 'bg-blue-600 text-white'
                    }`}
                  >
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* User + Logout */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
          {/* Avatar + name */}
          <div className="flex items-center gap-3 px-2">
            <div className="h-9 w-9 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shrink-0">
              {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-800 dark:text-white truncate">
                {user?.full_name || 'Utilisateur'}
              </p>
              <p className="text-xs text-gray-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-2.5 w-full rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-sm font-medium"
          >
            <LogOut className="w-4 h-4" />
            Déconnexion
          </button>
        </div>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* TopBar */}
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-gray-500 dark:text-gray-400 text-sm">
              Bienvenue,{' '}
              <strong className="text-gray-900 dark:text-white">
                {user?.full_name || 'Utilisateur'}
              </strong>
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Insights bell with badge */}
            <Link
              to="/insights"
              className="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              title="Insights"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 text-[10px] font-bold bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </Link>

            {/* Avatar */}
            <div className="h-9 w-9 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow">
              {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
