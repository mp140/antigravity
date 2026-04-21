/**
 * ANTIGRAVITY v3.0 — Dashboard Logic
 * Handles API calls, tab switching, rendering, and live updates.
 */

const API = '';

// ═══ Tab Navigation ═══
document.querySelectorAll('.nav-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`panel-${tab.dataset.tab}`).classList.add('active');
    const tabName = tab.dataset.tab;
    if (tabName === 'platforms') loadPlatforms();
    if (tabName === 'signals') loadSignals();
    if (tabName === 'portfolio') loadPortfolio();
    if (tabName === 'performance') loadPerformance();
    if (tabName === 'intelligence') loadIntelligence();
    if (tabName === 'autobot') loadBotDashboard();
  });
});

// ═══ Clock ═══
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();

// ═══ Enter key support ═══
document.getElementById('ticker-input').addEventListener('keydown', e => { if (e.key === 'Enter') analyzeStock(); });
document.getElementById('trading-ticker')?.addEventListener('keydown', e => { if (e.key === 'Enter') liveAnalyze(); });
document.getElementById('news-ticker')?.addEventListener('keydown', e => { if (e.key === 'Enter') searchNews(); });

// ═══ API Helper ═══
async function apiFetch(endpoint) {
  try {
    const res = await fetch(`${API}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    return null;
  }
}

// ═══ Analyze Stock (Full) ═══
async function analyzeStock() {
  const ticker = document.getElementById('ticker-input').value.trim().toUpperCase();
  if (!ticker) return;
  const container = document.getElementById('analysis-result');
  container.style.display = 'block';
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span class="loading-text">Running multi-agent analysis on ${ticker}...</span></div>`;

  const data = await apiFetch(`/api/stock/${ticker}`);
  if (!data || data.error) {
    container.innerHTML = `<div class="card"><p style="color:var(--red);">Error: ${data?.error || 'Failed to analyze'}</p></div>`;
    return;
  }
  container.innerHTML = renderFullAnalysis(data);
}

function renderFullAnalysis(d) {
  const actionClass = d.action === 'BUY' ? 'buy' : d.action === 'SELL' ? 'sell' : 'hold';
  const actionBadge = `<span class="card-badge badge-${actionClass}">${d.action}</span>`;
  const conf = d.confidence || 0;
  const risk = d.risk || {};
  const tech = d.technical || {};
  const sent = d.sentiment || {};
  const macro = d.macro || {};
  const pats = d.patterns || {};

  return `
    <div class="card mb-6" style="border-top: 3px solid ${d.action === 'BUY' ? 'var(--green)' : d.action === 'SELL' ? 'var(--red)' : 'var(--accent-amber)'}">
      <div class="card-header">
        <div>
          <span class="signal-ticker">${d.ticker}</span>
          ${actionBadge}
        </div>
        <span class="text-sm font-mono" style="color:var(--text-muted)">${d.elapsed_seconds}s</span>
      </div>

      <!-- Confidence Meter -->
      <div style="margin-bottom:20px;">
        <div class="flex justify-between items-center mb-4">
          <span class="text-sm" style="color:var(--text-secondary)">AI Confidence</span>
          <span class="font-mono font-bold ${conf >= 70 ? 'text-green' : conf >= 50 ? 'text-amber' : 'text-red'}">${conf}%</span>
        </div>
        <div class="confidence-meter">
          <div class="confidence-fill" style="width: ${conf}%"></div>
        </div>
      </div>

      <!-- Agent Swarm Grid -->
      <div class="agent-grid mb-6">
        <div class="agent-card">
          <div class="agent-name">🌍 MACRO</div>
          <div class="agent-score ${macro.regime === 'RISK_ON' ? 'text-green' : macro.regime === 'RISK_OFF' ? 'text-red' : 'text-amber'}">${macro.regime || 'N/A'}</div>
          <div class="agent-label">VIX: ${macro.vix || '—'}</div>
        </div>
        <div class="agent-card">
          <div class="agent-name">📊 TECHNICAL</div>
          <div class="agent-score ${(tech.score||50) >= 60 ? 'text-green' : (tech.score||50) <= 40 ? 'text-red' : 'text-amber'}">${tech.score || 50}</div>
          <div class="agent-label">${tech.trend || 'neutral'}</div>
        </div>
        <div class="agent-card">
          <div class="agent-name">🕯️ PATTERNS</div>
          <div class="agent-score ${(pats.score||50) >= 60 ? 'text-green' : (pats.score||50) <= 40 ? 'text-red' : 'text-amber'}">${pats.score || 50}</div>
          <div class="agent-label">${pats.bias || 'neutral'}</div>
        </div>
        <div class="agent-card">
          <div class="agent-name">💬 SENTIMENT</div>
          <div class="agent-score ${(sent.score||50) >= 60 ? 'text-green' : (sent.score||50) <= 40 ? 'text-red' : 'text-amber'}">${sent.score || 50}</div>
          <div class="agent-label">${sent.label || 'neutral'} (${sent.news_count || 0} news)</div>
        </div>
        <div class="agent-card">
          <div class="agent-name">🛡️ RISK</div>
          <div class="agent-score ${risk.approved ? 'text-green' : 'text-red'}">${risk.approved ? 'OK' : 'BLOCK'}</div>
          <div class="agent-label">${risk.risk_reward_ratio || '—'}</div>
        </div>
        <div class="agent-card">
          <div class="agent-name">🧠 DECISION</div>
          <div class="agent-score ${d.action === 'BUY' ? 'text-green' : d.action === 'SELL' ? 'text-red' : 'text-amber'}">${(d.final_score * 100).toFixed(0)}%</div>
          <div class="agent-label">${d.action}</div>
        </div>
      </div>

      ${risk.approved ? `
      <!-- Trade Levels -->
      <div class="signal-levels">
        <div class="signal-level">
          <div class="signal-level-label">Entry</div>
          <div class="signal-level-value text-blue">$${risk.entry_price}</div>
        </div>
        <div class="signal-level">
          <div class="signal-level-label">Stop Loss</div>
          <div class="signal-level-value text-red">$${risk.stop_loss}</div>
        </div>
        <div class="signal-level">
          <div class="signal-level-label">Take Profit</div>
          <div class="signal-level-value text-green">$${risk.take_profit_1}</div>
        </div>
      </div>
      <div class="flex justify-between mt-4 text-sm" style="color:var(--text-muted)">
        <span>Position: ${risk.position_size} shares ($${risk.position_value})</span>
        <span>Risk: $${risk.risk_amount} | R:R ${risk.risk_reward_ratio}</span>
      </div>
      ` : ''}

      <!-- Signals List -->
      ${(tech.signals || []).length > 0 ? `
      <div class="mt-6">
        <h4 style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;">Technical Signals</h4>
        <div class="flex gap-4" style="flex-wrap:wrap;">
          ${tech.signals.map(s => `
            <span class="card-badge badge-${s.bias === 'bullish' ? 'bullish' : s.bias === 'bearish' ? 'bearish' : 'neutral'}">
              ${s.indicator}: ${s.signal}
            </span>`).join('')}
        </div>
      </div>` : ''}

      <!-- Headlines -->
      ${(sent.top_headlines || []).length > 0 ? `
      <div class="mt-6">
        <h4 style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;">Top Headlines</h4>
        ${sent.top_headlines.map(h => `
          <div class="news-item">
            <div class="news-title">${h.title}</div>
            <div class="news-meta"><span class="news-source">${h.source}</span></div>
          </div>`).join('')}
      </div>` : ''}
    </div>`;
}

// ═══ Live Trading Analysis ═══
async function liveAnalyze() {
  const ticker = document.getElementById('trading-ticker').value.trim().toUpperCase();
  if (!ticker) return;
  const container = document.getElementById('live-result');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span class="loading-text">Full AI analysis: ${ticker}...</span></div>`;
  const data = await apiFetch(`/api/report/${ticker}`);
  if (!data) { container.innerHTML = `<div class="card"><p style="color:var(--red)">Analysis failed</p></div>`; return; }
  const analysis = data.analysis || {};
  const prediction = data.prediction || {};
  container.innerHTML = `
    ${renderFullAnalysis(analysis)}
    <div class="card mt-4">
      <div class="card-header">
        <span class="card-title">🤖 AI Prediction</span>
        <span class="card-badge badge-${prediction.direction === 'UP' ? 'bullish' : prediction.direction === 'DOWN' ? 'bearish' : 'neutral'}">${prediction.direction || 'N/A'}</span>
      </div>
      <div class="grid-3">
        <div class="stat-box">
          <div class="stat-value ${prediction.probability_up > 0.55 ? 'text-green' : prediction.probability_up < 0.45 ? 'text-red' : 'text-amber'}">${((prediction.probability_up || 0.5) * 100).toFixed(1)}%</div>
          <div class="stat-label">Probability Up</div>
        </div>
        <div class="stat-box">
          <div class="stat-value text-cyan">${prediction.confidence || 0}%</div>
          <div class="stat-label">Confidence</div>
        </div>
        <div class="stat-box">
          <div class="stat-value">${prediction.predicted_move_pct || 0}%</div>
          <div class="stat-label">Predicted Move</div>
        </div>
      </div>
      ${prediction.model_accuracy ? `
      <div class="mt-4 text-sm" style="color:var(--text-muted)">
        Model Accuracy — RF: ${prediction.model_accuracy.random_forest}% | GB: ${prediction.model_accuracy.gradient_boosting}% | Ensemble: ${prediction.model_accuracy.ensemble}%
      </div>` : ''}
    </div>`;
}

// ═══ Top 25 ═══
async function refreshTop25() {
  const container = document.getElementById('top25-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span class="loading-text">Scanning markets...</span></div>`;
  const data = await apiFetch('/api/top25');
  if (!data || !data.top25) { container.innerHTML = '<p style="color:var(--text-muted)">Failed to load</p>'; return; }
  container.innerHTML = `
    <table class="data-table">
      <thead><tr><th>#</th><th>Ticker</th><th>Price</th><th>Change</th><th>Score</th><th>Trend</th></tr></thead>
      <tbody>
        ${data.top25.map((item, i) => `
          <tr onclick="analyzeFromTable('${item.ticker}')" style="cursor:pointer">
            <td style="color:var(--text-muted)">${i + 1}</td>
            <td class="ticker">${item.ticker}</td>
            <td class="price">${item.formatted?.price || '$' + (item.price || 0).toFixed(2)}</td>
            <td style="color:${(item.change_pct || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">${item.formatted?.change_pct || (item.change_pct || 0).toFixed(2) + '%'}</td>
            <td><span class="font-mono font-bold ${(item.score || 50) >= 60 ? 'text-green' : (item.score || 50) <= 40 ? 'text-red' : 'text-amber'}">${item.score || 50}</span></td>
            <td><span class="card-badge badge-${item.trend === 'bullish' ? 'bullish' : item.trend === 'bearish' ? 'bearish' : 'neutral'}">${item.trend || 'neutral'}</span></td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}

function analyzeFromTable(ticker) {
  document.getElementById('ticker-input').value = ticker;
  analyzeStock();
}

// ═══ Macro ═══
async function loadMacro() {
  const container = document.getElementById('macro-container');
  const data = await apiFetch('/api/stock/SPY');
  if (!data) { container.innerHTML = '<p style="color:var(--text-muted)">Loading...</p>'; return; }
  const macro = data.macro || {};
  container.innerHTML = `
    <div class="stat-box mb-4">
      <div class="stat-value ${macro.regime === 'RISK_ON' ? 'text-green' : macro.regime === 'RISK_OFF' ? 'text-red' : 'text-amber'}">${macro.regime || 'NEUTRAL'}</div>
      <div class="stat-label">Market Regime</div>
    </div>
    <div class="grid-2 gap-4">
      <div class="stat-box">
        <div class="stat-value text-cyan">${macro.vix || '—'}</div>
        <div class="stat-label">VIX</div>
      </div>
      <div class="stat-box">
        <div class="stat-value">${macro.regime_score || '—'}</div>
        <div class="stat-label">Score</div>
      </div>
    </div>
    <p class="text-sm mt-4" style="color:var(--text-secondary)">${macro.recommendation || ''}</p>`;
}

// ═══ News Feed ═══
async function loadGlobalNews() {
  const container = document.getElementById('news-container');
  const data = await apiFetch('/api/global-news');
  if (!data || !data.news) { container.innerHTML = '<p style="color:var(--text-muted)">No news available</p>'; return; }
  container.innerHTML = data.news.slice(0, 8).map(n => `
    <div class="news-item">
      <div class="news-title">${n.title}</div>
      <div class="news-meta">
        <span class="news-source">${n.source}</span>
        <span>${n.published || ''}</span>
      </div>
    </div>`).join('');
}

// ═══ Intelligence ═══
async function loadIntelligence() {
  const newsContainer = document.getElementById('intel-news');
  const sentContainer = document.getElementById('intel-sentiment');
  const data = await apiFetch('/api/global-news');
  if (!data) return;
  newsContainer.innerHTML = (data.news || []).slice(0, 12).map(n => `
    <div class="news-item">
      <div class="news-title">${n.title}</div>
      <div class="news-meta"><span class="news-source">${n.source}</span></div>
    </div>`).join('');
  const sent = data.sentiment || {};
  sentContainer.innerHTML = `
    <div class="stat-box mb-4">
      <div class="stat-value ${sent.label?.includes('bullish') ? 'text-green' : sent.label?.includes('bearish') ? 'text-red' : 'text-amber'}">${sent.label || 'Neutral'}</div>
      <div class="stat-label">Market Sentiment</div>
    </div>
    <div class="grid-2 gap-4">
      <div class="stat-box"><div class="stat-value text-green">${sent.bullish_count || 0}</div><div class="stat-label">Bullish</div></div>
      <div class="stat-box"><div class="stat-value text-red">${sent.bearish_count || 0}</div><div class="stat-label">Bearish</div></div>
    </div>
    <div class="mt-4">
      <div class="confidence-meter"><div class="confidence-fill" style="width: ${Math.max(5, (sent.aggregate_score + 1) * 50)}%"></div></div>
      <div class="text-sm font-mono" style="color:var(--text-muted);margin-top:4px">Score: ${sent.aggregate_score?.toFixed(3) || 0}</div>
    </div>`;
}

async function searchNews() {
  const ticker = document.getElementById('news-ticker').value.trim().toUpperCase();
  if (!ticker) return;
  const data = await apiFetch(`/api/news/${ticker}`);
  if (!data) return;
  document.getElementById('intel-news').innerHTML = (data.news || []).slice(0, 12).map(n => `
    <div class="news-item"><div class="news-title">${n.title}</div><div class="news-meta"><span class="news-source">${n.source}</span></div></div>`).join('');
  const sent = data.sentiment || {};
  document.getElementById('intel-sentiment').innerHTML = `
    <div class="stat-box mb-4"><div class="stat-value ${sent.label?.includes('bullish') ? 'text-green' : sent.label?.includes('bearish') ? 'text-red' : 'text-amber'}">${sent.label || 'Neutral'}</div><div class="stat-label">${ticker} Sentiment</div></div>
    <div class="confidence-meter"><div class="confidence-fill" style="width: ${Math.max(5, (sent.aggregate_score + 1) * 50)}%"></div></div>`;
}

// ═══ Scanner ═══
async function scanCategory(category) {
  const container = document.getElementById('scanner-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span class="loading-text">Scanning ${category}...</span></div>`;
  const data = await apiFetch('/api/top100');
  if (!data || !data.categories) { container.innerHTML = '<p style="color:var(--text-muted)">Failed</p>'; return; }
  const items = data.categories[category] || [];
  container.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Ticker</th><th>Name</th><th>Price</th><th>Change</th><th>Volume</th></tr></thead>
      <tbody>${items.map(item => `
        <tr onclick="document.getElementById('ticker-input').value='${item.ticker}';document.querySelector('[data-tab=command]').click();analyzeStock();" style="cursor:pointer">
          <td class="ticker">${item.ticker}</td>
          <td>${item.name || item.ticker}</td>
          <td class="price">${item.formatted?.price || ''}</td>
          <td style="color:${(item.change_pct||0)>=0?'var(--green)':'var(--red)'}">${item.formatted?.change_pct || ''}</td>
          <td style="color:var(--text-muted)">${item.formatted?.volume || ''}</td>
        </tr>`).join('')}
      </tbody>
    </table>`;
}

// ═══ Platforms ═══
async function loadPlatforms() {
  const container = document.getElementById('platforms-container');
  const data = await apiFetch('/api/platforms');
  if (!data) return;
  container.innerHTML = `
    <div class="platform-row" style="font-size:11px;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.5px">
      <span>#</span><span>Platform</span><span>Type</span><span>Reliability</span><span>Rating</span><span>API</span>
    </div>
    ${(data.platforms || []).map(p => `
      <div class="platform-row">
        <span class="platform-rank">${p.rank}</span>
        <span class="platform-name">${p.name}</span>
        <span class="platform-type">${p.type}</span>
        <span style="font-size:12px;color:var(--text-secondary)">${p.reliability}</span>
        <span class="platform-rating">★ ${p.rating}</span>
        <span class="api-badge ${p.api ? 'api-yes' : 'api-no'}">${p.api ? 'API' : '—'}</span>
      </div>`).join('')}`;
}

// ═══ Signals ═══
async function loadSignals() {
  const container = document.getElementById('signals-container');
  const data = await apiFetch('/api/signals');
  if (!data || !data.signals || data.signals.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px;">No active signals. Run analysis to generate signals.</p>';
    return;
  }
  container.innerHTML = `<div class="grid-2">${data.signals.map(s => `
    <div class="signal-card ${s.action === 'BUY' ? 'buy' : 'sell'}">
      <div class="flex justify-between items-center mb-4">
        <span class="signal-ticker">${s.ticker}</span>
        <span class="signal-action" style="background:${s.action==='BUY'?'rgba(34,197,94,0.2)':'rgba(239,68,68,0.2)'};color:${s.action==='BUY'?'var(--green)':'var(--red)'}">${s.action}</span>
      </div>
      <div class="signal-levels">
        <div class="signal-level"><div class="signal-level-label">Entry</div><div class="signal-level-value text-blue">$${s.entry_price}</div></div>
        <div class="signal-level"><div class="signal-level-label">Stop Loss</div><div class="signal-level-value text-red">$${s.stop_loss}</div></div>
        <div class="signal-level"><div class="signal-level-label">TP1</div><div class="signal-level-value text-green">$${s.take_profit_1}</div></div>
      </div>
      <div class="flex justify-between mt-4 text-sm" style="color:var(--text-muted)">
        <span>Conf: ${s.confidence}%</span><span>R:R ${s.risk_reward}</span>
      </div>
    </div>`).join('')}</div>`;
}

// ═══ Portfolio ═══
async function loadPortfolio() {
  const data = await apiFetch('/api/portfolio');
  if (!data) return;
  document.getElementById('portfolio-stats').innerHTML = `
    <div class="stat-box"><div class="stat-value text-indigo">$${(data.capital||0).toLocaleString()}</div><div class="stat-label">Capital</div></div>
    <div class="stat-box"><div class="stat-value ${(data.total_return||0)>=0?'text-green':'text-red'}">${(data.total_return||0).toFixed(1)}%</div><div class="stat-label">Total Return</div></div>
    <div class="stat-box"><div class="stat-value text-cyan">${data.open_count||0}</div><div class="stat-label">Open Positions</div></div>
    <div class="stat-box"><div class="stat-value ${(data.total_unrealized_pnl||0)>=0?'text-green':'text-red'}">$${(data.total_unrealized_pnl||0).toFixed(2)}</div><div class="stat-label">Unrealized P&L</div></div>`;
  const positions = data.open_positions || [];
  document.getElementById('portfolio-positions').innerHTML = positions.length === 0
    ? '<p style="color:var(--text-muted);text-align:center;padding:40px;">No open positions</p>'
    : `<table class="data-table"><thead><tr><th>Ticker</th><th>Direction</th><th>Entry</th><th>Current</th><th>P&L</th><th>P&L %</th></tr></thead><tbody>
      ${positions.map(p => `<tr>
        <td class="ticker">${p.ticker}</td><td>${p.direction}</td><td class="price">$${p.entry_price}</td><td class="price">$${p.current_price}</td>
        <td style="color:${p.unrealized_pnl>=0?'var(--green)':'var(--red)'}">$${p.unrealized_pnl}</td>
        <td style="color:${p.pnl_pct>=0?'var(--green)':'var(--red)'}">${p.pnl_pct}%</td></tr>`).join('')}</tbody></table>`;
}

// ═══ Performance ═══
async function loadPerformance() {
  const data = await apiFetch('/api/performance');
  if (!data) return;
  document.getElementById('perf-stats').innerHTML = `
    <div class="stat-box"><div class="stat-value text-cyan">${data.total_trades||0}</div><div class="stat-label">Total Trades</div></div>
    <div class="stat-box"><div class="stat-value ${(data.total_pnl||0)>=0?'text-green':'text-red'}">$${(data.total_pnl||0).toFixed(2)}</div><div class="stat-label">Total P&L</div></div>
    <div class="stat-box"><div class="stat-value text-amber">${(data.win_rate||0)}%</div><div class="stat-label">Win Rate</div></div>
    <div class="stat-box"><div class="stat-value text-indigo">${(data.profit_factor||0)}x</div><div class="stat-label">Profit Factor</div></div>`;
  const trades = data.recent_trades || [];
  document.getElementById('perf-trades').innerHTML = trades.length === 0
    ? '<p style="color:var(--text-muted);text-align:center;padding:40px;">No completed trades yet</p>'
    : `<table class="data-table"><thead><tr><th>Ticker</th><th>Direction</th><th>Entry</th><th>Exit</th><th>P&L</th></tr></thead><tbody>
      ${trades.map(t => `<tr><td class="ticker">${t.ticker}</td><td>${t.direction}</td><td class="price">$${t.entry_price}</td><td class="price">$${t.exit_price}</td>
      <td style="color:${(t.pnl||0)>=0?'var(--green)':'var(--red)'}">$${(t.pnl||0).toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

// ═══ Init ═══
document.addEventListener('DOMContentLoaded', () => {
  refreshTop25();
  loadGlobalNews();
  loadMacro();
});

// ═══ Autobot ═══
async function loadBotDashboard() {
  const container = document.getElementById('bot-platforms-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span class="loading-text">Loading top 100 platforms...</span></div>`;
  const data = await apiFetch('/api/bot/dashboard');
  if (!data) return;
  
  container.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Rank</th><th>Name</th><th>Type</th><th>Reliability</th><th>Rating</th><th>API Supported</th></tr></thead>
      <tbody>
        ${(data.platforms || []).map(p => `
          <tr>
            <td style="color:var(--text-muted)">${p.rank}</td>
            <td class="platform-name font-bold">${p.name}</td>
            <td class="platform-type">${p.type}</td>
            <td style="color:var(--text-secondary)">${p.reliability}</td>
            <td class="platform-rating font-bold text-amber">★ ${p.rating}</td>
            <td><span class="card-badge badge-${p.api ? 'bullish' : 'neutral'}">${p.api ? 'YES' : 'NO'}</span></td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}

async function connectEtoro() {
  const statusDiv = document.getElementById('bot-etoro-status');
  statusDiv.innerHTML = `Connecting to eToro Network Simulator...`;
  const data = await fetch(`${API}/api/bot/etoro/connect`, { method: 'POST' }).then(r => r.json()).catch(e => null);
  if (!data) {
    statusDiv.innerHTML = `<span class="text-red">Connection failed. Check backend connection.</span>`;
    return;
  }
  statusDiv.innerHTML = `<span class="text-green">✅ ${data.message} | Acct: ${data.account_id} | Bal: $${data.balance}</span>`;
}

async function executeBotTrade() {
  const logDiv = document.getElementById('bot-execution-log');
  logDiv.style.display = 'block';
  logDiv.innerHTML = `Bot is scanning global news and evaluating top 25 rankings...`;
  
  const data = await fetch(`${API}/api/bot/execute`, { method: 'POST' }).then(r => r.json()).catch(e => null);
  if (!data) {
    logDiv.innerHTML += `<br><span class="text-red">Execution failed. Check backend connection.</span>`;
    return;
  }
  
  const ev = data.evaluation || {};
  const ds = ev.decision || {};
  const t = data.execution || {};
  
  logDiv.innerHTML = `
    <div style="margin-bottom: 8px;"><strong class="text-cyan">Analysis Complete</strong></div>
    <div>Target: ${ev.candidate}</div>
    <div>Sentiment Score: ${ev.overall_sentiment?.aggregate_score?.toFixed(3) || 0}</div>
    <div>Decision: <span class="${ds.action === 'BUY' ? 'text-green' : 'text-red'}">${ds.action}</span> for $${ds.amount}</div>
    <div>Reason: ${ds.reasoning}</div>
    <div style="margin-top: 15px; margin-bottom: 8px;"><strong class="text-indigo">Execution Report</strong></div>
    ${t.status === 'success' 
      ? `<div>Status: <span class="text-green">SUCCESS</span> (Trade ID: ${t.trade_id})</div>
         <div>Executed ${t.action} on ${t.ticker} for $${t.executed_amount}. TP: ${t.take_profit_set}, SL: ${t.stop_loss_set}</div>`
      : `<div class="text-red">Status: FAILED - ${t.message || 'Unknown error'}</div>`
    }
  `;
}

// Auto-refresh every 60 seconds
setInterval(() => {
  if (document.querySelector('[data-tab="command"].active')) {
    refreshTop25();
    loadGlobalNews();
  }
}, 60000);
