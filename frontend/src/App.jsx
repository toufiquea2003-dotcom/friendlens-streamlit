import React, {useState, useEffect} from 'react';
import axios from 'axios';

const API = import.meta.env.VITE_API_BASE || '/api';

export default function App(){
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [summary, setSummary] = useState(null);
  const [recs, setRecs] = useState([]);
  const [hobbyRecs, setHobbyRecs] = useState([]);
  const [loading, setLoading] = useState(false);

  // Check if user is already logged in (from localStorage or URL params)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlUser = urlParams.get('user');
    const urlPass = urlParams.get('pass');

    if (urlUser && urlPass) {
      setUsername(urlUser);
      setPassword(urlPass);
      localStorage.setItem('friendlens_user', urlUser);
      localStorage.setItem('friendlens_pass', urlPass);
      setIsLoggedIn(true);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      const savedUser = localStorage.getItem('friendlens_user');
      const savedPass = localStorage.getItem('friendlens_pass');
      if (savedUser && savedPass) {
        setUsername(savedUser);
        setPassword(savedPass);
        setIsLoggedIn(true);
      }
    }
  }, []);

  const login = async () => {
    if (!username || !password) return alert('Please enter username and password');
    setLoading(true);
    try {
      // Test login with a simple request
      const res = await axios.get(`${API}/health`, {
        auth: { username, password }
      });
      localStorage.setItem('friendlens_user', username);
      localStorage.setItem('friendlens_pass', password);
      setIsLoggedIn(true);
      setLoading(false);
    } catch (e) {
      console.error(e);
      alert('Login failed: Invalid credentials');
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('friendlens_user');
    localStorage.removeItem('friendlens_pass');
    setIsLoggedIn(false);
    setUsername('');
    setPassword('');
    setPreview([]);
    setSummary(null);
    setRecs([]);
    setHobbyRecs([]);
  };

  const getAuthConfig = () => ({
    auth: { username, password }
  });

  const upload = async ()=>{
    if(!file) return alert('Select a CSV file first');
    setLoading(true);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await axios.post(`${API}/upload`, fd, {
        headers: {'Content-Type':'multipart/form-data'},
        ...getAuthConfig()
      });
      alert(`Uploaded ${res.data.filename} (${res.data.rows} rows)`);
      fetchPreview();
      fetchSummary();
    } catch (e) {
      console.error(e);
      alert('Upload failed');
    }
    setLoading(false);
  };

  const fetchPreview = async ()=>{
    setLoading(true);
    try{
      const res = await axios.get(`${API}/preview?n=20`, getAuthConfig());
      setPreview(res.data.head || []);
    }catch(e){ console.error(e); alert('Preview failed'); }
    setLoading(false);
  };

  const fetchSummary = async ()=>{
    setLoading(true);
    try{
      const res = await axios.get(`${API}/summary`, getAuthConfig());
      setSummary(res.data);
    }catch(e){ console.error(e); alert('Summary failed'); }
    setLoading(false);
  };

  const getRecs = async ()=>{
    const uid = prompt('Enter user id (exact string from dataset):');
    if(!uid) return;
    setLoading(true);
    try{
      const res = await axios.get(`${API}/recommend/${encodeURIComponent(uid)}`, getAuthConfig());
      setRecs(res.data.recommendations || []);
    }catch(e){ console.error(e); alert('Recommendation failed'); }
    setLoading(false);
  };

  const getHobbyRecs = async ()=>{
    const uid = prompt('Enter user id (exact number from dataset):');
    if(!uid) return;
    setLoading(true);
    try{
      const res = await axios.get(`${API}/recommend_hobbies/${encodeURIComponent(uid)}`, getAuthConfig());
      setHobbyRecs(res.data.hobby_club_recommendations || []);
    }catch(e){ console.error(e); alert('Hobby recommendation failed'); }
    setLoading(false);
  };

  const getViz = async ()=>{
    setLoading(true);
    try{
      const res = await axios.get(`${API}/visualize`, getAuthConfig());
      alert('Visualization created on backend: ' + JSON.stringify(res.data));
    }catch(e){ console.error(e); alert('Visualization failed'); }
    setLoading(false);
  };

  const analyzeTask = async ()=>{
    const task = prompt('Describe what you want to analyze (e.g., "give me a summary", "recommend friends for Alice", "create a visualization"):');
    if(!task) return;
    setLoading(true);
    try{
      const fd = new FormData();
      fd.append('task', task);
      const res = await axios.post(`${API}/analyze`, fd, getAuthConfig());
      alert('Analysis Result: ' + JSON.stringify(res.data, null, 2));
    }catch(e){ console.error(e); alert('Analysis failed'); }
    setLoading(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h1 className="app-title">FriendLens</h1>
          <p className="app-subtitle">Discover Your Friendship Network</p>
          <div className="login-form">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="login-input"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="login-input"
            />
            <button onClick={login} disabled={loading} className="login-btn">
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </div>
          <div className="login-footer">
            <p>Demo Credentials: FriendLens1 / 12345678</p>
            <p>Shareable Link: <a href={`http://localhost:5173/?user=FriendLens1&pass=12345678`} target="_blank" rel="noopener noreferrer">http://localhost:5173/?user=FriendLens1&pass=12345678</a></p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">FriendLens</h1>
        <div className="user-info">
          <span>Welcome, {username}!</span>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </header>

      <main className="main-content">
        <div className="upload-section">
          <input type="file" accept=".csv" onChange={e=>setFile(e.target.files[0])} className="file-input"/>
          <button onClick={upload} disabled={loading} className="action-btn upload-btn">
            {loading ? 'Uploading...' : 'Upload CSV'}
          </button>
          <button onClick={fetchPreview} disabled={loading} className="action-btn">
            {loading ? 'Loading...' : 'Refresh Preview'}
          </button>
          <button onClick={fetchSummary} disabled={loading} className="action-btn">
            {loading ? 'Loading...' : 'Get Summary'}
          </button>
          <button onClick={getRecs} disabled={loading} className="action-btn">
            {loading ? 'Loading...' : 'Get Recommendations'}
          </button>
          <button onClick={getHobbyRecs} disabled={loading} className="action-btn">
            {loading ? 'Loading...' : 'Get Hobby Recommendations'}
          </button>
          <button onClick={getViz} disabled={loading} className="action-btn">
            {loading ? 'Loading...' : 'Create Visualization'}
          </button>
          <button onClick={analyzeTask} disabled={loading} className="action-btn">
            {loading ? 'Loading...' : 'AI Analyze'}
          </button>
        </div>

        <div className="data-section">
          <div className="summary-card">
            <h3>Summary</h3>
            <pre className="summary-content">{summary?JSON.stringify(summary,null,2):'No summary yet'}</pre>
          </div>

          <div className="preview-card">
            <h3>Preview (first rows)</h3>
            {preview.length===0? <div className="no-data">No preview</div> :
              <div className="table-container">
                <table className="data-table">
                  <thead><tr>{Object.keys(preview[0]).map(c=> <th key={c}>{c}</th>)}</tr></thead>
                  <tbody>
                    {preview.map((r,i)=>(<tr key={i}>{Object.keys(r).map(k=> <td key={k+i}>{String(r[k])}</td>)}</tr>))}
                  </tbody>
                </table>
              </div>
            }
          </div>

          <div className="recommendations-card">
            <h3>Recommendations</h3>
            <ol className="recs-list">{recs.map((r,i)=>(<li key={i} className="rec-item">{r}</li>))}</ol>
          </div>

          <div className="hobby-recommendations-card">
            <h3>Hobby/Club Recommendations</h3>
            <ol className="recs-list">{hobbyRecs.map((r,i)=>(<li key={i} className="rec-item">{r}</li>))}</ol>
          </div>
        </div>
      </main>
    </div>
  )
}
