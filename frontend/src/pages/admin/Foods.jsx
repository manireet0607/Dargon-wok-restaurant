import { useState } from "react";
import { ErrorBox, FoodTypeMark, Loading } from "../../components/Ui";
import { useFetch } from "../../hooks/useFetch";
import { api } from "../../services/api";
import { inrStr } from "../../services/format";

const blank = (categoryId) => ({ category_id: categoryId || "", name: "", description: "", price: "", image_url: "", food_type: "veg", is_available: true });

export default function Foods() {
  const items = useFetch(() => api.admin.menu(), []);
  const cats = useFetch(() => api.admin.categories(), []);
  const [form, setForm] = useState(null); // null = closed, otherwise the item being edited
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  const openNew = () => { setEditId(null); setForm(blank(cats.data?.[0]?.id)); setError(""); };
  const openEdit = (i) => { setEditId(i.id); setForm({ ...i, description: i.description || "", image_url: i.image_url || "" }); setError(""); };

  const save = async (e) => {
    e.preventDefault();
    setError("");
    const body = {
      category_id: Number(form.category_id), name: form.name, description: form.description || null,
      price: String(form.price), image_url: form.image_url || null, food_type: form.food_type, is_available: form.is_available,
    };
    try {
      editId ? await api.admin.updateItem(editId, body) : await api.admin.createItem(body);
      setForm(null);
      items.reload();
    } catch (err) { setError(err.message); }
  };
  const remove = async (i) => {
    if (!window.confirm(`Delete "${i.name}"?`)) return;
    setMsg("");
    try { await api.admin.deleteItem(i.id); items.reload(); } catch (e) { setMsg(e.message); }
  };
  const toggle = async (i) => {
    setMsg("");
    try { await api.admin.setAvailability(i.id, !i.is_available); items.reload(); } catch (e) { setMsg(e.message); }
  };

  return (
    <>
      <div className="between"><h1>Food items</h1><button className="btn" onClick={openNew} disabled={!cats.data?.length}>Add food item</button></div>
      {msg && <p className="error" role="alert">{msg}</p>}
      {items.loading && !items.data ? <Loading /> : items.error ? <ErrorBox message={items.error} onRetry={items.reload} /> : (
        <div className="scroll">
          <table className="tbl">
            <thead><tr><th>Name</th><th>Category</th><th className="r">Price</th><th>Available</th><th></th></tr></thead>
            <tbody>
              {items.data.map((i) => (
                <tr key={i.id}>
                  <td><span className="food-title"><FoodTypeMark type={i.food_type} />{i.name}</span></td>
                  <td>{i.category_name}</td><td className="r">{inrStr(i.price)}</td>
                  <td><label className="switch"><input type="checkbox" checked={i.is_available} onChange={() => toggle(i)} aria-label={`${i.name} available`} /><span /></label></td>
                  <td className="actions"><button className="linkbtn" onClick={() => openEdit(i)}>Edit</button><button className="linkbtn danger" onClick={() => remove(i)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {form && (
        <div className="modal" role="dialog" aria-modal="true" aria-label={editId ? "Edit food item" : "Add food item"}>
          <form className="modal-box form" onSubmit={save}>
            <h2>{editId ? "Edit food item" : "Add food item"}</h2>
            <label>Name<input required minLength={2} value={form.name} onChange={set("name")} /></label>
            <label>Category
              <select required value={form.category_id} onChange={set("category_id")}>
                <option value="" disabled>Choose a category</option>
                {cats.data.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </label>
            <label>Description<textarea rows={2} value={form.description} onChange={set("description")} /></label>
            <div className="row">
              <label className="grow">Price (₹)<input required type="number" min="1" step="0.01" value={form.price} onChange={set("price")} /></label>
              <label className="grow">Type
                <select value={form.food_type} onChange={set("food_type")}><option value="veg">Vegetarian</option><option value="non_veg">Non-vegetarian</option></select>
              </label>
            </div>
            <label>Image URL<input value={form.image_url} onChange={set("image_url")} placeholder="/images/noodles.svg or https://..." /></label>
            <label className="radio"><input type="checkbox" checked={form.is_available} onChange={set("is_available")} /> Available to order</label>
            {error && <p className="error" role="alert">{error}</p>}
            <div className="row"><button className="btn">Save</button><button type="button" className="btn ghost" onClick={() => setForm(null)}>Cancel</button></div>
          </form>
        </div>
      )}
    </>
  );
}
