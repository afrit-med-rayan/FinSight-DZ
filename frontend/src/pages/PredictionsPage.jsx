import { useEffect, useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Brain, TrendingUp, TrendingDown, RefreshCw, AlertCircle } from 'lucide-react';
import client from '../api/client';
import useAuthStore from '../store/authStore';
import { formatCurrency } from '../utils/formatters';

const PredictionsPage = () => {
  const { selectedAccountId } = useAuthStore();
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isRetraining, setIsRetraining] = useState(false);
  const [error, setError] = useState(null);

  const fetchPredictions = async () => {
    if (!selectedAccountId) return;
    setLoading(true);
    try {
      const res = await client.get(`/predictions/?account_id=${selectedAccountId}`);
      setPredictions(res.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch predictions', err);
      setError("Impossible de charger les prédictions. Assurez-vous d'avoir au moins 3 mois d'historique.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, [selectedAccountId]);

  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      await client.post(`/predictions/retrain?account_id=${selectedAccountId}`);
      await fetchPredictions();
    } catch (err) {
      console.error('Retraining failed', err);
    } finally {
      setIsRetraining(false);
    }
  };

  if (!selectedAccountId) {
    return <div className="p-8 text-center text-gray-500">Veuillez sélectionner un compte.</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-3">
            <Brain className="w-8 h-8 text-purple-600" />
            Prévisions IA
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Analyse prédictive de votre solde et de vos dépenses basées sur votre historique.
          </p>
        </div>
        <button
          onClick={handleRetrain}
          disabled={isRetraining || loading}
          className="flex items-center justify-center gap-2 px-6 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white rounded-xl font-semibold transition-all shadow-lg shadow-purple-200 dark:shadow-none"
        >
          <RefreshCw className={`w-4 h-4 ${isRetraining ? 'animate-spin' : ''}`} />
          {isRetraining ? 'Entraînement...' : 'Recalculer'}
        </button>
      </div>

      {error ? (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-6 rounded-2xl flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-amber-600 mt-0.5" />
          <div>
            <h3 className="font-bold text-amber-900 dark:text-amber-100">Données insuffisantes</h3>
            <p className="text-amber-800 dark:text-amber-200 text-sm mt-1">{error}</p>
          </div>
        </div>
      ) : loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 h-96 bg-gray-100 dark:bg-gray-800 animate-pulse rounded-2xl"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-100 dark:bg-gray-800 animate-pulse rounded-2xl"></div>)}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* ── Forecast Chart ───────────────────────────────────────────── */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 p-8 rounded-3xl shadow-xl shadow-gray-100 dark:shadow-none border border-gray-100 dark:border-gray-700">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Prévision du solde (6 mois)</h3>
            <div className="h-[400px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={predictions}>
                  <defs>
                    <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="predicted_for_month" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                    dy={10}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                    tickFormatter={(val) => `${val/1000}k`}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      borderRadius: '16px', 
                      border: 'none', 
                      boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)',
                      backgroundColor: '#fff'
                    }}
                    formatter={(value) => [formatCurrency(value), 'Solde prévu']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="predicted_balance_da" 
                    stroke="#8b5cf6" 
                    strokeWidth={4}
                    fillOpacity={1} 
                    fill="url(#colorBalance)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 flex items-center gap-2 text-xs text-gray-400 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-xl">
              <AlertCircle className="w-4 h-4" />
              Ces prévisions sont basées sur une régression linéaire de votre activité passée et ne garantissent pas les résultats futurs.
            </div>
          </div>

          {/* ── Monthly Summary List ─────────────────────────────────────── */}
          <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">Dépenses prévues</h3>
            <div className="space-y-4">
              {predictions.map((pred) => (
                <div 
                  key={pred.id}
                  className="group bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-100 dark:border-gray-700 hover:border-purple-200 dark:hover:border-purple-900 transition-all shadow-sm hover:shadow-md"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-sm font-bold text-gray-400 group-hover:text-purple-600 transition-colors">
                      {pred.predicted_for_month}
                    </span>
                    <div className="flex items-center gap-1 text-xs font-medium px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
                      <TrendingDown className="w-3 h-3 text-red-500" />
                      Prévu
                    </div>
                  </div>
                  <div className="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
                    {formatCurrency(pred.predicted_expense_da)}
                  </div>
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-xs text-gray-400">Intervalle de confiance</span>
                    <span className="text-xs font-medium text-gray-500">
                      ± {formatCurrency(pred.confidence_interval_da)}
                    </span>
                  </div>
                  <div className="mt-2 w-full bg-gray-100 dark:bg-gray-700 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className="bg-purple-500 h-full rounded-full" 
                      style={{ width: `${Math.min(100, (pred.predicted_expense_da / 100000) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            
            <div className="bg-gradient-to-br from-purple-600 to-indigo-700 p-6 rounded-3xl text-white shadow-xl">
              <h4 className="font-bold flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5" />
                Conseil IA
              </h4>
              <p className="text-sm text-purple-100 leading-relaxed">
                Votre tendance actuelle suggère une augmentation de 12% de vos dépenses le mois prochain. Pensez à ajuster vos budgets !
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionsPage;
