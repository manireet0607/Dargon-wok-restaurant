import { Link, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { useEffect } from "react";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import About from "./pages/About";
import Account from "./pages/Account";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import Contact from "./pages/Contact";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Menu from "./pages/Menu";
import OrderConfirmation from "./pages/OrderConfirmation";
import Register from "./pages/Register";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminLogin from "./pages/admin/AdminLogin";
import Categories from "./pages/admin/Categories";
import Customers from "./pages/admin/Customers";
import Foods from "./pages/admin/Foods";
import Orders from "./pages/admin/Orders";
import Overview from "./pages/admin/Overview";

function SiteLayout() {
  const { pathname } = useLocation();
  useEffect(() => window.scrollTo(0, 0), [pathname]);
  return (
    <>
      <Navbar />
      <main><Outlet /></main>
      <Footer />
    </>
  );
}

const NotFound = () => (
  <div className="wrap section narrow"><h1>Page not found</h1><p>The page you are looking for does not exist.</p><Link className="btn" to="/">Go home</Link></div>
);

export default function App() {
  return (
    <Routes>
      <Route element={<SiteLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/menu" element={<Menu />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
        <Route path="/order-confirmation/:id" element={<ProtectedRoute><OrderConfirmation /></ProtectedRoute>} />
        <Route path="/account" element={<ProtectedRoute><Account /></ProtectedRoute>} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="*" element={<NotFound />} />
      </Route>
      {/* Admin dashboard has its own layout (no customer navbar) */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Overview />} />
        <Route path="orders" element={<Orders />} />
        <Route path="foods" element={<Foods />} />
        <Route path="categories" element={<Categories />} />
        <Route path="customers" element={<Customers />} />
      </Route>
    </Routes>
  );
}
