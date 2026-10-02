export default function Contact() {
  return (
    <div className="wrap section narrow">
      <h1>Contact us</h1>
      <p className="lead">Questions about an order? Call us and keep your order number ready.</p>
      <dl className="info">
        <dt>Phone</dt><dd><a href="tel:+911100000000">+91 11 0000 0000</a></dd>
        <dt>Email</dt><dd><a href="mailto:hello@dragonwok.example">hello@dragonwok.example</a></dd>
        <dt>Opening hours</dt><dd>Every day, 11:00 am to 11:00 pm</dd>
        <dt>Address</dt><dd>Dragon Wok Kitchen, Sector 12, Dwarka, New Delhi</dd>
      </dl>
      <p className="muted">Replace these sample details with your restaurant's real contact information in <code>src/pages/Contact.jsx</code>.</p>
    </div>
  );
}
