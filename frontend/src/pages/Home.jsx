import { Link } from "react-router-dom";
import FoodCard from "../components/FoodCard";
import { ErrorBox, Loading } from "../components/Ui";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

export default function Home() {
  const menu = useFetch(() => api.menu(), []);
  const cats = useFetch(() => api.categories(), []);
  const popular = (menu.data || []).filter((m) => m.is_available).slice(0, 6);

  return (
    <>
      <section className="hero">
        <div className="wrap hero-in">
          <p className="hero-zh" aria-hidden="true">龍 鍋</p>
          <h1>Hot from the wok,<br />straight to your door.</h1>
          <p className="hero-sub">Noodles, fried rice, momos and gravies cooked to order over a roaring flame.</p>
          <div className="row">
            <Link to="/menu" className="btn big">Order now</Link>
            <Link to="/about" className="btn ghost light big">Our story</Link>
          </div>
        </div>
      </section>

      <section className="wrap section">
        <h2>Pick a craving</h2>
        {cats.loading ? <Loading /> : cats.error ? <ErrorBox message={cats.error} onRetry={cats.reload} /> : (
          <div className="chips">
            {cats.data.map((c) => (
              <Link key={c.id} className="chip" to={`/menu?category=${c.id}`}>{c.name}</Link>
            ))}
          </div>
        )}
      </section>

      <section className="wrap section">
        <div className="between"><h2>From today's menu</h2><Link to="/menu" className="textlink">See the full menu</Link></div>
        {menu.loading ? <Loading /> : menu.error ? <ErrorBox message={menu.error} onRetry={menu.reload} /> : (
          <div className="grid">{popular.map((m) => <FoodCard key={m.id} item={m} />)}</div>
        )}
      </section>

      <section className="band">
        <div className="wrap band-in">
          <div><h3>Cash on delivery</h3><p>Pay when your food arrives. No online payment needed.</p></div>
          <div><h3>Cooked to order</h3><p>Every dish is made after you order, never reheated.</p></div>
          <div><h3>Track your order</h3><p>Log in to see each step, from confirmed to delivered.</p></div>
        </div>
      </section>
    </>
  );
}
