import React, { useState } from "react";
import { createTransaction, getErrorMessage } from "../api";

export default function TransactionForm({ onTransactionAdded }) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [type, setType] = useState("expense");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setError("Amount must be a positive number greater than 0.");
      return;
    }

    if (!description.trim()) {
      setError("Description cannot be empty.");
      return;
    }

    setLoading(true);
    try {
      const created = await createTransaction({
        description: description.trim(),
        amount: parsedAmount,
        transaction_type: type,
      });

      setSuccess(
        `Transaction recorded! Auto-categorized as "${created.category}" (Amount: $${created.amount.toFixed(2)})`
      );
      setDescription("");
      setAmount("");
      setType("expense");
      if (onTransactionAdded) {
        onTransactionAdded();
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card form-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">➕ Add Transaction</h2>
          <p className="card-subtitle">
            Auto-categorized by keywords — just describe it naturally.
          </p>
        </div>
      </div>
      {error && (
        <div className="alert alert-error" role="alert">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success" role="alert">
          <span className="alert-icon">✓</span>
          <span>{success}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="form-grid">
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <input
            id="description"
            type="text"
            placeholder="e.g. McDonald's, Uber, Monthly Salary"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="amount">Amount ($)</label>
          <input
            id="amount"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="transaction_type">Type</label>
          <select
            id="transaction_type"
            value={type}
            onChange={(e) => setType(e.target.value)}
            disabled={loading}
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Adding..." : "+ Add Transaction"}
          </button>
        </div>
      </form>
    </div>
  );
}
