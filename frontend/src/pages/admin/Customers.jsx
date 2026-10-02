import { ErrorBox, Loading } from "../../components/Ui";
import { useFetch } from "../../hooks/useFetch";
import { api } from "../../services/api";
import { fmtDate } from "../../services/format";

export default function Customers() {
  const { data, error, loading, reload } = useFetch(() => api.admin.customers(), []);
  if (loading) return <Loading />;
  if (error) return <ErrorBox message={error} onRetry={reload} />;
  return (
    <>
      <h1>Customers</h1>
      <div className="scroll">
        <table className="tbl">
          <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Joined</th></tr></thead>
          <tbody>
            {data.length === 0 && <tr><td colSpan={4} className="muted">No customers yet.</td></tr>}
            {data.map((c) => <tr key={c.id}><td>{c.name}</td><td>{c.email}</td><td>{c.phone}</td><td>{fmtDate(c.created_at)}</td></tr>)}
          </tbody>
        </table>
      </div>
    </>
  );
}
