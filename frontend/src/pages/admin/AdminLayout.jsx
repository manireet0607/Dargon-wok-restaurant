import { Link, NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { Loading } from "../../components/Ui";
import { useAuth } from "../../context/AuthContext";

export default function AdminLayout() {
  const { user, loading, isAdmin, logout } = useAuth();
  const nav = useNavigate();
  if (loading) return <div className="wrap section"><Loading /></div>;
  if (!user) return <Navigate to="/admin/login" replace />;
  if (!isAdmin)
    return (
      <div className="wrap section narrow">
        <h1>No access</h1>
        <p>This area is only for Dragon Wok staff.</p>
        <Link className="btn" to="/">Back to the website</Link>
      </div>
    );

  return (
    <div className="admin">
      <aside className="side">
        <div className="logo"><span className="logo-mark" aria-hidden="true">龍</span> Admin</div>
        <nav>
          <NavLink to="/admin" end>Overview</NavLink>
          <NavLink to="/admin/orders">Orders</NavLink>
          <NavLink to="/admin/foods">Food items</NavLink>
          <NavLink to="/admin/categories">Categories</NavLink>
          <NavLink to="/admin/customers">Customers</NavLink>
        </nav>
        <div className="side-foot">
          <Link to="/">View website</Link>
          <button className="linkbtn" onClick={() => { logout(); nav("/admin/login"); }}>Logout</button>
        </div>
      </aside>
      <main className="admin-main"><Outlet /></main>
    </div>
  );
}
