import React from "react";

export default function MonthlySummary({ summaryData, selectedMonth, onMonthChange, loading }) {
  const totalIncome = summaryData.reduce((acc, row) => acc + row.total_income, 0);
  const totalExpense = summaryData.reduce((acc, row) => acc + row.total_expense, 0);
  const netSavings = totalIncome - totalExpense;

  return (
    <div className="card summary-card">
      <div className="card-header summary-header">
        <div>
          <h2 className="card-title">Monthly Financial Summary</h2>
          <p className="card-subtitle">
            Category breakdown of income and expenses
          </p>
        </div>
        <div className="summary-month-control">
          <label htmlFor="summary-month-picker">Filter Month:</label>
          <input
            id="summary-month-picker"
            type="month"
            value={selectedMonth}
            onChange={(e) => onMonthChange(e.target.value)}
          />
          {selectedMonth && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => onMonthChange("")}
            >
              All Months
            </button>
          )}
        </div>
      </div>

      {/* KPI Balance Cards */}
      <div className="kpi-grid">
        <div className="kpi-card kpi-income">
          <div className="kpi-label">Total Income</div>
          <div className="kpi-value">+₹{totalIncome.toFixed(2)}</div>
        </div>
        <div className="kpi-card kpi-expense">
          <div className="kpi-label">Total Expense</div>
          <div className="kpi-value">-₹{totalExpense.toFixed(2)}</div>
        </div>
        <div className={`kpi-card ${netSavings >= 0 ? "kpi-net-positive" : "kpi-net-negative"}`}>
          <div className="kpi-label">Net Balance</div>
          <div className="kpi-value">
            {netSavings >= 0 ? `+₹${netSavings.toFixed(2)}` : `-₹${Math.abs(netSavings).toFixed(2)}`}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="state-container">
          <div className="spinner"></div>
          <p>Calculating aggregates...</p>
        </div>
      ) : summaryData.length === 0 ? (
        <div className="state-container empty-state">
          <span className="empty-icon">📊</span>
          <p>No summary data available for the selected month.</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="data-table summary-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Category</th>
                <th className="text-right">Income</th>
                <th className="text-right">Expense</th>
                <th className="text-right">Net Category</th>
              </tr>
            </thead>
            <tbody>
              {summaryData.map((row, idx) => {
                const rowNet = row.total_income - row.total_expense;
                return (
                  <tr key={`${row.month}-${row.category}-${idx}`}>
                    <td><strong>{row.month}</strong></td>
                    <td>
                      <span className="badge badge-category">{row.category}</span>
                    </td>
                    <td className="text-right amount-income">
                      {row.total_income > 0 ? `+₹${row.total_income.toFixed(2)}` : "₹0.00"}
                    </td>
                    <td className="text-right amount-expense">
                      {row.total_expense > 0 ? `-₹${row.total_expense.toFixed(2)}` : "₹0.00"}
                    </td>
                    <td className={`text-right font-medium ${rowNet >= 0 ? "amount-income" : "amount-expense"}`}>
                      {rowNet >= 0 ? `+₹${rowNet.toFixed(2)}` : `-₹${Math.abs(rowNet).toFixed(2)}`}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
