import { useState } from "react";
import { useCart } from "../context/CartContext";
import { inrStr } from "../services/format";
import { FoodTypeMark } from "./Ui";

export default function FoodCard({ item }) {
  const cart = useCart();
  const [flash, setFlash] = useState(false);
  const inCart = cart.items.find((i) => i.id === item.id);

  const add = () => {
    cart.add(item);
    setFlash(true);
    setTimeout(() => setFlash(false), 900);
  };

  return (
    <article className={`food ${item.is_available ? "" : "off"}`}>
      <div className="food-img">
        <img src={item.image_url || "/images/main.svg"} alt={item.name} loading="lazy" />
        {!item.is_available && <span className="sold">Not available today</span>}
      </div>
      <div className="food-body">
        <div className="food-title">
          <FoodTypeMark type={item.food_type} />
          <h3>{item.name}</h3>
        </div>
        <p className="muted">{item.description}</p>
        <div className="food-foot">
          <strong className="price">{inrStr(item.price)}</strong>
          {inCart ? (
            <div className="stepper" aria-label={`Quantity of ${item.name}`}>
              <button onClick={() => (inCart.quantity <= 1 ? cart.remove(item.id) : cart.setQty(item.id, inCart.quantity - 1))} aria-label="Decrease">−</button>
              <span>{inCart.quantity}</span>
              <button onClick={() => cart.setQty(item.id, inCart.quantity + 1)} aria-label="Increase">+</button>
            </div>
          ) : (
            <button className="btn small" disabled={!item.is_available} onClick={add}>
              {flash ? "Added" : "Add to cart"}
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
