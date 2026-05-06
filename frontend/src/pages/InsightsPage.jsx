import { useEffect, useState } from 'react';
import useAuthStore from '../store/authStore';
import client from '../api/client';
import { AlertTriangle, CheckCircle2, Info, TrendingUp, Sparkles, RefreshCw, Eye } from 'lucide-react';

// ─── Severity styling ────────────────────────────────────────────────────────
const SEVERITY = {
  CRITICAL: {
    bg: 'bg-red-50 border-red-200',
    border: 'border-l-4 border-l-red-500',
    text: 'text-red-800',
    badge: 'bg-red-100 text-red-700',
    icon: AlertTriangle,
    iconColor: 'text-red-500',
    label: 'Critique',
  },
  WARN: {
    bg: 'bg-amber-50 border-amber-200',
    border: 'border-l-4 border-l-amber-500',
    text: 'text-amber-800',
    badge: 'bg-amber-100 text-amber-700',
    icon: AlertTriangle,
    iconColor: 'text-amber-500',
    label: 'Attention',
  },
  INFO: {
    bg: 'bg-blue-50 border-blue-200',
    border: 'border-l-4 border-l-blue-500',
    text: 'text-blue-800',
    badge: 'bg-blue-100 text-blue-700',
    icon: Info,
    iconColor: 'text-blue-500',
    label: 'Info',
  },
  GOOD: {
    bg: 'bg-green-50 border-green-200',
    border: 'border-l-4 border-l-green-500',
    text: 'text-green-800',
    badge: 'bg-green-100 text-green-700',
    icon: CheckCircle2,
    iconColor: 'text-green-500',
    label: 'Bonne nouvelle',
  },
  CONTEXT: {
    bg: 'bg-teal-50 border-teal-200',
    border: 'border-l-4 border-l-teal-500',
    text: 'text-teal-800',
    badge: 'bg-teal-100 text-teal-700',
    icon: Sparkles,
    iconColor: 'text-teal-500',
    label: 'Contexte',
  },
};

// Format date nicely in French
const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export default function InsightsPage() {
  const { selectedAccountId } = useAuthStore();
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [filter, setFilter] = useState('ALL');

  const fetchInsights = async () => {
    if (!selectedAccountId) return;
    setLoading(true);
    try {
      const res = await client.get(`/insights?account_id=${selectedAccountId}`);
      setInsights(res.data);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [selectedAccountId]);

  const handleGenerate = async () => {
    if (!selectedAccountId) return;
    setGenerating(true);
    try {
      await client.post(`/insights/generate?account_id=${selectedAccountId}`);
      await fetchInsights();
    } finally {
      setGenerating(false);
    }
  };

  const handleMarkRead = async (id) => {
    await client.patch(`/insights/${id}/read`);
    setInsights((prev) =>
      prev.map((ins) => (ins.id === id ? { ...ins, is_read: true } : ins))
    );
  };

  const handleMarkAllRead = async () => {
    await client.patch(`/insights/mark-all-read?account_id=${selectedAccountId}`);
    setInsights((prev) => prev.map((ins) => ({ ...ins, is_read: true })));
  };

  const severities = ['ALL', 'CRITICAL', 'WARN', 'INFO', 'GOOD', 'CONTEXT'];
  const filtered =
    filter === 'ALL' ? insights : insights.filter((i) => i.severity === filter);

  const unreadCount = insights.filter((i) => !i.is_read).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="w-7 h-7 text-blue-600" />
            Insights Financiers
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1 text-sm">
            Analyse intelligente de vos habitudes de dépense
          </p>
        </div>
        <div className="flex gap-3">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700 transition"
            >
              <Eye className="w-4 h-4" />
              Tout marquer lu
            </button>
          )}
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-60 transition"
          >
            <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
            {generating ? 'Génération…' : 'Regénérer'}
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {severities.slice(1).map((sev) => {
          const s = SEVERITY[sev];
          const count = insights.filter((i) => i.severity === sev).length;
          return (
            <div key={sev} className={`rounded-xl p-3 border ${s.bg} ${s.border} text-center`}>
              <p className={`text-2xl font-bold ${s.text}`}>{count}</p>
              <p className={`text-xs font-medium mt-0.5 ${s.text}`}>{s.label}</p>
            </div>
          );
        })}
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {severities.map((sev) => (
          <button
            key={sev}
            onClick={() => setFilter(sev)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
              filter === sev
                ? 'bg-blue-600 text-white shadow'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            {sev === 'ALL' ? `Tous (${insights.length})` : (SEVERITY[sev]?.label ?? sev)}
          </button>
        ))}
      </div>

      {/* Insights List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-lg font-medium">Aucun insight disponible</p>
          <p className="text-sm mt-1">Cliquez sur « Regénérer » pour analyser vos transactions.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((ins) => {
            const s = SEVERITY[ins.severity] ?? SEVERITY.INFO;
            const Icon = s.icon;
            return (
              <div
                key={ins.id}
                className={`rounded-xl border p-4 transition-all ${s.bg} ${s.border} ${
                  ins.is_read ? 'opacity-60' : 'shadow-sm'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className="mt-0.5 shrink-0">
                    <Icon className={`w-5 h-5 ${s.iconColor}`} />
                  </div>

                  {/* Body */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${s.badge}`}>
                        {s.label}
                      </span>
                      {ins.rule_id && (
                        <span className="text-xs text-gray-400 font-mono">{ins.rule_id}</span>
                      )}
                      {!ins.is_read && (
                        <span className="text-xs text-blue-600 font-semibold">● Nouveau</span>
                      )}
                    </div>
                    <p className={`text-sm font-medium leading-snug ${s.text}`}>
                      {ins.message_fr}
                    </p>
                    <p className="text-xs text-gray-400 mt-1.5">
                      {formatDate(ins.generated_at)}
                    </p>
                  </div>

                  {/* Mark read */}
                  {!ins.is_read && (
                    <button
                      onClick={() => handleMarkRead(ins.id)}
                      title="Marquer comme lu"
                      className="shrink-0 mt-0.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
