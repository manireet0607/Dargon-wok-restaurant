import { Link, useNavigate } from "react-router-dom";
import { FoodTypeMark, Empty } from "../components/Ui";
import { useCart } from "../context/CartContext";
import { inr, inrStr, toPaise } from "../services/format";

export function Summary({ cart }) {
  return (
    <dl className="sum">
      <dt>Subtotal</dt><dd>{inr(cart.subtotal)}</dd>
      <dt>Delivery fee</dt><dd>{cart.fee === 0 ? "Free" : inr(cart.fee)}</dd>
      <dt>Taxes ({(cart.taxRate * 100).toFixed(0)}%)</dt><dd>{inr(cart.tax)}</dd>
      <dt className="total">Total</dt><dd className="total">{inr(cart.total)}</dd>
    </dl>
  );
}

export default function Cart() {
  const cart = useCart();
  const nav = useNavigate();
  if (cart.items.length === 0) return <div className="wrap section"><h1>Your cart</h1><Empty text="Your cart is empty." to="/menu" action="Browse the menu" /></div>;

  return (
    <div className="wrap section">
      <h1>Your cart</h1>
      <div className="two">
        <ul className="lines">
          {cart.items.map((i) => (
            <li key={i.id} className="line">
              <img src={i.image_url || "/images/main.svg"} alt="" />
              <div className="grow">
                <div className="food-title"><FoodTypeMark type={i.food_type} /><strong>{i.name}</strong></div>
                <span className="muted">{inrStr(i.price)} each</span>
              </div>
              <div className="stepper">
                <button onClick={() => (i.quantity <= 1 ? cart.remove(i.id) : cart.setQty(i.id, i.quantity - 1))} aria-label={`Decrease ${i.name}`}>−</button>
                <span>{i.quantity}</span>
                <button onClick={() => cart.setQty(i.id, i.quantity + 1)} aria-label={`Increase ${i.name}`}>+</button>
              </div>
              <strong className="line-total">{inr(toPaise(i.price) * i.quantity)}</strong>
              <button className="linkbtn danger" onClick={() => cart.remove(i.id)}>Remove</button>
            </li>
          ))}
        </ul>
        <aside className="card">
          <h2>Order summary</h2>
          <Summary cart={cart} />
          <button className="btn big full" onClick={() => nav("/checkout")}>Go to checkout</button>
          <Link to="/menu" className="textlink center">Add more dishes</Link>
        </aside>
      </div>
    </div>
  );
}
