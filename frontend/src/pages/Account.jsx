import { useState } from "react";
import { Empty, ErrorBox, Loading, StatusBadge } from "../components/Ui";
import { useAuth } from "../context/AuthContext";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";
import { STATUS_LABELS, fmtDate, inrStr } from "../services/format";

export function OrderLines({ order }) {
  return (
    <table className="tbl">
      <thead><tr><th>Item</th><th className="r">Qty</th><th className="r">Price</th><th className="r">Amount</th></tr></thead>
      <tbody>
        {order.items.map((i) => (
          <tr key={i.id}><td>{i.item_name}</td><td className="r">{i.quantity}</td><td className="r">{inrStr(i.unit_price)}</td><td className="r">{inrStr(i.subtotal)}</td></tr>
        ))}
        <tr className="sumrow"><td colSpan={3}>Subtotal</td><td className="r">{inrStr(order.subtotal)}</td></tr>
        <tr className="sumrow"><td colSpan={3}>Delivery fee</td><td className="r">{inrStr(order.delivery_fee)}</td></tr>
        <tr className="sumrow"><td colSpan={3}>Taxes</td><td className="r">{inrStr(order.tax_amount)}</td></tr>
        <tr className="sumrow total"><td colSpan={3}>Total</td><td className="r">{inrStr(order.total_amount)}</td></tr>
      </tbody>
    </table>
  );
}

export default function Account() {
  const { user } = useAuth();
  const { data, error, loading, reload } = useFetch(() => api.myOrders(), []);
  const [open, setOpen] = useState(null);
  const [msg, setMsg] = useState("");

  const cancel = async (id) => {
    if (!window.confirm("Cancel this order?")) return;
    try { await api.cancelOrder(id); setMsg(""); reload(); } catch (e) { setMsg(e.message); }
  };

  return (
    <div className="wrap section">
      <h1>My account</h1>
      <div className="card profile">
        <div><span className="muted">Name</span><strong>{user.name}</strong></div>
        <div><span className="muted">Email</span><strong>{user.email}</strong></div>
        <div><span className="muted">Phone</span><strong>{user.phone}</strong></div>
      </div>
      <h2>Order history</h2>
      {msg && <p className="error" role="alert">{msg}</p>}
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> :
        data.length === 0 ? <Empty text="You have not placed any orders yet." to="/menu" action="Order something tasty" /> : (
          <ul className="orders">
            {data.map((o) => (
              <li key={o.id} className="card">
                <button className="order-head" onClick={() => setOpen(open === o.id ? null : o.id)} aria-expanded={open === o.id}>
                  <span className="mono">{o.order_number}</span>
                  <span className="muted">{fmtDate(o.created_at)}</span>
                  <StatusBadge status={o.order_status} label={STATUS_LABELS[o.order_status]} />
                  <strong>{inrStr(o.total_amount)}</strong>
                </button>
                {open === o.id && (
                  <div className="order-body">
                    <OrderLines order={o} />
                    <p className="muted">Delivered to: {o.delivery_address}</p>
                    {o.order_status === "pending" && <button className="btn ghost danger-btn" onClick={() => cancel(o.id)}>Cancel order</button>}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
    </div>
  );
}
