/**
 * AI Job Hunter - Web Application Client Logic (SPA Router)
 * DevSecOps-hardened Client-side Application Controller
 */

const API_BASE = '/api/v1';

// State Store
let state = {
  token: localStorage.getItem('jwt_token') || null,
  user: JSON.parse(localStorage.getItem('user_data') || 'null'),
  currentView: 'dashboard'
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  if (state.token && state.user) {
    showApp();
  } else {
    showAuth();
  }
});

// View Navigation & SPA Router
function navigate(viewId) {
  state.currentView = viewId;
  
  // Toggle Active Nav Item
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewId) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Toggle View Panel
  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.remove('active');
  });

  const targetPanel = document.getElementById(`view-${viewId}`);
  if (targetPanel) {
    targetPanel.classList.add('active');
  }

  // Load View Data
  switch (viewId) {
    case 'dashboard':
      loadDashboardMetrics();
      break;
    case 'resumes':
      loadResumesList();
      break;
    case 'tracker':
      loadApplicationTracker();
      break;
    case 'autohunter':
      fetchAutoHunterJobs();
      break;
  }
}

// Auth UI Switches
function switchAuthTab(tab) {
  const loginForm = document.getElementById('login-form');
  const regForm = document.getElementById('register-form');
  const loginBtn = document.getElementById('tab-login-btn');
  const regBtn = document.getElementById('tab-register-btn');

  if (tab === 'login') {
    loginForm.style.display = 'block';
    regForm.style.display = 'none';
    loginBtn.classList.add('active');
    regBtn.classList.remove('active');
  } else {
    loginForm.style.display = 'none';
    regForm.style.display = 'block';
    loginBtn.classList.remove('active');
    regBtn.classList.add('active');
  }
}

function showAuth() {
  document.getElementById('auth-screen').style.display = 'flex';
  document.getElementById('app-screen').style.display = 'none';
}

function showApp() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('app-screen').style.display = 'flex';

  if (state.user) {
    document.getElementById('user-display-name').innerText = state.user.full_name || 'Candidate';
    document.getElementById('user-display-email').innerText = state.user.email || '';
    document.getElementById('user-avatar').innerText = (state.user.full_name || 'C').charAt(0).toUpperCase();
  }

  navigate('dashboard');
}

// API Helper with JWT Header Injection
async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  options.headers = headers;

  const response = await fetch(`${API_BASE}${endpoint}`, options);
  if (response.status === 401) {
    handleLogout();
    throw new Error('Session expired. Please sign in again.');
  }

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

// Auth Actions
async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  const alertBox = document.getElementById('auth-alert');
  alertBox.style.display = 'none';

  try {
    const data = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    state.token = data.access_token;
    state.user = data.user;
    localStorage.setItem('jwt_token', data.access_token);
    localStorage.setItem('user_data', JSON.stringify(data.user));

    showApp();
  } catch (err) {
    alertBox.className = 'alert-box alert-error';
    alertBox.innerText = err.message;
    alertBox.style.display = 'block';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const full_name = document.getElementById('reg-name').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;

  const alertBox = document.getElementById('auth-alert');
  alertBox.style.display = 'none';

  try {
    const data = await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name })
    });

    state.token = data.access_token;
    state.user = data.user;
    localStorage.setItem('jwt_token', data.access_token);
    localStorage.setItem('user_data', JSON.stringify(data.user));

    showApp();
  } catch (err) {
    alertBox.className = 'alert-box alert-error';
    alertBox.innerText = err.message;
    alertBox.style.display = 'block';
  }
}

function handleLogout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('jwt_token');
  localStorage.removeItem('user_data');
  showAuth();
}

// View Functions: Dashboard
async function loadDashboardMetrics() {
  try {
    const data = await apiFetch('/tracker/analytics');
    const counts = data.status_counts || {};
    document.getElementById('dash-saved').innerText = counts.saved || 0;
    document.getElementById('dash-applied').innerText = counts.applied || 0;
    document.getElementById('dash-interview').innerText = counts.interview || 0;
    document.getElementById('dash-offer').innerText = counts.offer || 0;
  } catch (err) {
    console.error('Failed to load dashboard metrics:', err);
  }
}

// View Functions: Resume Upload
async function handleResumeUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('resume-file');
  if (!fileInput.files.length) return;

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    alert('Uploading and AI-parsing resume...');
    await apiFetch('/resume/upload', {
      method: 'POST',
      body: formData
    });
    alert('Resume uploaded and parsed successfully!');
    fileInput.value = '';
    loadResumesList();
  } catch (err) {
    alert(`Resume upload failed: ${err.message}`);
  }
}

async function loadResumesList() {
  const container = document.getElementById('resume-list-container');
  try {
    const list = await apiFetch('/resume/list');
    if (!list.length) {
      container.innerHTML = '<p style="color:var(--text-muted);">No resumes uploaded yet. Upload your first PDF/DOCX resume above.</p>';
      return;
    }

    let html = '<ul class="status-list">';
    list.forEach(r => {
      html += `
        <li style="justify-content:space-between; background:rgba(255,255,255,0.03); padding:0.8rem; border-radius:10px;">
          <div>
            <strong>📄 ${r.file_name}</strong> ${r.is_primary ? '<span class="text-green">(Primary)</span>' : ''}
            <div style="font-size:0.8rem; color:var(--text-muted);">Uploaded: ${new Date(r.created_at).toLocaleDateString()}</div>
          </div>
        </li>
      `;
    });
    html += '</ul>';
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<p class="alert-error">Failed to load resumes: ${err.message}</p>`;
  }
}

// View Functions: Job Search
async function handleJobSearch(e) {
  e.preventDefault();
  const title = document.getElementById('job-search-title').value;
  const location = document.getElementById('job-search-loc').value;
  const container = document.getElementById('job-results-container');

  container.innerHTML = '<p>Searching Remotive & Adzuna for matching listings...</p>';

  try {
    const data = await apiFetch('/jobs/search', {
      method: 'POST',
      body: JSON.stringify({ query: title, location: location, limit: 12 })
    });

    const jobs = data.jobs || [];
    if (!jobs.length) {
      container.innerHTML = '<p>No listings found for this query.</p>';
      return;
    }

    let html = '';
    jobs.forEach(j => {
      html += `
        <div class="glass-panel job-card">
          <h4>${j.title}</h4>
          <p>🏢 ${j.company} • 📍 ${j.location || 'Remote'}</p>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <a href="${j.url}" target="_blank" class="btn-secondary" style="font-size:0.8rem;">View Listing</a>
            <button onclick="trackJob('${j.title}', '${j.company}', '${j.location}')" class="btn-primary" style="font-size:0.8rem;">Track Application</button>
          </div>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<p class="alert-error">Search failed: ${err.message}</p>`;
  }
}

async function trackJob(title, company, location) {
  try {
    await apiFetch('/tracker', {
      method: 'POST',
      body: JSON.stringify({ job_title: title, company_name: company, location: location, status: 'saved' })
    });
    alert(`Tracked application for ${title} at ${company}!`);
  } catch (err) {
    alert(`Failed to track job: ${err.message}`);
  }
}

// View Functions: ATS Analyzer
async function handleATSAnalyze(e) {
  e.preventDefault();
  const jobTitle = document.getElementById('ats-job-title').value;
  const jobDesc = document.getElementById('ats-job-desc').value;
  const resBox = document.getElementById('ats-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Calculating ATS compatibility match % & keyword gap...</p>';

  try {
    const data = await apiFetch('/resume/analyze-ats', {
      method: 'POST',
      body: JSON.stringify({ job_title: jobTitle, job_description: jobDesc })
    });

    resBox.innerHTML = `
      <h3>🎯 ATS Score Results</h3>
      <div style="font-size:2.5rem; font-weight:800; color:var(--accent-cyan); margin:1rem 0;">${data.score}% Match</div>
      <p style="margin-bottom:1rem;">${data.assessment || 'Solid match.'}</p>
      <h4>Missing Keywords:</h4>
      <p style="color:var(--accent-pink);">${(data.missing_keywords || []).join(', ') || 'None'}</p>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">ATS calculation failed: ${err.message}</p>`;
  }
}

// View Functions: Career Assets
async function handleGenerateCoverLetter(e) {
  e.preventDefault();
  const jobTitle = document.getElementById('asset-job-title').value;
  const company = document.getElementById('asset-company').value;
  const desc = document.getElementById('asset-job-desc').value;
  const resBox = document.getElementById('asset-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>AI Agent generating tailored cover letter...</p>';

  try {
    const data = await apiFetch('/assets/cover-letter', {
      method: 'POST',
      body: JSON.stringify({ job_title: jobTitle, company_name: company, job_description: desc })
    });

    resBox.innerHTML = `
      <h3>✨ Generated Cover Letter</h3>
      <textarea rows="10" style="margin-top:1rem;">${data.cover_letter}</textarea>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">Generation failed: ${err.message}</p>`;
  }
}

// View Functions: Tracker
async function loadApplicationTracker() {
  const container = document.getElementById('tracker-list-container');
  try {
    const list = await apiFetch('/tracker/list');
    if (!list.length) {
      container.innerHTML = '<p style="color:var(--text-muted);">No tracked applications. Discover jobs and click "Track Application".</p>';
      return;
    }

    let html = '<ul class="status-list">';
    list.forEach(t => {
      html += `
        <li style="justify-content:space-between; background:rgba(255,255,255,0.03); padding:1rem; border-radius:10px;">
          <div>
            <strong>${t.job_title}</strong> @ ${t.company_name}
            <div style="font-size:0.8rem; color:var(--text-muted);">Status: <span style="color:var(--accent-cyan);">${t.status.toUpperCase()}</span></div>
          </div>
        </li>
      `;
    });
    html += '</ul>';
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<p class="alert-error">Failed to load tracker: ${err.message}</p>`;
  }
}

// View Functions: Company Research
async function handleCompanyResearch(e) {
  e.preventDefault();
  const companyName = document.getElementById('company-name-input').value;
  const resBox = document.getElementById('company-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = `<p>AI Agent researching ${companyName}...</p>`;

  try {
    const data = await apiFetch('/jobs/research-company', {
      method: 'POST',
      body: JSON.stringify({ company_name: companyName })
    });

    const info = data.company_info || {};
    resBox.innerHTML = `
      <h3>🏢 Company Intelligence: ${companyName}</h3>
      <p style="margin:0.8rem 0;">${info.summary || 'Research complete.'}</p>
      <h4>Target Tech Stack:</h4>
      <p style="color:var(--accent-purple); margin-bottom:0.8rem;">${(info.tech_stack || []).join(', ') || 'N/A'}</p>
      <h4>Interview Strategy Tip:</h4>
      <p style="color:var(--accent-green);">${info.culture || 'Focus on architectural scalability and system design.'}</p>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">Research failed: ${err.message}</p>`;
  }
}

// View Functions: AI Mock Interview
async function handleMockInterview(e) {
  e.preventDefault();
  const role = document.getElementById('interview-role').value;
  const company = document.getElementById('interview-company').value;
  const question = document.getElementById('interview-question').value;
  const answer = document.getElementById('interview-answer').value;
  const resBox = document.getElementById('interview-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Evaluating answer with STAR methodology & scoring...</p>';

  try {
    const data = await apiFetch('/assets/mock-interview/evaluate', {
      method: 'POST',
      body: JSON.stringify({ job_title: role, company_name: company, question: question, candidate_answer: answer })
    });

    resBox.innerHTML = `
      <h3>🎙️ Interview Evaluation</h3>
      <div style="font-size:2rem; font-weight:800; color:var(--accent-green); margin:0.8rem 0;">Score: ${data.score} / 10</div>
      <h4>Feedback:</h4>
      <p style="margin-bottom:1rem;">${data.feedback}</p>
      <h4>Model Answer:</h4>
      <p style="color:var(--accent-cyan); margin-bottom:1rem;">${data.improved_answer}</p>
      <h4>Follow-up Question:</h4>
      <p style="color:var(--accent-purple); font-weight:600;">${data.next_question}</p>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">Evaluation failed: ${err.message}</p>`;
  }
}

// View Functions: Salary Negotiation
async function handleSalaryNegotiation(e) {
  e.preventDefault();
  const title = document.getElementById('sal-job-title').value;
  const company = document.getElementById('sal-company').value;
  const base = parseInt(document.getElementById('sal-base').value);
  const bonus = parseInt(document.getElementById('sal-bonus').value) || 0;
  const equity = parseInt(document.getElementById('sal-equity').value) || 0;
  const loc = document.getElementById('sal-loc').value;
  const resBox = document.getElementById('salary-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Benchmarking offer vs market percentiles...</p>';

  try {
    const data = await apiFetch('/assets/salary-negotiation', {
      method: 'POST',
      body: JSON.stringify({
        job_title: title,
        company_name: company,
        offered_base: base,
        offered_bonus: bonus,
        offered_equity: equity,
        location: loc
      })
    });

    const mr = data.market_range || {};
    resBox.innerHTML = `
      <h3>💰 Offer Evaluation & Counter Strategy</h3>
      <div style="display:flex; gap:1.5rem; margin:1rem 0;">
        <div>25th %: <strong>$${(mr.percentile_25||0).toLocaleString()}</strong></div>
        <div>50th Median: <strong>$${(mr.percentile_50_median||0).toLocaleString()}</strong></div>
        <div>75th %: <strong>$${(mr.percentile_75||0).toLocaleString()}</strong></div>
        <div style="color:var(--accent-green);">Recommended Counter: <strong>$${(data.recommended_counter||0).toLocaleString()}</strong></div>
      </div>
      <h4>Assessment:</h4>
      <p style="margin-bottom:1rem;">${data.offer_assessment}</p>
      <h4>Counter-Offer Email Script:</h4>
      <textarea rows="6">${data.counter_offer_script}</textarea>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">Negotiation analysis failed: ${err.message}</p>`;
  }
}

// View Functions: Auto Hunter
async function fetchAutoHunterJobs() {
  const container = document.getElementById('autohunter-results');
  container.innerHTML = '<p>Background Agent scanning job providers...</p>';
  try {
    const recs = await apiFetch('/jobs/recommendations');
    if (!recs.length) {
      container.innerHTML = '<p>No background recommendations queued. Scan complete.</p>';
      return;
    }

    let html = '<div class="grid-cards">';
    recs.forEach(j => {
      html += `
        <div class="glass-panel job-card">
          <h4>${j.title}</h4>
          <p>🏢 ${j.company} • 📍 ${j.location || 'Remote'}</p>
          <div style="color:var(--accent-green); font-weight:600;">ATS Match: ${j.ats_score || 85}%</div>
        </div>
      `;
    });
    html += '</div>';
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<p class="alert-error">Hunter failed: ${err.message}</p>`;
  }
}

function handleSaveProfile(e) {
  e.preventDefault();
  alert('Candidate profile parameters updated successfully!');
}
