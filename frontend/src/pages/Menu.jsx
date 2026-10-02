import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import FoodCard from "../components/FoodCard";
import { Empty, ErrorBox, Loading } from "../components/Ui";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

export default function Menu() {
  const [params, setParams] = useSearchParams();
  const category = params.get("category") || "";
  const [type, setType] = useState("");
  const [search, setSearch] = useState("");

  const cats = useFetch(() => api.categories(), []);
  const menu = useFetch(() => api.menu({ category_id: category, food_type: type, search }), [category, type, search]);

  const groups = useMemo(() => {
    const byCat = new Map();
    (menu.data || []).forEach((m) => byCat.set(m.category_name, [...(byCat.get(m.category_name) || []), m]));
    return [...byCat.entries()];
  }, [menu.data]);

  return (
    <div className="wrap section">
      <h1>Our menu</h1>
      <div className="filters">
        <div className="chips" role="tablist" aria-label="Categories">
          <button className={`chip ${!category ? "on" : ""}`} onClick={() => setParams({})}>All</button>
          {(cats.data || []).map((c) => (
            <button key={c.id} className={`chip ${category === String(c.id) ? "on" : ""}`} onClick={() => setParams({ category: c.id })}>{c.name}</button>
          ))}
        </div>
        <div className="row wrapx">
          <select value={type} onChange={(e) => setType(e.target.value)} aria-label="Food type">
            <option value="">Veg and non-veg</option>
            <option value="veg">Vegetarian only</option>
            <option value="non_veg">Non-vegetarian only</option>
          </select>
          <input type="search" placeholder="Search dishes" value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Search dishes" />
        </div>
      </div>

      {menu.loading && !menu.data ? <Loading /> : menu.error ? <ErrorBox message={menu.error} onRetry={menu.reload} /> :
        groups.length === 0 ? <Empty text="No dishes match your search." /> :
        groups.map(([name, items]) => (
          <section key={name} className="menu-group">
            <h2>{name}</h2>
            <div className="grid">{items.map((m) => <FoodCard key={m.id} item={m} />)}</div>
          </section>
        ))}
    </div>
  );
}
