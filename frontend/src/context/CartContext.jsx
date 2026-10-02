import { createContext, useContext, useEffect, useMemo, useReducer, useState } from "react";
import { api } from "../services/api";
import { toPaise } from "../services/format";

const CartContext = createContext(null);
const KEY = "dw_cart";

function reducer(items, a) {
  switch (a.type) {
    case "add": {
      const found = items.find((i) => i.id === a.item.id);
      if (found) return items.map((i) => (i.id === a.item.id ? { ...i, quantity: Math.min(50, i.quantity + 1) } : i));
      const { id, name, price, image_url, food_type } = a.item;
      return [...items, { id, name, price, image_url, food_type, quantity: 1 }];
    }
    case "qty":
      return items.map((i) => (i.id === a.id ? { ...i, quantity: Math.max(1, Math.min(50, a.quantity)) } : i));
    case "remove":
      return items.filter((i) => i.id !== a.id);
    case "clear":
      return [];
    default:
      return items;
  }
}

export function CartProvider({ children }) {
  const [items, dispatch] = useReducer(reducer, [], () => {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || [];
    } catch {
      return [];
    }
  });
  const [config, setConfig] = useState({ delivery_fee: "40.00", tax_rate: "0.05", free_delivery_above: "0.00" });

  useEffect(() => localStorage.setItem(KEY, JSON.stringify(items)), [items]);
  useEffect(() => {
    api.config().then(setConfig).catch(() => {});
  }, []);

  const value = useMemo(() => {
    const subtotal = items.reduce((s, i) => s + toPaise(i.price) * i.quantity, 0);
    const freeAbove = toPaise(config.free_delivery_above);
    const fee = items.length === 0 || (freeAbove > 0 && subtotal >= freeAbove) ? 0 : toPaise(config.delivery_fee);
    const tax = Math.round(subtotal * parseFloat(config.tax_rate));
    return {
      items,
      count: items.reduce((s, i) => s + i.quantity, 0),
      subtotal,
      fee,
      tax,
      total: subtotal + fee + tax, // estimate only: the server calculates the real total
      taxRate: parseFloat(config.tax_rate),
      add: (item) => dispatch({ type: "add", item }),
      setQty: (id, quantity) => dispatch({ type: "qty", id, quantity }),
      remove: (id) => dispatch({ type: "remove", id }),
      clear: () => dispatch({ type: "clear" }),
    };
  }, [items, config]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);
