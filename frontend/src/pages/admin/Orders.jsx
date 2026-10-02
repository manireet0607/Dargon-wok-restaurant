import { useState } from "react";
import { ErrorBox, Loading, StatusBadge } from "../../components/Ui";
import { useFetch } from "../../hooks/useFetch";
import { api } from "../../services/api";
import { NEXT_STATUS, STATUS_LABELS, fmtDate, inrStr } from "../../services/format";
import { OrderLines } from "../Account";

export default function Orders() {
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState(null);
  const [msg, setMsg] = useState("");
  const { data, error, loading, reload } = useFetch(() => api.admin.orders(filter), [filter]);

  const change = async (order, status) => {
    setMsg("");
    try {
      const updated = await api.admin.setStatus(order.id, status);
      setSelected(updated);
      reload();
    } catch (e) {
      setMsg(e.message);
    }
  };

  return (
    <>
      <div className="between">
        <h1>Orders</h1>
        <select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filter by status">
          <option value="">All statuses</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      {loading && !data ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <div className="scroll">
          <table className="tbl hover">
            <thead><tr><th>Order</th><th>Date</th><th>Customer</th><th className="r">Total</th><th>Payment</th><th>Status</th></tr></thead>
            <tbody>
              {data.length === 0 && <tr><td colSpan={6} className="muted">No orders found.</td></tr>}
              {data.map((o) => (
                <tr key={o.id} onClick={() => { setSelected(o); setMsg(""); }} className={selected?.id === o.id ? "sel" : ""} tabIndex={0} onKeyDown={(e) => e.key === "Enter" && setSelected(o)}>
                  <td className="mono">{o.order_number}</td><td>{fmtDate(o.created_at)}</td><td>{o.customer_name}</td>
                  <td className="r">{inrStr(o.total_amount)}</td><td>{o.payment_method.toUpperCase()} · {o.payment_status}</td>
                  <td><StatusBadge status={o.order_status} label={STATUS_LABELS[o.order_status]} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && (
        <div className="modal" role="dialog" aria-modal="true" aria-label="Order details" onClick={(e) => e.target === e.currentTarget && setSelected(null)}>
          <div className="modal-box">
            <div className="between"><h2 className="mono">{selected.order_number}</h2><button className="linkbtn" onClick={() => setSelected(null)}>Close</button></div>
            <dl className="info">
              <dt>Customer</dt><dd>{selected.customer_name} ({selected.customer_email})</dd>
              <dt>Phone</dt><dd>{selected.customer_phone}</dd>
              <dt>Address</dt><dd>{selected.delivery_address}</dd>
              {selected.special_instructions && (<><dt>Notes</dt><dd>{selected.special_instructions}</dd></>)}
              <dt>Placed</dt><dd>{fmtDate(selected.created_at)}</dd>
              <dt>Status</dt><dd><StatusBadge status={selected.order_status} label={STATUS_LABELS[selected.order_status]} /></dd>
            </dl>
            <OrderLines order={selected} />
            {msg && <p className="error" role="alert">{msg}</p>}
            <div className="row wrapx">
              {NEXT_STATUS[selected.order_status].length === 0 && <span className="muted">This order is final.</span>}
              {NEXT_STATUS[selected.order_status].map((s) => (
                <button key={s} className={`btn small ${s === "cancelled" ? "ghost danger-btn" : ""}`} onClick={() => change(selected, s)}>
                  {s === "cancelled" ? "Cancel order" : `Mark ${STATUS_LABELS[s]}`}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
