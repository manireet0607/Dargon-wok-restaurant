import { Link } from "react-router-dom";

export const Loading = ({ text = "Loading..." }) => <p className="state" role="status">{text}</p>;
export const ErrorBox = ({ message, onRetry }) => (
  <div className="state error" role="alert">
    <p>{message}</p>
    {onRetry && <button className="btn ghost" onClick={onRetry}>Try again</button>}
  </div>
);
export const Empty = ({ text, to, action }) => (
  <div className="state">
    <p>{text}</p>
    {to && <Link className="btn" to={to}>{action}</Link>}
  </div>
);

export function FoodTypeMark({ type }) {
  const veg = type === "veg";
  return (
    <span className={`ftype ${veg ? "veg" : "nonveg"}`} title={veg ? "Vegetarian" : "Non-vegetarian"} role="img" aria-label={veg ? "Vegetarian" : "Non-vegetarian"}>
      <i />
    </span>
  );
}

export function StatusBadge({ status, label }) {
  return <span className={`badge s-${status}`}>{label}</span>;
}
