import React, { useState, useEffect, useCallback } from "react";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";
import MonthlySummary from "./components/MonthlySummary";
import ExpensePieChart from "./components/ExpensePieChart";
import MonthlyComparisonChart from "./components/MonthlyComparisonChart";
import { listTransactions, getSummary, getErrorMessage } from "./api";

const TABS = [
  { id: "dashboard", label: "Dashboard",   icon: "⊞" },
  { id: "add",       label: "Add",          icon: "＋" },
  { id: "summary",   label: "Summary",      icon: "◈" },
  { id: "records",   label: "Records",      icon: "≡" },
  { id: "trends",    label: "Trends",       icon: "↗" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [transactions, setTransactions] = useState([]);
  const [summaryData, setSummaryData] = useState([]);
  const [allSummaryData, setAllSummaryData] = useState([]);
  const [loadingTransactions, setLoadingTransactions] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [globalError, setGlobalError] = useState(null);

  const [filters, setFilters] = useState({ month: "", type: "", category: "" });
  const [summaryMonth, setSummaryMonth] = useState("");
  const [refreshTick, setRefreshTick] = useState(0);

  const triggerRefresh = useCallback(() => {
    setRefreshTick((prev) => prev + 1);
  }, []);

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

  const fetchSummary = useCallback(async () => {
    setLoadingSummary(true);
    try {
      const [filteredData, overallData] = await Promise.all([
        getSummary(summaryMonth || null),
        getSummary(null),
      ]);
      setSummaryData(filteredData);
      setAllSummaryData(overallData);
    } catch (err) {
      console.error("Failed to load summary:", err);
    } finally {
      setLoadingSummary(false);
    }
  }, [summaryMonth, refreshTick]);

  useEffect(() => { fetchTransactions(); }, [fetchTransactions, refreshTick]);
  useEffect(() => { fetchSummary(); }, [fetchSummary]);

  // Smart polling — pause when tab hidden
  useEffect(() => {
    const interval = setInterval(() => {
      if (document.visibilityState === "visible") {
        fetchTransactions();
        fetchSummary();
      }
    }, parseInt(import.meta?.env?.VITE_POLL_INTERVAL_MS || "10000"));
    return () => clearInterval(interval);
  }, [fetchTransactions, fetchSummary]);

  // Computed totals for dashboard
  const totalIncome  = allSummaryData.reduce((s, r) => s + r.total_income, 0);
  const totalExpense = allSummaryData.reduce((s, r) => s + r.total_expense, 0);
  const netBalance   = totalIncome - totalExpense;

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    // auto-refresh when switching to data-heavy tabs
    if (tabId === "records" || tabId === "summary" || tabId === "trends") {
      triggerRefresh();
    }
  };

  return (
    <div className="app-shell">
      {/* ── Top Navbar ─────────────────────────────────────── */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-logo">A</div>
          <div className="brand-text">
            <span className="brand-title">Amune</span>
            <span className="brand-sub">Expense Tracker</span>
          </div>
        </div>

        <nav className="tab-bar" role="tablist" aria-label="Main navigation">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              className={`tab-btn ${activeTab === tab.id ? "tab-active" : ""}`}
              onClick={() => handleTabChange(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
              {activeTab === tab.id && <span className="tab-indicator" />}
            </button>
          ))}
        </nav>

        <div className="nav-right">
          <div className="status-pill">
            <span className="status-dot" />
            <span>Live</span>
          </div>
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={triggerRefresh}
            title="Refresh all data"
          >
            ↻ Refresh
          </button>
        </div>
      </header>

      {/* ── Global Error ────────────────────────────────────── */}
      {globalError && (
        <div className="global-alert">
          <span>⚠️</span> {globalError}
        </div>
      )}

      {/* ── Page Content ────────────────────────────────────── */}
      <main className="page-content">

        {/* ═══════════ DASHBOARD TAB ═══════════ */}
        {activeTab === "dashboard" && (
          <div className="tab-page fade-in">
            <div className="page-heading">
              <h1 className="page-title">Overview</h1>
              <p className="page-subtitle">Your complete financial snapshot at a glance</p>
            </div>

            {/* KPI Strip */}
            <div className="kpi-strip">
              <div className="kpi-tile kpi-income">
                <div className="kpi-icon">↑</div>
                <div>
                  <div className="kpi-label">Total Income</div>
                  <div className="kpi-value">+₹{totalIncome.toFixed(2)}</div>
                </div>
              </div>
              <div className="kpi-tile kpi-expense">
                <div className="kpi-icon">↓</div>
                <div>
                  <div className="kpi-label">Total Expense</div>
                  <div className="kpi-value">-₹{totalExpense.toFixed(2)}</div>
                </div>
              </div>
              <div className={`kpi-tile ${netBalance >= 0 ? "kpi-net-pos" : "kpi-net-neg"}`}>
                <div className="kpi-icon">◈</div>
                <div>
                  <div className="kpi-label">Net Balance</div>
                  <div className="kpi-value">
                    {netBalance >= 0 ? `+₹${netBalance.toFixed(2)}` : `-₹${Math.abs(netBalance).toFixed(2)}`}
                  </div>
                </div>
              </div>
              <div className="kpi-tile kpi-count">
                <div className="kpi-icon">≡</div>
                <div>
                  <div className="kpi-label">Transactions</div>
                  <div className="kpi-value">{transactions.length}</div>
                </div>
              </div>
            </div>

            {/* Charts row */}
            <div className="dash-grid">
              <ExpensePieChart summaryData={summaryData} selectedMonth={summaryMonth} />
              <MonthlyComparisonChart allSummaryData={allSummaryData} />
            </div>

            {/* Recent 5 transactions */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h2 className="card-title">Recent Transactions</h2>
                  <p className="card-subtitle">Last {Math.min(5, transactions.length)} entries</p>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => setActiveTab("records")}>
                  View all →
                </button>
              </div>
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Description</th>
                      <th>Category</th>
                      <th>Type</th>
                      <th className="text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.slice(0, 5).map((tx) => {
                      const isIncome = tx.transaction_type === "income";
                      return (
                        <tr key={tx.id} className={isIncome ? "row-income" : "row-expense"}>
                          <td className="cell-date">
                            {new Date(tx.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
                          </td>
                          <td><strong>{tx.description}</strong></td>
                          <td><span className="badge badge-category">{tx.category}</span></td>
                          <td>
                            <span className={`badge ${isIncome ? "badge-income" : "badge-expense"}`}>
                              {tx.transaction_type}
                            </span>
                          </td>
                          <td className={`text-right ${isIncome ? "amount-income" : "amount-expense"}`}>
                            {isIncome ? `+₹${tx.amount.toFixed(2)}` : `-₹${tx.amount.toFixed(2)}`}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ═══════════ ADD TAB ═══════════ */}
        {activeTab === "add" && (
          <div className="tab-page fade-in">
            <div className="page-heading">
              <h1 className="page-title">Add Transaction</h1>
              <p className="page-subtitle">Record a new income or expense — it gets auto-categorized instantly</p>
            </div>
            <div className="add-layout">
              <TransactionForm onTransactionAdded={() => { triggerRefresh(); }} />
              <ExpensePieChart summaryData={summaryData} selectedMonth={summaryMonth} />
            </div>
          </div>
        )}

        {/* ═══════════ SUMMARY TAB ═══════════ */}
        {activeTab === "summary" && (
          <div className="tab-page fade-in">
            <div className="page-heading">
              <h1 className="page-title">Monthly Summary</h1>
              <p className="page-subtitle">Category breakdown of income and expenses by month</p>
            </div>
            <MonthlySummary
              summaryData={summaryData}
              selectedMonth={summaryMonth}
              onMonthChange={setSummaryMonth}
              loading={loadingSummary}
            />
          </div>
        )}

        {/* ═══════════ RECORDS TAB ═══════════ */}
        {activeTab === "records" && (
          <div className="tab-page fade-in">
            <div className="page-heading">
              <h1 className="page-title">All Records</h1>
              <p className="page-subtitle">Filter, reclassify, and manage all your transactions</p>
            </div>
            <TransactionList
              transactions={transactions}
              loading={loadingTransactions}
              filters={filters}
              onFilterChange={setFilters}
              onDataChanged={triggerRefresh}
            />
          </div>
        )}

        {/* ═══════════ TRENDS TAB ═══════════ */}
        {activeTab === "trends" && (
          <div className="tab-page fade-in">
            <div className="page-heading">
              <h1 className="page-title">Financial Trends</h1>
              <p className="page-subtitle">Historical income vs. expense analysis across all months</p>
            </div>
            <MonthlyComparisonChart allSummaryData={allSummaryData} />
          </div>
        )}
      </main>

      <footer className="footer">
        Amune Expense Tracker • FastAPI + SQLite + React • Built for Amune
      </footer>
    </div>
  );
}
