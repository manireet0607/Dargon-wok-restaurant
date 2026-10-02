import { Link } from "react-router-dom";
import { ErrorBox, Loading } from "../../components/Ui";
import { useFetch } from "../../hooks/useFetch";
import { api } from "../../services/api";
import { STATUS_LABELS, inrStr } from "../../services/format";

export default function Overview() {
  const { data: s, error, loading, reload } = useFetch(() => api.admin.stats(), []);
  if (loading) return <Loading />;
  if (error) return <ErrorBox message={error} onRetry={reload} />;
  return (
    <>
      <h1>Overview</h1>
      <div className="stats">
        <Link to="/admin/orders" className="stat"><span>Total orders</span><strong>{s.total_orders}</strong></Link>
        <div className="stat"><span>Revenue (delivered orders)</span><strong>{inrStr(s.revenue)}</strong></div>
        <Link to="/admin/customers" className="stat"><span>Customers</span><strong>{s.customers}</strong></Link>
        <Link to="/admin/foods" className="stat"><span>Menu items</span><strong>{s.menu_items}</strong></Link>
      </div>
      <h2>Orders by status</h2>
      <div className="stats small">
        {Object.keys(STATUS_LABELS).map((k) => (
          <div className="stat" key={k}><span>{STATUS_LABELS[k]}</span><strong>{s.orders_by_status[k] || 0}</strong></div>
        ))}
      </div>
    </>
  );
}
