import React, { useState, useEffect, useCallback } from "react";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";
import MonthlySummary from "./components/MonthlySummary";
import ExpensePieChart from "./components/ExpensePieChart";
import { listTransactions, getSummary, getErrorMessage } from "./api";

export default function App() {
  const [transactions, setTransactions] = useState([]);
  const [summaryData, setSummaryData] = useState([]);
  const [loadingTransactions, setLoadingTransactions] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [globalError, setGlobalError] = useState(null);

  // Filters state
  const [filters, setFilters] = useState({
    month: "",
    type: "",
    category: "",
  });

  // Summary month filter
  const [summaryMonth, setSummaryMonth] = useState("");

  // Counter to trigger data refreshes across components
  const [refreshTick, setRefreshTick] = useState(0);

  const triggerRefresh = useCallback(() => {
    setRefreshTick((prev) => prev + 1);
  }, []);

  // Fetch transactions
  const fetchTransactions = useCallback(async () => {
    setLoadingTransactions(true);
    setGlobalError(null);
    try {
      const data = await listTransactions(filters);
      setTransactions(data);
    } catch (err) {
      setGlobalError(`Failed to load transactions: ${getErrorMessage(err)}`);
    } finally {
      setLoadingTransactions(false);
    }
  }, [filters]);

  // Fetch summary data
  const fetchSummary = useCallback(async () => {
    setLoadingSummary(true);
    try {
      const data = await getSummary(summaryMonth || null);
      setSummaryData(data);
    } catch (err) {
      console.error("Failed to load summary:", err);
    } finally {
      setLoadingSummary(false);
    }
  }, [summaryMonth]);

  // Effect to load data on filter change or manual refresh trigger
  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions, refreshTick]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary, refreshTick]);

  // Real-time updates (Bonus): Poll every 10 seconds when tab is active
  useEffect(() => {
    const interval = setInterval(() => {
      if (document.visibilityState === "visible") {
        fetchTransactions();
        fetchSummary();
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [fetchTransactions, fetchSummary]);

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <header className="navbar">
        <div className="brand">
          <span className="brand-icon">💳</span>
          <div>
            <span className="brand-title">FinanceTracker</span>
            <span className="brand-badge">Live API</span>
          </div>
        </div>

        <div className="nav-actions">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span>API Connected (:8000)</span>
          </div>
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={triggerRefresh}
            title="Refresh Data"
          >
            ↻ Refresh
          </button>
        </div>
      </header>

      {/* Main Body */}
      <main className="main-content">
        {globalError && (
          <div className="alert alert-error" role="alert">
            <span className="alert-icon">⚠️</span>
            <span>{globalError}</span>
          </div>
        )}

        {/* Top Section: Form + Chart */}
        <section className="top-grid">
          <TransactionForm onTransactionAdded={triggerRefresh} />
          <ExpensePieChart summaryData={summaryData} selectedMonth={summaryMonth} />
        </section>

        {/* Monthly Summary Section */}
        <section>
          <MonthlySummary
            summaryData={summaryData}
            selectedMonth={summaryMonth}
            onMonthChange={setSummaryMonth}
            loading={loadingSummary}
          />
        </section>

        {/* Filterable Transactions List */}
        <section>
          <TransactionList
            transactions={transactions}
            loading={loadingTransactions}
            filters={filters}
            onFilterChange={setFilters}
            onDataChanged={triggerRefresh}
          />
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Personal Finance Tracker • FastAPI + SQLite + ReactJS • Clean Architecture</p>
      </footer>
    </div>
  );
}
