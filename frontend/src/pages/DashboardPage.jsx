import { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { formatCurrency } from '../utils/formatters';
import CategoryPieChart from '../components/charts/CategoryPieChart';
import MonthlyLineChart from '../components/charts/MonthlyLineChart';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await apiClient.get('/dashboard/summary');
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading dashboard...</div>;
  if (!data) return <div className="p-8 text-center text-red-500">Failed to load dashboard.</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard Overview</h2>
      
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Balance</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(data.total_balance)}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Monthly Income</h3>
          <p className="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">{formatCurrency(data.monthly_income)}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Monthly Expenses</h3>
          <p className="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">{formatCurrency(data.monthly_expenses)}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Trend Chart */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">6-Month Trend</h3>
          <div className="h-80">
            <MonthlyLineChart data={data.monthly_trends} />
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Expenses by Category</h3>
          <div className="h-80">
            <CategoryPieChart data={data.expenses_by_category} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
