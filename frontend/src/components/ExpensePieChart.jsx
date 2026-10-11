import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLOR_PALETTE = [
  "#3b82f6", // blue
  "#ef4444", // red
  "#10b981", // green
  "#f59e0b", // amber
  "#8b5cf6", // purple
  "#ec4899", // pink
  "#14b8a6", // teal
  "#f97316", // orange
  "#6366f1", // indigo
  "#64748b", // slate
];

export default function ExpensePieChart({ summaryData, selectedMonth }) {
  // Aggregate expenses per category
  const categoryExpenses = summaryData
    .filter((item) => item.total_expense > 0)
    .reduce((acc, curr) => {
      const existing = acc.find((x) => x.name === curr.category);
      if (existing) {
        existing.value += curr.total_expense;
      } else {
        acc.push({
          name: curr.category,
          value: parseFloat(curr.total_expense.toFixed(2)),
        });
      }
      return acc;
    }, []);

  const totalExpense = categoryExpenses.reduce((sum, item) => sum + item.value, 0);

  if (categoryExpenses.length === 0) {
    return (
      <div className="card chart-card">
        <h2 className="card-title">Expense Distribution (Bonus)</h2>
        <div className="state-container empty-state">
          <span className="empty-icon">🥧</span>
          <p>No expense data available to display chart.</p>
        </div>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = totalExpense > 0 ? ((data.value / totalExpense) * 100).toFixed(1) : 0;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-title"><strong>{data.name}</strong></p>
          <p className="tooltip-amount">${data.value.toFixed(2)} ({percentage}%)</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card chart-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Expense Breakdown by Category</h2>
          <p className="card-subtitle">
            {selectedMonth ? `Expenses for ${selectedMonth}` : "All Recorded Expenses"} • Total: ${totalExpense.toFixed(2)}
          </p>
        </div>
      </div>

      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={categoryExpenses}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={95}
              innerRadius={50}
              paddingAngle={3}
              label={({ name, percent }) => (percent >= 0.04 ? `${name} ${(percent * 100).toFixed(0)}%` : "")}
              labelLine={({ percent }) => percent >= 0.04}
            >
              {categoryExpenses.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLOR_PALETTE[index % COLOR_PALETTE.length]}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
