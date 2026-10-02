import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const { count } = useCart();
  const [open, setOpen] = useState(false);
  const nav = useNavigate();
  const close = () => setOpen(false);

  return (
    <header className="nav">
      <div className="wrap nav-in">
        <Link to="/" className="logo" onClick={close}>
          <span className="logo-mark" aria-hidden="true">龍</span> Dragon Wok
        </Link>
        <button className="burger" aria-label="Menu" aria-expanded={open} onClick={() => setOpen(!open)}>
          <span /><span /><span />
        </button>
        <nav className={`links ${open ? "open" : ""}`} onClick={close}>
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/menu">Menu</NavLink>
          <NavLink to="/about">About Us</NavLink>
          <NavLink to="/contact">Contact</NavLink>
          <NavLink to="/cart" className="cart-link">Cart{count > 0 && <b className="count">{count}</b>}</NavLink>
          {user ? (
            <>
              <NavLink to="/account">{user.name.split(" ")[0]}</NavLink>
              {isAdmin && <NavLink to="/admin">Admin</NavLink>}
              <button className="linkbtn" onClick={() => { logout(); nav("/"); }}>Logout</button>
            </>
          ) : (
            <>
              <NavLink to="/login">Login</NavLink>
              <NavLink to="/register" className="btn small">Register</NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
