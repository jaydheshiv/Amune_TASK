import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (typeof process !== "undefined" && process.env?.REACT_APP_API_URL) ||
  "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Extract user-friendly error message from Axios error
 */
export function getErrorMessage(error) {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
    }
    return JSON.stringify(detail);
  }
  return error.message || "An unexpected error occurred.";
}

/**
 * Create a new transaction
 */
export async function createTransaction(data) {
  const response = await apiClient.post("/transactions/", data);
  return response.data;
}

/**
 * List transactions with optional filters: month, type, category
 */
export async function listTransactions(filters = {}) {
  const params = {};
  if (filters.month) params.month = filters.month;
  if (filters.type) params.type = filters.type;
  if (filters.category) params.category = filters.category;

  const response = await apiClient.get("/transactions/", { params });
  return response.data;
}

/**
 * Get monthly category aggregation summary
 */
export async function getSummary(month = null) {
  const params = {};
  if (month) params.month = month;

  const response = await apiClient.get("/transactions/summary", { params });
  return response.data;
}

/**
 * Delete a transaction by ID
 */
export async function deleteTransaction(id) {
  const response = await apiClient.delete(`/transactions/${id}`);
  return response.data;
}

/**
 * Reclassify a transaction's category
 */
export async function reclassifyTransaction(id, category) {
  const response = await apiClient.patch(`/transactions/${id}/reclassify`, {
    category,
  });
  return response.data;
}

export default apiClient;
