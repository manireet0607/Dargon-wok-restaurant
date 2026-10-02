import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="wrap foot-in">
        <div>
          <div className="logo"><span className="logo-mark" aria-hidden="true">龍</span> Dragon Wok</div>
          <p className="muted">Chinese food, cooked to order and delivered hot.</p>
        </div>
        <div>
          <h4>Visit</h4>
          <p className="muted">Open every day, 11:00 am to 11:00 pm</p>
        </div>
        <div>
          <h4>Quick links</h4>
          <p><Link to="/menu">Menu</Link></p>
          <p><Link to="/contact">Contact</Link></p>
          <p><Link to="/admin/login">Staff login</Link></p>
        </div>
      </div>
      <div className="wrap copy">© {new Date().getFullYear()} Dragon Wok. All prices are in Indian Rupees (₹).</div>
    </footer>
  );
}
