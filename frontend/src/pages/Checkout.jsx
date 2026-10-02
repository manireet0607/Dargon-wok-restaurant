import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { api } from "../services/api";
import { Summary } from "./Cart";

export default function Checkout() {
  const { user } = useAuth();
  const cart = useCart();
  const nav = useNavigate();
  const [form, setForm] = useState({ name: user?.name || "", phone: user?.phone || "", address: "", notes: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  if (cart.items.length === 0) return <Navigate to="/cart" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      // Only item ids and quantities are sent. The server looks up prices and calculates the total.
      const order = await api.createOrder({
        items: cart.items.map((i) => ({ menu_item_id: i.id, quantity: i.quantity })),
        customer_name: form.name,
        customer_phone: form.phone,
        delivery_address: form.address,
        special_instructions: form.notes || null,
        payment_method: "cod",
      });
      cart.clear();
      nav(`/order-confirmation/${order.id}`, { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <div className="wrap section">
      <h1>Checkout</h1>
      <div className="two">
        <form className="card form" onSubmit={submit}>
          <h2>Delivery details</h2>
          <label>Full name<input required minLength={2} value={form.name} onChange={set("name")} autoComplete="name" /></label>
          <label>Phone number<input required type="tel" value={form.phone} onChange={set("phone")} autoComplete="tel" placeholder="9876543210" /></label>
          <label>Delivery address<textarea required minLength={10} rows={3} value={form.address} onChange={set("address")} placeholder="House number, street, area, landmark, pincode" /></label>
          <label>Special instructions (optional)<textarea rows={2} maxLength={500} value={form.notes} onChange={set("notes")} placeholder="For example: less spicy, no onion" /></label>
          <fieldset>
            <legend>Payment</legend>
            <label className="radio"><input type="radio" checked readOnly /> Cash on delivery</label>
            <p className="muted">Pay in cash when your order arrives. Online payment is coming later.</p>
          </fieldset>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="btn big full" disabled={busy}>{busy ? "Placing order..." : "Place order"}</button>
        </form>
        <aside className="card">
          <h2>Your order</h2>
          <ul className="mini">
            {cart.items.map((i) => <li key={i.id}><span>{i.quantity} × {i.name}</span></li>)}
          </ul>
          <Summary cart={cart} />
          <p className="muted small-text">The final amount is confirmed by our server when you place the order.</p>
        </aside>
      </div>
    </div>
  );
}
