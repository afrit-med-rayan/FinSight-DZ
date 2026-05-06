import { useEffect, useState } from 'react';
import useAuthStore from '../store/authStore';
import client from '../api/client';
import {
  PiggyBank,
  Plus,
  Trash2,
  TrendingDown,
  CheckCircle2,
  AlertTriangle,
  X,
} from 'lucide-react';

// ─── Helpers ─────────────────────────────────────────────────────────────────
const formatDA = (amount) =>
  new Intl.NumberFormat('fr-DZ', {
    style: 'currency',
    currency: 'DZD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);

const pct = (spent, limit) => Math.min(100, Math.round((spent / limit) * 100));
const barColor = (p) =>
  p >= 100 ? 'bg-red-500' : p >= 80 ? 'bg-amber-500' : 'bg-emerald-500';

// ─── Modal ────────────────────────────────────────────────────────────────────
function AddBudgetModal({ accountId, onClose, onSaved }) {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    category_id: '',
    limit_da: '',
    period_type: 'MENSUEL',
    start_date: new Date().toISOString().split('T')[0],
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    client.get('/categories').then((r) => setCategories(r.data));
  }, []);

  // Flatten tree
  const flat = [];
  const walk = (nodes, depth = 0) => {
    for (const cat of nodes) {
      flat.push({ ...cat, depth });
      if (cat.children?.length) walk(cat.children, depth + 1);
    }
  };
  walk(categories);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await client.post('/budgets', {
        account_id: accountId,
        category_id: Number(form.category_id),
        limit_da: Number(form.limit_da),
        period_type: form.period_type,
        start_date: form.start_date,
      });
      onSaved();
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <PiggyBank className="w-5 h-5 text-blue-600" />
            Nouveau budget
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Catégorie
            </label>
            <select
              required
              value={form.category_id}
              onChange={(e) => setForm({ ...form, category_id: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Choisir une catégorie</option>
              {flat.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {'  '.repeat(cat.depth)}{cat.depth > 0 ? '└ ' : ''}{cat.name_fr}
                </option>
              ))}
            </select>
          </div>

          {/* Limit */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Plafond mensuel (DA)
            </label>
            <input
              required
              type="number"
              min="1"
              value={form.limit_da}
              onChange={(e) => setForm({ ...form, limit_da: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="ex: 30000"
            />
          </div>

          {/* Period */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Période
            </label>
            <select
              value={form.period_type}
              onChange={(e) => setForm({ ...form, period_type: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="MENSUEL">Mensuel</option>
              <option value="HEBDOMADAIRE">Hebdomadaire</option>
              <option value="RAMADAN">Ramadan</option>
            </select>
          </div>

          {/* Start date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Date de début
            </label>
            <input
              type="date"
              required
              value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-60 transition"
            >
              {saving ? 'Enregistrement…' : 'Créer le budget'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Budget Card ──────────────────────────────────────────────────────────────
function BudgetCard({ budget, catName, onDelete }) {
  const p = pct(budget.spent_da, Number(budget.limit_da));
  const remaining = Number(budget.limit_da) - budget.spent_da;
  const overBudget = remaining < 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow-md transition">
      {/* Top row */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-gray-900 dark:text-white">{catName}</p>
          <p className="text-xs text-gray-400 mt-0.5 uppercase tracking-wide">
            {budget.period_type}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {overBudget ? (
            <AlertTriangle className="w-5 h-5 text-red-500" />
          ) : p >= 80 ? (
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          )}
          <button
            onClick={() => onDelete(budget.id)}
            className="text-gray-300 hover:text-red-400 transition"
            title="Supprimer"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2.5 mb-3 overflow-hidden">
        <div
          className={`h-2.5 rounded-full transition-all duration-500 ${barColor(p)}`}
          style={{ width: `${p}%` }}
        />
      </div>

      {/* Amounts */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500 dark:text-gray-400">
          Dépensé:{' '}
          <span className="font-semibold text-gray-800 dark:text-white">
            {formatDA(budget.spent_da)}
          </span>
        </span>
        <span className={overBudget ? 'text-red-600 font-semibold' : 'text-gray-500 dark:text-gray-400'}>
          {overBudget
            ? `Dépassé de ${formatDA(Math.abs(remaining))}`
            : `Reste: ${formatDA(remaining)}`}
        </span>
      </div>

      {/* Limit & Percentage */}
      <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
        <span>Plafond: {formatDA(Number(budget.limit_da))}</span>
        <span className={`font-semibold ${p >= 100 ? 'text-red-500' : p >= 80 ? 'text-amber-500' : 'text-emerald-500'}`}>
          {p}%
        </span>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function BudgetsPage() {
  const { selectedAccountId } = useAuthStore();
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchBudgets = async () => {
    if (!selectedAccountId) return;
    setLoading(true);
    try {
      const [bRes, cRes] = await Promise.all([
        client.get(`/budgets?account_id=${selectedAccountId}`),
        client.get('/categories'),
      ]);
      setBudgets(bRes.data);

      // Flatten categories into a map id → name_fr
      const map = {};
      const walk = (nodes) => {
        for (const c of nodes) {
          map[c.id] = c.name_fr;
          if (c.children?.length) walk(c.children);
        }
      };
      walk(cRes.data);
      setCategories(map);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, [selectedAccountId]);

  const handleDelete = async (id) => {
    if (!confirm('Supprimer ce budget ?')) return;
    await client.delete(`/budgets/${id}`);
    setBudgets((prev) => prev.filter((b) => b.id !== id));
  };

  // Summary stats
  const totalLimit = budgets.reduce((s, b) => s + Number(b.limit_da), 0);
  const totalSpent = budgets.reduce((s, b) => s + (b.spent_da || 0), 0);
  const overCount  = budgets.filter((b) => b.spent_da > Number(b.limit_da)).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <PiggyBank className="w-7 h-7 text-blue-600" />
            Budgets
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1 text-sm">
            Suivi de vos plafonds de dépenses par catégorie
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4" />
          Nouveau budget
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{budgets.length}</p>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-wide">Budgets actifs</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm text-center">
          <p className="text-2xl font-bold text-blue-600">{formatDA(totalSpent)}</p>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-wide">Total dépensé</p>
        </div>
        <div className={`rounded-xl border p-4 shadow-sm text-center ${overCount > 0 ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-700'}`}>
          <p className={`text-2xl font-bold ${overCount > 0 ? 'text-red-600' : 'text-green-600'}`}>
            {overCount}
          </p>
          <p className={`text-xs mt-1 uppercase tracking-wide ${overCount > 0 ? 'text-red-500' : 'text-green-500'}`}>
            Budgets dépassés
          </p>
        </div>
      </div>

      {/* Progress summary bar */}
      {totalLimit > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2 text-sm">
            <span className="font-medium text-gray-700 dark:text-gray-300">
              Utilisation globale des budgets
            </span>
            <span className="text-gray-500 dark:text-gray-400">
              {formatDA(totalSpent)} / {formatDA(totalLimit)}
            </span>
          </div>
          <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-700 ${barColor(pct(totalSpent, totalLimit))}`}
              style={{ width: `${pct(totalSpent, totalLimit)}%` }}
            />
          </div>
          <p className="text-xs text-right text-gray-400 mt-1">
            {pct(totalSpent, totalLimit)}% utilisé
          </p>
        </div>
      )}

      {/* Budget Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : budgets.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <TrendingDown className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-lg font-medium">Aucun budget défini</p>
          <p className="text-sm mt-1">Cliquez sur « Nouveau budget » pour commencer le suivi.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {budgets.map((b) => (
            <BudgetCard
              key={b.id}
              budget={b}
              catName={categories[b.category_id] || `Catégorie ${b.category_id}`}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <AddBudgetModal
          accountId={selectedAccountId}
          onClose={() => setShowModal(false)}
          onSaved={fetchBudgets}
        />
      )}
    </div>
  );
}
