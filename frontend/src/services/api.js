// All calls to the Python backend go through this file.
const BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");
const TOKEN_KEY = "dw_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY));

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

function messageFrom(data, status) {
  const d = data && data.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((e) => {
        const field = (e.loc || []).slice(1).join(" ");
        const msg = String(e.msg || "").replace(/^Value error, /, "");
        return field ? `${field}: ${msg}` : msg;
      })
      .join(". ");
  }
  if (status >= 500) return "Something went wrong on our side. Please try again.";
  return "Request failed.";
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${BASE}${path}`, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined });
  } catch {
    throw new ApiError("Cannot reach the server. Check your internet and try again.", 0);
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    if (res.status === 401 && token) window.dispatchEvent(new Event("dw:unauthorized"));
    throw new ApiError(messageFrom(data, res.status), res.status);
  }
  return data;
}

export const api = {
  // public
  config: () => request("/config", { auth: false }),
  categories: () => request("/categories", { auth: false }),
  menu: (params = {}) => {
    const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== undefined && v !== "" && v !== null)).toString();
    return request(`/menu${q ? `?${q}` : ""}`, { auth: false });
  },
  // auth
  register: (body) => request("/auth/register", { method: "POST", body, auth: false }),
  login: (body) => request("/auth/login", { method: "POST", body, auth: false }),
  me: () => request("/users/me"),
  // orders
  createOrder: (body) => request("/orders", { method: "POST", body }),
  myOrders: () => request("/orders"),
  order: (id) => request(`/orders/${id}`),
  cancelOrder: (id) => request(`/orders/${id}/cancel`, { method: "POST" }),
  // admin
  admin: {
    stats: () => request("/admin/stats"),
    menu: () => request("/admin/menu"),
    createItem: (body) => request("/admin/menu", { method: "POST", body }),
    updateItem: (id, body) => request(`/admin/menu/${id}`, { method: "PUT", body }),
    deleteItem: (id) => request(`/admin/menu/${id}`, { method: "DELETE" }),
    setAvailability: (id, is_available) => request(`/admin/menu/${id}/availability`, { method: "PATCH", body: { is_available } }),
    categories: () => request("/admin/categories"),
    createCategory: (body) => request("/admin/categories", { method: "POST", body }),
    updateCategory: (id, body) => request(`/admin/categories/${id}`, { method: "PUT", body }),
    deleteCategory: (id) => request(`/admin/categories/${id}`, { method: "DELETE" }),
    orders: (status) => request(`/admin/orders${status ? `?status=${status}` : ""}`),
    setStatus: (id, status) => request(`/admin/orders/${id}/status`, { method: "PATCH", body: { status } }),
    customers: () => request("/admin/customers"),
  },
};
