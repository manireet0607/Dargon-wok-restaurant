import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const from = useLocation().state?.from || "/menu";
  const [f, setF] = useState({ name: "", email: "", phone: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(f);
      nav(from, { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <div className="wrap section authbox">
      <form className="card form" onSubmit={submit}>
        <h1>Create your account</h1>
        <label>Full name<input required minLength={2} autoComplete="name" value={f.name} onChange={set("name")} /></label>
        <label>Email<input type="email" required autoComplete="email" value={f.email} onChange={set("email")} /></label>
        <label>Phone number<input type="tel" required autoComplete="tel" value={f.phone} onChange={set("phone")} placeholder="9876543210" /></label>
        <label>Password<input type="password" required minLength={8} maxLength={72} autoComplete="new-password" value={f.password} onChange={set("password")} />
          <span className="hint">At least 8 characters, with a letter and a number.</span></label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="btn full" disabled={busy}>{busy ? "Creating account..." : "Register"}</button>
        <p className="muted center">Already registered? <Link to="/login" state={{ from }}>Log in</Link></p>
      </form>
    </div>
  );
}
