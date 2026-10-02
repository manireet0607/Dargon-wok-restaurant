import { Link, useParams } from "react-router-dom";
import { ErrorBox, Loading, StatusBadge } from "../components/Ui";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";
import { STATUS_LABELS, inrStr } from "../services/format";
import { OrderLines } from "./Account";

export default function OrderConfirmation() {
  const { id } = useParams();
  const { data: o, error, loading, reload } = useFetch(() => api.order(id), [id]);
  if (loading) return <div className="wrap section"><Loading /></div>;
  if (error) return <div className="wrap section"><ErrorBox message={error} onRetry={reload} /></div>;

  return (
    <div className="wrap section narrow">
      <div className="card confirm">
        <p className="tick" aria-hidden="true">✓</p>
        <h1>Thank you, {o.customer_name.split(" ")[0]}! Your order is placed.</h1>
        <p className="lead">Order number <strong className="mono">{o.order_number}</strong></p>
        <p><StatusBadge status={o.order_status} label={STATUS_LABELS[o.order_status]} /> Pay <strong>{inrStr(o.total_amount)}</strong> in cash on delivery.</p>
        <OrderLines order={o} />
        <p className="muted">Delivering to: {o.delivery_address}</p>
        <div className="row center-row">
          <Link to="/account" className="btn">View my orders</Link>
          <Link to="/menu" className="btn ghost">Order more</Link>
        </div>
      </div>
    </div>
  );
}
