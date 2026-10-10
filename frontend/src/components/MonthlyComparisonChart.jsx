import React, { useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function MonthlyComparisonChart({ allSummaryData }) {
  const [chartType, setChartType] = useState("bar"); // "bar" or "line"

  // Aggregate monthly totals: { month: "YYYY-MM", income: 0, expense: 0, net: 0 }
  const monthlyAggregates = React.useMemo(() => {
    if (!allSummaryData || allSummaryData.length === 0) return [];

    const map = {};
    allSummaryData.forEach((row) => {
      if (!map[row.month]) {
        map[row.month] = { month: row.month, income: 0, expense: 0 };
      }
      map[row.month].income += row.total_income;
      map[row.month].expense += row.total_expense;
    });

    return Object.values(map)
      .map((item) => ({
        ...item,
        income: parseFloat(item.income.toFixed(2)),
        expense: parseFloat(item.expense.toFixed(2)),
        net: parseFloat((item.income - item.expense).toFixed(2)),
      }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [allSummaryData]);

  if (monthlyAggregates.length === 0) {
    return (
      <div className="card chart-card">
        <h2 className="card-title">Monthly Trends (Bonus)</h2>
        <div className="state-container empty-state">
          <span className="empty-icon">📈</span>
          <p>No historical data available for monthly comparison.</p>
        </div>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-title"><strong>Month: {label}</strong></p>
          {payload.map((p, idx) => (
            <p key={idx} style={{ color: p.color }}>
              {p.name}: ${p.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card chart-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Monthly Financial Trends</h2>
          <p className="card-subtitle">
            Compare income vs. expenses over time
          </p>
        </div>
        <div className="chart-toggle-group">
          <button
            type="button"
            className={`btn btn-xs ${chartType === "bar" ? "btn-primary" : "btn-outline"}`}
            onClick={() => setChartType("bar")}
          >
            📊 Bar Comparison
          </button>
          <button
            type="button"
            className={`btn btn-xs ${chartType === "line" ? "btn-primary" : "btn-outline"}`}
            onClick={() => setChartType("line")}
          >
            📈 Expense Trend
          </button>
        </div>
      </div>

      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          {chartType === "bar" ? (
            <BarChart data={monthlyAggregates} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" height={36} />
              <Bar dataKey="income" name="Total Income" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="expense" name="Total Expense" fill="#f43f5e" radius={[4, 4, 0, 0]} />
            </BarChart>
          ) : (
            <LineChart data={monthlyAggregates} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" height={36} />
              <Line
                type="monotone"
                dataKey="expense"
                name="Monthly Expenses"
                stroke="#f43f5e"
                strokeWidth={3}
                dot={{ r: 5, fill: "#f43f5e" }}
                activeDot={{ r: 8 }}
              />
              <Line
                type="monotone"
                dataKey="income"
                name="Monthly Income"
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 4, fill: "#10b981" }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
