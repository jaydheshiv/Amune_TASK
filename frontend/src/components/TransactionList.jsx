import React, { useState } from "react";
import { deleteTransaction, reclassifyTransaction, getErrorMessage } from "../api";

const PRESET_CATEGORIES = [
  "Food",
  "Transport",
  "Rent",
  "Utilities",
  "Entertainment",
  "Salary",
  "Travel",
  "Healthcare",
  "Uncategorized",
];

export default function TransactionList({
  transactions,
  loading,
  filters,
  onFilterChange,
  onDataChanged,
}) {
  const [editingId, setEditingId] = useState(null);
  const [newCategory, setNewCategory] = useState("");
  const [actionError, setActionError] = useState(null);
  const [actionLoadingId, setActionLoadingId] = useState(null);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this transaction?")) {
      return;
    }
    setActionError(null);
    setActionLoadingId(id);
    try {
      await deleteTransaction(id);
      if (onDataChanged) onDataChanged();
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const startEditing = (tx) => {
    setEditingId(tx.id);
    setNewCategory(tx.category || "Uncategorized");
    setActionError(null);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setNewCategory("");
  };

  const handleReclassify = async (id) => {
    if (!newCategory.trim()) {
      setActionError("Category name cannot be empty.");
      return;
    }
    setActionError(null);
    setActionLoadingId(id);
    try {
      await reclassifyTransaction(id, newCategory.trim());
      setEditingId(null);
      if (onDataChanged) onDataChanged();
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleClearFilters = () => {
    onFilterChange({
      month: "",
      type: "",
      category: "",
    });
  };

  return (
    <div className="card list-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Transactions</h2>
          <p className="card-subtitle">
            Showing {transactions.length} record{transactions.length === 1 ? "" : "s"}
          </p>
        </div>
      </div>

      {actionError && (
        <div className="alert alert-error" role="alert">
          <span className="alert-icon">⚠️</span>
          <span>{actionError}</span>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="filter-toolbar">
        <div className="filter-group">
          <label htmlFor="filter-month">Month</label>
          <input
            id="filter-month"
            type="month"
            value={filters.month || ""}
            onChange={(e) => onFilterChange({ ...filters, month: e.target.value })}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="filter-type">Type</label>
          <select
            id="filter-type"
            value={filters.type || ""}
            onChange={(e) => onFilterChange({ ...filters, type: e.target.value })}
          >
            <option value="">All Types</option>
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="filter-category">Category</label>
          <input
            id="filter-category"
            type="text"
            placeholder="Search category..."
            value={filters.category || ""}
            onChange={(e) => onFilterChange({ ...filters, category: e.target.value })}
          />
        </div>

        {(filters.month || filters.type || filters.category) && (
          <div className="filter-actions">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleClearFilters}
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>

      {/* Transactions Table */}
      {loading ? (
        <div className="state-container">
          <div className="spinner"></div>
          <p>Loading transactions...</p>
        </div>
      ) : transactions.length === 0 ? (
        <div className="state-container empty-state">
          <span className="empty-icon">📂</span>
          <p>No transactions found matching the selected criteria.</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Tag Mode</th>
                <th>Type</th>
                <th className="text-right">Amount</th>
                <th className="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => {
                const isEditing = editingId === tx.id;
                const isBusy = actionLoadingId === tx.id;
                const isIncome = tx.transaction_type === "income";
                const dateStr = new Date(tx.timestamp).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                });

                return (
                  <tr key={tx.id} className={isIncome ? "row-income" : "row-expense"}>
                    <td className="cell-date">{dateStr}</td>
                    <td className="cell-desc">
                      <strong>{tx.description}</strong>
                    </td>
                    <td className="cell-cat">
                      {isEditing ? (
                        <div className="reclassify-input-group">
                          <input
                            type="text"
                            list="preset-categories"
                            value={newCategory}
                            onChange={(e) => setNewCategory(e.target.value)}
                            className="input-sm"
                            placeholder="Category"
                            autoFocus
                          />
                          <datalist id="preset-categories">
                            {PRESET_CATEGORIES.map((c) => (
                              <option key={c} value={c} />
                            ))}
                          </datalist>
                        </div>
                      ) : (
                        <span className="badge badge-category">{tx.category || "Uncategorized"}</span>
                      )}
                    </td>
                    <td>
                      {tx.auto_tagged ? (
                        <span className="badge badge-auto">Auto</span>
                      ) : (
                        <span className="badge badge-manual">Manual</span>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${isIncome ? "badge-income" : "badge-expense"}`}>
                        {tx.transaction_type}
                      </span>
                    </td>
                    <td className={`text-right cell-amount ${isIncome ? "amount-income" : "amount-expense"}`}>
                      {isIncome ? `+₹${tx.amount.toFixed(2)}` : `-₹${tx.amount.toFixed(2)}`}
                    </td>
                    <td className="text-center cell-actions">
                      {isEditing ? (
                        <div className="action-buttons">
                          <button
                            type="button"
                            className="btn btn-primary btn-xs"
                            onClick={() => handleReclassify(tx.id)}
                            disabled={isBusy}
                          >
                            Save
                          </button>
                          <button
                            type="button"
                            className="btn btn-secondary btn-xs"
                            onClick={cancelEditing}
                            disabled={isBusy}
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <div className="action-buttons">
                          <button
                            type="button"
                            className="btn btn-outline btn-xs"
                            onClick={() => startEditing(tx)}
                            disabled={isBusy}
                            title="Reclassify Category"
                          >
                            Reclassify
                          </button>
                          <button
                            type="button"
                            className="btn btn-danger btn-xs"
                            onClick={() => handleDelete(tx.id)}
                            disabled={isBusy}
                            title="Delete Transaction"
                          >
                            Delete
                          </button>
                        </div>
                      )}
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
