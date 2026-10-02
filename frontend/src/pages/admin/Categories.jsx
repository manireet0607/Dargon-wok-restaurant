import { useState } from "react";
import { ErrorBox, Loading } from "../../components/Ui";
import { useFetch } from "../../hooks/useFetch";
import { api } from "../../services/api";

export default function Categories() {
  const { data, error, loading, reload } = useFetch(() => api.admin.categories(), []);
  const [form, setForm] = useState({ name: "", description: "" });
  const [editId, setEditId] = useState(null);
  const [msg, setMsg] = useState("");

  const save = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      const body = { name: form.name, description: form.description || null };
      editId ? await api.admin.updateCategory(editId, body) : await api.admin.createCategory(body);
      setForm({ name: "", description: "" });
      setEditId(null);
      reload();
    } catch (err) { setMsg(err.message); }
  };
  const remove = async (c) => {
    if (!window.confirm(`Delete category "${c.name}"?`)) return;
    setMsg("");
    try { await api.admin.deleteCategory(c.id); reload(); } catch (err) { setMsg(err.message); }
  };

  return (
    <>
      <h1>Categories</h1>
      <form className="card form inline-form" onSubmit={save}>
        <label>Name<input required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
        <label className="grow">Description<input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
        <button className="btn">{editId ? "Save changes" : "Add category"}</button>
        {editId && <button type="button" className="btn ghost" onClick={() => { setEditId(null); setForm({ name: "", description: "" }); }}>Cancel</button>}
      </form>
      {msg && <p className="error" role="alert">{msg}</p>}
      {loading && !data ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <table className="tbl">
          <thead><tr><th>Name</th><th>Description</th><th></th></tr></thead>
          <tbody>
            {data.map((c) => (
              <tr key={c.id}><td>{c.name}</td><td className="muted">{c.description}</td>
                <td className="actions"><button className="linkbtn" onClick={() => { setEditId(c.id); setForm({ name: c.name, description: c.description || "" }); }}>Edit</button><button className="linkbtn danger" onClick={() => remove(c)}>Delete</button></td></tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
