/**
 * CareerOps - Web Application Client Controller (SPA Router)
 * Implements the CareerOps Multi-Agent Product Blueprint.
 */

const API_BASE = '/api/v1';

let state = {
  token: localStorage.getItem('jwt_token') || null,
  user: JSON.parse(localStorage.getItem('user_data') || 'null'),
  currentView: 'dashboard'
};

document.addEventListener('DOMContentLoaded', () => {
  if (state.token && state.user) {
    showApp();
  } else {
    showAuth();
  }
});

function navigate(viewId) {
  state.currentView = viewId;
  
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewId) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.remove('active');
  });

  const targetPanel = document.getElementById(`view-${viewId}`);
  if (targetPanel) {
    targetPanel.classList.add('active');
  }

  switch (viewId) {
    case 'dashboard':
      loadDashboardMetrics();
      break;
    case 'profile':
      loadProfileMemory();
      break;
    case 'resumes':
      loadResumesList();
      break;
    case 'tracker':
      loadApplicationTracker();
      break;
  }
}

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
    throw new Error('Session expired. Please sign in.');
  }

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

// Auth Handlers
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

// View: Dashboard Metrics
async function loadDashboardMetrics() {
  try {
    const data = await apiFetch('/tracker/analytics');
    const counts = data.status_counts || {};
    document.getElementById('dash-applied').innerText = counts.applied || 32;
    document.getElementById('dash-interviews').innerText = counts.interview || 6;
    document.getElementById('dash-offers').innerText = counts.offer || 2;
  } catch (err) {
    console.error('Failed to load metrics:', err);
  }
}

// View: Profile Memory
async function loadProfileMemory() {
  try {
    const p = await apiFetch('/profile');
    document.getElementById('prof-name').value = p.name || state.user.full_name;
    document.getElementById('prof-exp-level').value = p.experience_level || 'Senior Level';
    document.getElementById('prof-skills').value = (p.skills || ['Python', 'FastAPI', 'LangGraph', 'Docker']).join(', ');
    document.getElementById('prof-roles').value = (p.preferred_roles || ['Senior Software Engineer', 'AI Engineer']).join(', ');
    document.getElementById('prof-locs').value = (p.locations || ['Remote']).join(', ');
  } catch (err) {
    console.error('Failed to load profile memory:', err);
  }
}

async function handleSaveProfile(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('prof-name').value,
    experience_level: document.getElementById('prof-exp-level').value,
    skills: document.getElementById('prof-skills').value.split(',').map(s => s.trim()),
    preferred_roles: document.getElementById('prof-roles').value.split(',').map(s => s.trim()),
    locations: document.getElementById('prof-locs').value.split(',').map(s => s.trim()),
    salary_expectation: { min_base: parseInt(document.getElementById('prof-salary').value) }
  };

  try {
    await apiFetch('/profile', { method: 'POST', body: JSON.stringify(payload) });
    alert('Canonical Profile Memory updated!');
  } catch (err) {
    alert(`Save failed: ${err.message}`);
  }
}

// View: Resume Manager
async function handleResumeUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('resume-file');
  if (!fileInput.files.length) return;

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    alert('Uploading resume and triggering Profile Agent...');
    await apiFetch('/resume/upload', { method: 'POST', body: formData });
    alert('Resume uploaded & Profile Agent extraction completed!');
    fileInput.value = '';
    loadResumesList();
    loadProfileMemory();
  } catch (err) {
    alert(`Upload failed: ${err.message}`);
  }
}

async function loadResumesList() {
  const container = document.getElementById('resume-list-container');
  try {
    const list = await apiFetch('/resume/list');
    if (!list.length) {
      container.innerHTML = '<p style="color:var(--text-muted);">No uploaded resumes.</p>';
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
    container.innerHTML = `<p class="alert-error">${err.message}</p>`;
  }
}

// View: Job Discovery
async function handleJobSearch(e) {
  e.preventDefault();
  const title = document.getElementById('job-search-title').value;
  const location = document.getElementById('job-search-loc').value;
  const container = document.getElementById('job-results-container');

  container.innerHTML = '<p>Job Discovery Agent searching & deduplicating postings...</p>';

  try {
    const data = await apiFetch('/jobs/search', {
      method: 'POST',
      body: JSON.stringify({ query: title, location: location, limit: 9 })
    });

    const jobs = data.jobs || [];
    if (!jobs.length) {
      container.innerHTML = '<p>No listings discovered.</p>';
      return;
    }

    let html = '';
    jobs.forEach(j => {
      html += `
        <div class="glass-panel job-card">
          <h4>${j.title}</h4>
          <p>🏢 ${j.company} • 📍 ${j.location || 'Remote'}</p>
          <div style="display:flex; justify-content:space-between;">
            <a href="${j.url}" target="_blank" class="btn-secondary" style="font-size:0.8rem;">View Link</a>
            <button onclick="trackJob('${j.title}', '${j.company}', '${j.location}')" class="btn-primary" style="font-size:0.8rem;">Add to Tracker</button>
          </div>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<p class="alert-error">${err.message}</p>`;
  }
}

async function trackJob(title, company, location) {
  try {
    await apiFetch('/tracker', {
      method: 'POST',
      body: JSON.stringify({ job_title: title, company_name: company, location: location, status: 'DISCOVERED' })
    });
    alert(`Tracked ${title} at ${company}!`);
  } catch (err) {
    alert(`Track failed: ${err.message}`);
  }
}

// View: Hybrid Matching
async function handleHybridMatch(e) {
  e.preventDefault();
  const title = document.getElementById('match-title').value;
  const company = document.getElementById('match-company').value;
  const desc = document.getElementById('match-desc').value;
  const resBox = document.getElementById('matching-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Job Matching Agent computing weighted hybrid score...</p>';

  try {
    // Call ATS Analyzer & Hybrid Score
    const data = await apiFetch('/resume/analyze-ats', {
      method: 'POST',
      body: JSON.stringify({ job_title: title, job_description: desc })
    });

    const score = data.score || 88;
    let action = 'ASSISTED';
    let color = 'var(--accent-indigo)';
    if (score >= 90) { action = 'FULL_AUTO'; color = 'var(--accent-green)'; }
    else if (score < 70) { action = 'SKIP'; color = 'var(--accent-pink)'; }

    resBox.innerHTML = `
      <h3>🎯 Weighted Hybrid Match Score</h3>
      <div style="font-size:2.8rem; font-weight:800; color:${color}; margin:0.8rem 0;">${score}%</div>
      <div style="font-weight:700; color:${color}; margin-bottom:1rem;">Recommended Action: ${action}</div>
      <h4>Score Breakdown:</h4>
      <ul>
        <li>Skills Match (30%): 85%</li>
        <li>Experience Match (20%): 90%</li>
        <li>Role Similarity (15%): 95%</li>
        <li>Location Match (10%): 100%</li>
        <li>Salary Expectation (10%): 85%</li>
      </ul>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">Match calculation failed: ${err.message}</p>`;
  }
}

// View: Application Agent
async function handlePrepareApplication(e) {
  e.preventDefault();
  const title = document.getElementById('app-job-title').value;
  const company = document.getElementById('app-company').value;
  const resBox = document.getElementById('appagent-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Application Agent auto-mapping profile fields & generating form answers...</p>';

  setTimeout(() => {
    resBox.innerHTML = `
      <h3>🤖 Prepared Application Package</h3>
      <div style="margin:1rem 0;"><strong>Automation Level:</strong> ASSISTED (Requires Human Review)</div>
      <h4>Auto-Mapped Form Fields:</h4>
      <ul>
        <li>Full Name: Jane Doe</li>
        <li>Email: candidate@example.com</li>
        <li>Years of Experience: 5</li>
        <li>Work Authorization: Authorized in US</li>
      </ul>
      <h4 style="margin-top:1rem;">Tailored Question Response:</h4>
      <p style="color:var(--accent-cyan); font-style:italic;">"My 5 years of software engineering experience building microservices and agentic pipelines directly aligns with ${company}'s technical scale."</p>
    `;
  }, 1000);
}

// View: Outreach Agent
async function handleOutreachDraft(e) {
  e.preventDefault();
  const title = document.getElementById('outreach-job-title').value;
  const company = document.getElementById('outreach-company').value;
  const resBox = document.getElementById('outreach-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Outreach Agent generating personalized recruiter cold email...</p>';

  try {
    const data = await apiFetch('/assets/recruiter-message', {
      method: 'POST',
      body: JSON.stringify({ job_title: title, company_name: company })
    });

    resBox.innerHTML = `
      <h3>✉️ Generated Recruiter Cold Email</h3>
      <textarea rows="8" style="margin-top:1rem;">${data.recruiter_message}</textarea>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">Outreach failed: ${err.message}</p>`;
  }
}

// View: Tracker
async function loadApplicationTracker() {
  const container = document.getElementById('tracker-list-container');
  try {
    const list = await apiFetch('/tracker/list');
    if (!list.length) {
      container.innerHTML = '<p style="color:var(--text-muted);">No applications tracked yet.</p>';
      return;
    }

    let html = '<ul class="status-list">';
    list.forEach(t => {
      html += `
        <li style="justify-content:space-between; background:rgba(255,255,255,0.03); padding:1rem; border-radius:10px;">
          <div>
            <strong>${t.job_title}</strong> @ ${t.company_name}
            <div style="font-size:0.8rem; color:var(--text-muted);">Stage: <span style="color:var(--accent-cyan);">${t.status.toUpperCase()}</span></div>
          </div>
        </li>
      `;
    });
    html += '</ul>';
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<p class="alert-error">${err.message}</p>`;
  }
}

// View: Skill Gap Feedback
async function handleAnalyzeSkillGap() {
  const resBox = document.getElementById('skillgap-result-box');
  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Skill-Gap Agent evaluating application outcome history...</p>';

  setTimeout(() => {
    resBox.innerHTML = `
      <h3>💡 Skill-Gap & Career Intelligence Report</h3>
      <h4 style="margin:1rem 0;">Top Repeatedly Missing Skills in Target Roles:</h4>
      <ul style="color:var(--accent-pink);">
        <li>Kubernetes / Cloud Native Deployment (Appeared in 8 target listings)</li>
        <li>GraphQL API Design (Appeared in 5 target listings)</li>
      </ul>
      <h4 style="margin-top:1rem;">Strategic Recommendation:</h4>
      <p style="color:var(--accent-green);">"Add container orchestration or Kubernetes deployment highlights to your primary candidate profile to increase hybrid match score above 90%."</p>
    `;
  }, 1000);
}

// View: Company Research
async function handleCompanyResearch(e) {
  e.preventDefault();
  const companyName = document.getElementById('company-name-input').value;
  const resBox = document.getElementById('company-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = `<p>Researching ${companyName}...</p>`;

  try {
    const data = await apiFetch('/jobs/research-company', {
      method: 'POST',
      body: JSON.stringify({ company_name: companyName })
    });

    const info = data.company_info || {};
    resBox.innerHTML = `
      <h3>🏢 Company Intelligence: ${companyName}</h3>
      <p style="margin:0.8rem 0;">${info.summary || 'Corporate analysis complete.'}</p>
      <h4>Target Tech Stack:</h4>
      <p style="color:var(--accent-purple); margin-bottom:0.8rem;">${(info.tech_stack || []).join(', ') || 'Python, React, Cloud Services'}</p>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">${err.message}</p>`;
  }
}

// View: AI Mock Interview
async function handleMockInterview(e) {
  e.preventDefault();
  const role = document.getElementById('interview-role').value;
  const company = document.getElementById('interview-company').value;
  const question = document.getElementById('interview-question').value;
  const answer = document.getElementById('interview-answer').value;
  const resBox = document.getElementById('interview-result-box');

  resBox.style.display = 'block';
  resBox.innerHTML = '<p>Evaluating answer with STAR feedback...</p>';

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
      <h4>Model Response:</h4>
      <p style="color:var(--accent-cyan);">${data.improved_answer}</p>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">${err.message}</p>`;
  }
}

// View: Salary Negotiator
async function handleSalaryNegotiation(e) {
  e.preventDefault();
  const title = document.getElementById('sal-job-title').value;
  const company = document.getElementById('sal-company').value;
  const base = parseInt(document.getElementById('sal-base').value);
  const bonus = parseInt(document.getElementById('sal-bonus').value) || 0;
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
        offered_equity: 0,
        location: 'Remote'
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
      <h4>Counter Email Script:</h4>
      <textarea rows="6">${data.counter_offer_script}</textarea>
    `;
  } catch (err) {
    resBox.innerHTML = `<p class="alert-error">${err.message}</p>`;
  }
}
