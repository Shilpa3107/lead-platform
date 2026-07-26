import { useState } from 'react';
import api from '../api';

export default function PublicCapture() {
  const [form, setForm] = useState({ name: '', email: '', phone: '', company: '', source: '' });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      await api.post('/public/leads', form);
      setSubmitted(true);
    } catch (err) {
      setError('Something went wrong — please try again.');
    }
  }

  if (submitted) {
    return (
      <div className="auth-form">
        <h1>Thanks!</h1>
        <p>We've received your details and someone will be in touch shortly.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="auth-form public-capture-form">
      <h1>Get in touch</h1>
      {error && <p className="error-text">{error}</p>}
      <input placeholder="Name *" value={form.name} onChange={(e) => update('name', e.target.value)} required />
      <input type="email" placeholder="Email" value={form.email} onChange={(e) => update('email', e.target.value)} />
      <input placeholder="Phone" value={form.phone} onChange={(e) => update('phone', e.target.value)} />
      <input placeholder="Company" value={form.company} onChange={(e) => update('company', e.target.value)} />
      <input placeholder="How did you hear about us?" value={form.source} onChange={(e) => update('source', e.target.value)} />
      <button type="submit">Submit</button>
    </form>
  );
}