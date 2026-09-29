import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';
import './style.css';
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const api = axios.create({ baseURL: API });
api.interceptors.request.use(c => { const t = localStorage.getItem('access'); if (t) c.headers.Authorization = `Bearer ${t}`; return c });
function App() {
    const [token, setToken] = useState(localStorage.getItem('access')); const [user, setUser] = useState(null); const [cards, setCards] = useState([]); const [tx, setTx] = useState([]); const [tab, setTab] = useState('dashboard'); const [msg, setMsg] = useState('');
    const load = async () => { try { const [u, c, t] = await Promise.all([api.get('/auth/me/'), api.get('/cards/'), api.get('/transactions/')]); setUser(u.data); setCards(c.data); setTx(t.data) } catch { logout() } };
    useEffect(() => { if (token) load() }, [token]);
    const logout = () => { localStorage.clear(); setToken(null); setUser(null) };
    if (!token) return <Auth onLogin={t => { localStorage.setItem('access', t); setToken(t) }} />;
    return <div className="app"><aside><h1>PaySecure</h1><p className="muted">Credit Card Payment System</p>{['dashboard', 'cards', 'payment', 'transactions'].map(x => <button className={tab === x ? 'nav active' : 'nav'} onClick={() => setTab(x)} key={x}>{x[0].toUpperCase() + x.slice(1)}</button>)}{user?.is_staff && <button className="nav" onClick={() => setTab('admin')}>Admin</button>}<button className="nav logout" onClick={logout}>Logout</button></aside><main><header><div><h2>{tab === 'dashboard' ? 'Dashboard' : tab === 'admin' ? 'Admin Dashboard' : tab[0].toUpperCase() + tab.slice(1)}</h2><span className="muted">Welcome, {user?.username}</span></div></header>{msg && <div className="notice">{msg}</div>}{tab === 'dashboard' && <Dashboard cards={cards} tx={tx} />} {tab === 'cards' && <Cards cards={cards} refresh={load} setMsg={setMsg} />} {tab === 'payment' && <Payment cards={cards} refresh={load} setMsg={setMsg} />} {tab === 'transactions' && <Transactions tx={tx} />} {tab === 'admin' && <Admin />}</main></div>
}
function Auth({ onLogin }) { const [mode, setMode] = useState('login'); const [form, setForm] = useState({ username: '', email: '', password: '' }); const [err, setErr] = useState(''); const submit = async e => { e.preventDefault(); setErr(''); try { if (mode === 'register') { await axios.post(API + '/auth/register/', form); setMode('login') } const r = await axios.post(API + '/auth/token/', { username: form.username, password: form.password }); onLogin(r.data.access) } catch (e) { setErr(e.response?.data?.detail || JSON.stringify(e.response?.data) || 'Request failed') } }; return <div className="auth"><form className="card authbox" onSubmit={submit}><h1>PaySecure</h1><p className="muted">{mode === 'login' ? 'Sign in to your account' : 'Create your account'}</p>{mode === 'register' && <input placeholder="Email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />}<input placeholder="Username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} required /><input placeholder="Password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />{err && <div className="error">{err}</div>}<button className="primary">{mode === 'login' ? 'Login' : 'Register'}</button><button type="button" className="link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>{mode === 'login' ? 'Create account' : 'Back to login'}</button></form></div> }
function Dashboard({ cards, tx }) { const success = tx.filter(t => t.status === 'SUCCESS').reduce((a, b) => a + Number(b.amount), 0); return <><div className="grid"><Stat title="Saved Cards" value={cards.length} /><Stat title="Transactions" value={tx.length} /><Stat title="Successful Payments" value={`₹${success.toFixed(2)}`} /></div><section className="card"><h3>Recent Transactions</h3><Table tx={tx.slice(-100).reverse()} /></section></> }
function Stat({ title, value }) { return <div className="card stat"><span className="muted">{title}</span><strong>{value}</strong></div> }
function Cards({ cards, refresh, setMsg }) { const [f, setF] = useState({ cardholder_name: '', card_number: '', brand: 'VISA' }); const add = async e => { e.preventDefault(); try { await api.post('/cards/', f); setF({ cardholder_name: '', card_number: '', brand: 'VISA' }); setMsg('Card saved securely (only masked number and last 4 digits are stored).'); refresh() } catch (e) { setMsg(JSON.stringify(e.response?.data)) } }; const del = async id => { try { await api.delete('/cards/' + id + '/'); refresh() } catch (e) { setMsg(e.response?.data?.detail || 'Unable to delete card') } }; return <div className="split"><form className="card" onSubmit={add}><h3>Add Card</h3><input placeholder="Cardholder name" value={f.cardholder_name} onChange={e => setF({ ...f, cardholder_name: e.target.value })} required /><input placeholder="Card number" value={f.card_number} onChange={e => setF({ ...f, card_number: e.target.value })} required /><select value={f.brand} onChange={e => setF({ ...f, brand: e.target.value })}><option>VISA</option><option>MASTERCARD</option><option>RUPAY</option></select><button className="primary">Save Card</button></form><section className="card"><h3>Saved Cards</h3>{cards.length ? <div className="cards">{cards.map(c => <div className="carditem" key={c.id}><b>{c.brand}</b><span>{c.masked_number}</span><small>{c.cardholder_name}</small><button onClick={() => del(c.id)}>Delete</button></div>)}</div> : <p className="muted">No cards saved.</p>}</section></div> }
function Payment({ cards, refresh, setMsg }) { const [f, setF] = useState({ card_id: '', amount: '' }); const pay = async e => { e.preventDefault(); try { const r = await api.post('/payments/', { card_id: Number(f.card_id), amount: f.amount }); setMsg(`Payment ${r.data.status}: ${r.data.reference}`); setF({ card_id: '', amount: '' }); refresh() } catch (e) { setMsg(JSON.stringify(e.response?.data)) } }; return <form className="card narrow" onSubmit={pay}><h3>Make Payment</h3><select value={f.card_id} onChange={e => setF({ ...f, card_id: e.target.value })} required><option value="">Select card</option>{cards.map(c => <option key={c.id} value={c.id}>{c.brand} •••• {c.last4}</option>)}</select><input type="number" step="0.01" min="0.01" placeholder="Amount (INR)" value={f.amount} onChange={e => setF({ ...f, amount: e.target.value })} required /><button className="primary">Pay Now</button><p className="muted">Payment is simulated by the FastAPI service.</p></form> }
function Transactions({ tx }) { return <section className="card"><h3>Transaction History</h3><Table tx={tx} /></section> }
function Table({ tx }) { return <div className="tablewrap"><table><thead><tr><th>Reference</th><th>Amount</th><th>Status</th><th>Card</th><th>Date</th></tr></thead><tbody>{tx.map(t => <tr key={t.id}><td>{t.reference}</td><td>₹{Number(t.amount).toFixed(2)}</td><td><span className={'badge ' + t.status.toLowerCase()}>{t.status}</span></td><td>•••• {t.card.last4}</td><td>{new Date(t.created_at).toLocaleString()}</td></tr>)}</tbody></table></div> }

function Admin() {
    const [s, setS] = useState(null);
    const [users, setUsers] = useState([]);
    const [msg, setMsg] = useState("");
    const [selectedUser, setSelectedUser] = useState(null);
    const [userTransactions, setUserTransactions] = useState([]);

    useEffect(() => {
        api.get("/admin/summary/").then(r => setS(r.data));
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            const r = await api.get("/admin/users/");
            setUsers(r.data);
        } catch (e) {
            setMsg("Failed to load users");
        }
    };
    const loadUserTransactions = async (userId) => {
        setSelectedUser(userId);
  try {
    const r = await api.get(`/admin/users/${userId}/transactions/`);
    setUserTransactions(Array.isArray(r.data) ? r.data :(r.data.transactions || []));
  } catch (e) {
    setMsg("Failed to load user transactions");
  }
};

    const toggleUser = async (userId) => {
        try {
            await api.patch(`/admin/users/${userId}/toggle/`);
            loadUsers();
        } catch (e) {
            setMsg("Failed to update user");
        }
    };
    
    


    const download = async () => {
        const r = await api.get("/admin/export/", {
            responseType: "blob"
        });

        const u = URL.createObjectURL(r.data);
        const a = document.createElement("a");
        a.href = u;
        a.download = "transactions.csv";
        a.click();
        URL.revokeObjectURL(u);
    };

    if (!s) {
        return <p>Loading admin dashboard...</p>;
    }

    return (
        <div>
            <h2>Admin Dashboard</h2>

            <div className="grid">
                <Stat title="Users" value={s.users} />
                <Stat title="Cards" value={s.cards} />
                <Stat title="Success Count" value={s.success_count} />
                <Stat
                    title="Successful Amount"
                    value={`₹${Number(s.successful_amount).toFixed(2)}`}
                />
            </div>

            <button
                className="primary"
                onClick={download}
            >
                Export CSV
            </button>

            <section className="card">
                <h3>Manage Users</h3>

                {msg && <p className="muted">{msg}</p>}

                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Staff</th>
                            <th>Status</th>
                            <th>Joined</th>
                            <th>Action</th>
                            <th>Transactions</th>
                        </tr>
                    </thead>

                    <tbody>
                        {users.map(user => (
                            <tr key={user.id}>
                                <td>{user.id}</td>
                                <td>{user.username}</td>
                                <td>{user.email}</td>
                                <td>{user.is_staff ? "Yes" : "No"}</td>

                                <td>
                                    {user.is_active ? "Active" : "Disabled"}
                                </td>

                                <td>
                                    {new Date(user.date_joined).toLocaleDateString()}
                                </td>

                                <td>
                                    <button onClick={() => toggleUser(user.id)}>
                                        {user.is_active ? "Disable" : "Enable"}
                                    </button>

                                    <button onClick={() => loadUserTransactions(user.id)}>
                                       View Transactions
                                    </button>
                                    
                                </td> 
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>
            {selectedUser && (
  <section className="card">
    <h3>
      Transactions for {selectedUser.username}
    </h3>

    {userTransactions.length === 0 ? (
      <p className="muted">No transactions found.</p>
    ) : (
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Reference</th>
            <th>Created</th>
          </tr>
        </thead>

        <tbody>
          {(Array.isArray(userTransactions) ? userTransactions : []).map(tx => (
            <tr key={tx.id}>
              <td>{tx.id}</td>
              <td>${Number(tx.amount).toFixed(2)}</td>
              <td>{tx.status}</td>
              <td>{tx.reference}</td>
              <td>
                {new Date(tx.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </section>)}
            
{selectedUser && (
  <section className="card">
    <h3>User Transactions</h3>

    {userTransactions.length === 0 ? (
      <p>No transactions found for this user.</p>
    ) : (
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Reference</th>
            <th>Amount</th>
            <th>Currency</th>
            <th>Status</th>
            <th>Failure Reason</th>
            <th>Created</th>
          </tr>
        </thead>

        <tbody>
          {(Array.isArray(userTransactions) ? userTransactions : []).map((tx) => (
            <tr key={tx.id}>
              <td>{tx.id}</td>
              <td>{tx.reference}</td>
              <td>{tx.amount}</td>
              <td>{tx.currency}</td>
              <td>{tx.status}</td>
              <td>{tx.failure_reason || "-"}</td>
              <td>
                {new Date(tx.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </section>
)}

        </div>
    );
}
createRoot(document.getElementById('root')).render(<App />);