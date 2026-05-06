import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import TransactionsPage from './pages/TransactionsPage';
import InsightsPage from './pages/InsightsPage';
import BudgetsPage from './pages/BudgetsPage';
import PredictionsPage from './pages/PredictionsPage';

function ProtectedRoute({ children }) {
  const token = useAuthStore((state) => state.token);
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index                   element={<DashboardPage />} />
          <Route path="transactions"     element={<TransactionsPage />} />
          <Route path="insights"         element={<InsightsPage />} />
          <Route path="budgets"          element={<BudgetsPage />} />
          <Route path="predictions"      element={<PredictionsPage />} />
          <Route path="*"                element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
