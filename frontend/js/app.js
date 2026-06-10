/**
 * app.js — Lógica principal do App Rotina Bebê 🍼
 * Gerencia navegação de datas, cards e interações com a API.
 */
import { api } from './api.js';

// ── Estado global ────────────────────────────────────────────────────────────
let currentDate = new Date();
let activeSleepId = null;

// ── Utilitários de data ───────────────────────────────────────────────────────
function toISODate(d) {
  return d.toISOString().split('T')[0];
}

function formatDate(d) {
  return d.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
}

function formatTime(isoStr) {
  if (!isoStr) return '--:--';
  const d = new Date(isoStr);
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function toLocalISOStringWithOffset(d) {
  const tzo = -d.getTimezoneOffset();
  const dif = tzo >= 0 ? '+' : '-';
  const pad = (num) => (num < 10 ? '0' : '') + num;
  return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
    'T' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds()) +
    dif + pad(Math.floor(Math.abs(tzo) / 60)) + ':' + pad(Math.abs(tzo) % 60);
}

function formatDuration(minutes) {
  if (!minutes && minutes !== 0) return '—';
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return h > 0 ? `${h}h ${m}min` : `${m}min`;
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 2600);
}

// ── Navegação de datas ────────────────────────────────────────────────────────
function updateDateLabel() {
  document.getElementById('current-date-label').textContent = formatDate(currentDate);
}

function navigate(delta) {
  currentDate.setDate(currentDate.getDate() + delta);
  updateDateLabel();
  loadAll();
}

// ── Loader de botão ───────────────────────────────────────────────────────────
async function withLoading(btn, fn) {
  const original = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>';
  try {
    await fn();
  } finally {
    btn.disabled = false;
    btn.innerHTML = original;
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  CARD: AMAMENTAÇÃO 🍼
// ════════════════════════════════════════════════════════════════════════════

let selectedMlOffered = null;
let selectedMlConsumed = null;

function setupFeedingCard() {
  // Toggles do form de mamadeira
  document.getElementById('btn-bottle').addEventListener('click', () => {
    const form = document.getElementById('ml-form');
    form.classList.toggle('visible');
  });

  // Chips de ML ofertados
  document.querySelectorAll('#chips-offered .ml-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#chips-offered .ml-chip').forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
      selectedMlOffered = parseInt(chip.dataset.ml);
      document.getElementById('ml-offered-input').value = selectedMlOffered;
    });
  });

  // Chips de ML consumidos
  document.querySelectorAll('#chips-consumed .ml-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#chips-consumed .ml-chip').forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
      selectedMlConsumed = parseInt(chip.dataset.ml);
      document.getElementById('ml-consumed-input').value = selectedMlConsumed;
    });
  });

  // Input manual sincroniza chip
  document.getElementById('ml-offered-input').addEventListener('input', e => {
    selectedMlOffered = parseInt(e.target.value) || null;
    syncChips('#chips-offered', selectedMlOffered);
  });

  document.getElementById('ml-consumed-input').addEventListener('input', e => {
    selectedMlConsumed = parseInt(e.target.value) || null;
    syncChips('#chips-consumed', selectedMlConsumed);
  });

  // Confirmar mamadeira
  document.getElementById('btn-bottle-confirm').addEventListener('click', async (e) => {
    const mlOffered = parseInt(document.getElementById('ml-offered-input').value);
    const mlConsumed = parseInt(document.getElementById('ml-consumed-input').value) || null;

    if (!mlOffered || mlOffered <= 0) {
      toast('Informe quantos ML foram ofertados!', 'error');
      return;
    }

    await withLoading(e.target, async () => {
      await api.feeding.create({ feeding_type: 'bottle', ml_offered: mlOffered, ml_consumed: mlConsumed });
      toast(`✅ Mamadeira ${mlOffered}ml registrada!`);
      resetBottleForm();
      await loadFeeding();
    });
  });

  // Breast esquerdo
  document.getElementById('btn-Breast-left').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      await api.feeding.create({ feeding_type: 'Breast', breast_side: 'left' });
      toast('✅ Peito esquerdo registrado!');
      await loadFeeding();
    });
  });

  // Breast direito
  document.getElementById('btn-Breast-right').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      await api.feeding.create({ feeding_type: 'Breast', breast_side: 'right' });
      toast('✅ Peito direito registrado!');
      await loadFeeding();
    });
  });

  // Ambos os Breasts
  document.getElementById('btn-Breast-both').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      await api.feeding.create({ feeding_type: 'Breast', breast_side: 'both' });
      toast('✅ Ambos os peitos registrados!');
      await loadFeeding();
    });
  });
}

function syncChips(selector, value) {
  document.querySelectorAll(`${selector} .ml-chip`).forEach(c => {
    c.classList.toggle('selected', parseInt(c.dataset.ml) === value);
  });
}

function resetBottleForm() {
  document.getElementById('ml-offered-input').value = '';
  document.getElementById('ml-consumed-input').value = '';
  document.querySelectorAll('.ml-chip').forEach(c => c.classList.remove('selected'));
  document.getElementById('ml-form').classList.remove('visible');
  selectedMlOffered = null;
  selectedMlConsumed = null;
}

async function loadFeeding() {
  const dateStr = toISODate(currentDate);
  const records = await api.feeding.list(dateStr);
  const list = document.getElementById('feeding-list');
  const badge = document.getElementById('feeding-badge');

  badge.textContent = records.length;

  if (records.length === 0) {
    list.innerHTML = '<p class="empty-state">Nenhum registro hoje 🍼</p>';
    return;
  }

  list.innerHTML = records.map(r => {
    let icon, detail;
    if (r.feeding_type === 'bottle') {
      icon = '🍼';
      const consumed = r.ml_consumed != null ? `/${r.ml_consumed}ml` : '';
      detail = `Mamadeira ${r.ml_offered}ml${consumed}`;
    } else {
      const sideMap = { left: 'Peito Esquerdo 🤱', right: 'Peito Direito 🤱', both: 'Ambos os Peitos 🤱' };
      icon = '🤱';
      detail = sideMap[r.breast_side] || 'Peito';
    }
    return `
      <div class="record-item" id="feed-${r.id}">
        <span class="record-icon">${icon}</span>
        <div class="record-info">
          <div class="record-time">
            ${formatTime(r.recorded_at)} 
            <button class="record-edit-btn" onclick="editFeeding(${r.id}, '${r.recorded_at}')" title="Editar horário">✏️</button>
          </div>
          <div class="record-detail">${detail}</div>
        </div>
        <button class="record-delete" onclick="deleteFeed(${r.id})" title="Remover">✕</button>
      </div>
    `;
  }).join('');
}

window.editFeeding = async (id, currentIsoStr) => {
  const currentFormatted = formatTime(currentIsoStr);
  const newTime = prompt('Alterar horário (formato HH:MM):', currentFormatted);
  if (!newTime || newTime === currentFormatted) return;

  const regex = /^([01]\d|2[0-3]):([0-5]\d)$/;
  if (!regex.test(newTime)) return toast('Formato inválido! Use HH:MM (ex: 14:30)', 'error');

  const updatedDateTime = new Date(currentIsoStr);
  const [hours, minutes] = newTime.split(':');
  updatedDateTime.setHours(parseInt(hours), parseInt(minutes));

  try {
    await api.feeding.update(id, { recorded_at: toLocalISOStringWithOffset(updatedDateTime) });
    toast('Horário atualizado com sucesso!');
    await loadFeeding();
    await updateSummary();
  } catch (err) {
    toast(err.message, 'error');
  }
};

window.deleteFeed = async (id) => {
  if (!confirm('Remover este registro?')) return;
  await api.feeding.delete(id);
  toast('Registro removido', 'success');
  await loadFeeding();
  await updateSummary();
};

// ════════════════════════════════════════════════════════════════════════════
//  CARD: TROCA DE FRALDA 👶
// ════════════════════════════════════════════════════════════════════════════

function setupDiaperCard() {
  document.getElementById('btn-diaper-pee').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      await api.diaper.create({ has_pee: true, has_poop: false });
      toast('✅ Xixi registrado! 💧');
      await loadDiapers();
    });
  });

  document.getElementById('btn-diaper-poop').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      await api.diaper.create({ has_pee: false, has_poop: true });
      toast('✅ Cocô registrado! 💩');
      await loadDiapers();
    });
  });

  document.getElementById('btn-diaper-both').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      await api.diaper.create({ has_pee: true, has_poop: true });
      toast('✅ Xixi + Cocô registrado!');
      await loadDiapers();
    });
  });
}

async function loadDiapers() {
  const dateStr = toISODate(currentDate);
  const records = await api.diaper.list(dateStr);
  const list = document.getElementById('diaper-list');
  const badge = document.getElementById('diaper-badge');

  badge.textContent = records.length;

  if (records.length === 0) {
    list.innerHTML = '<p class="empty-state">Nenhuma troca hoje 👶</p>';
    return;
  }

  list.innerHTML = records.map(r => {
    let icon = r.has_poop ? '💩' : '💧';
    let detail = [];
    if (r.has_pee) detail.push('Xixi 💧');
    if (r.has_poop) detail.push('Cocô 💩');
    return `
      <div class="record-item" id="diaper-${r.id}">
        <span class="record-icon">${icon}</span>
        <div class="record-info">
          <div class="record-time">
            ${formatTime(r.recorded_at)}
            <button class="record-edit-btn" onclick="editDiaper(${r.id}, '${r.recorded_at}')" title="Editar horário">✏️</button>
          </div>
          <div class="record-detail">${detail.join(' + ')}</div>
        </div>
        <button class="record-delete" onclick="deleteDiaper(${r.id})" title="Remover">✕</button>
      </div>
    `;
  }).join('');
}

window.editDiaper = async (id, currentIsoStr) => {
  const currentFormatted = formatTime(currentIsoStr);
  const newTime = prompt('Alterar horário (formato HH:MM):', currentFormatted);
  if (!newTime || newTime === currentFormatted) return;

  const regex = /^([01]\d|2[0-3]):([0-5]\d)$/;
  if (!regex.test(newTime)) return toast('Formato inválido! Use HH:MM', 'error');

  const updatedDateTime = new Date(currentIsoStr);
  const [hours, minutes] = newTime.split(':');
  updatedDateTime.setHours(parseInt(hours), parseInt(minutes));

  try {
    await api.diaper.update(id, { recorded_at: toLocalISOStringWithOffset(updatedDateTime) });
    toast('Horário da troca atualizado!');
    await loadDiapers();
    await updateSummary();
  } catch (err) {
    toast(err.message, 'error');
  }
};

window.deleteDiaper = async (id) => {
  if (!confirm('Remover esta troca?')) return;
  await api.diaper.delete(id);
  toast('Troca removida', 'success');
  await loadDiapers();
  await updateSummary();
};

// ════════════════════════════════════════════════════════════════════════════
//  CARD: SONO 😴
// ════════════════════════════════════════════════════════════════════════════

function setupSleepCard() {
  document.getElementById('btn-sleep-start').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      const record = await api.sleep.start();
      activeSleepId = record.id;
      toast('😴 Hora de nanar! Soninho iniciado.');
      updateSleepUI(true);
      await loadSleeps();
    });
  });

  document.getElementById('btn-sleep-end').addEventListener('click', async (e) => {
    if (!activeSleepId) return;
    await withLoading(e.target, async () => {
      const record = await api.sleep.end(activeSleepId);
      const dur = formatDuration(record.duration_min);
      activeSleepId = null;
      toast(`☀️ Acordou! Dormiu ${dur}.`);
      updateSleepUI(false);
      await loadSleeps();
    });
  });
}

function updateSleepUI(isActive) {
  document.getElementById('btn-sleep-start').style.display = isActive ? 'none' : 'flex';
  document.getElementById('btn-sleep-end').style.display = isActive ? 'flex' : 'none';
  const indicator = document.getElementById('sleep-active-indicator');
  indicator.classList.toggle('visible', isActive);
}

async function loadSleeps() {
  const dateStr = toISODate(currentDate);
  const records = await api.sleep.list(dateStr);
  const list = document.getElementById('sleep-list');
  const badge = document.getElementById('sleep-badge');

  badge.textContent = records.length;

  if (records.length === 0) {
    list.innerHTML = '<p class="empty-state">Nenhum sono registrado 😴</p>';
    return;
  }

  list.innerHTML = records.map(r => {
    const start = formatTime(r.start_time);
    const end = r.end_time ? formatTime(r.end_time) : '...';
    const dur = r.duration_min != null ? formatDuration(r.duration_min) : '⏳ em andamento';
    const icon = r.is_active ? '🌙' : '☀️';
    return `
      <div class="record-item" id="sleep-${r.id}">
        <span class="record-icon">${icon}</span>
        <div class="record-info">
          <div class="record-time">
            ${start} → ${end}
            <button class="record-edit-btn" onclick="editSleep(${r.id}, '${r.start_time}', ${r.end_time ? `'${r.end_time}'` : 'null'})" title="Editar horários">✏️</button>
          </div>
          <div class="record-detail">${dur}</div>
        </div>
        <button class="record-delete" onclick="deleteSleep(${r.id})" title="Remover">✕</button>
      </div>
    `;
  }).join('');
}

window.editSleep = async (id, startIsoStr, endIsoStr) => {
  const regex = /^([01]\d|2[0-3]):([0-5]\d)$/;
  const payload = {};

  // 1. Edição do Horário de Início
  const startFormatted = formatTime(startIsoStr);
  const newStartTime = prompt('Alterar horário de INÍCIO (HH:MM):', startFormatted);

  if (newStartTime && newStartTime !== startFormatted) {
    if (!regex.test(newStartTime)) return toast('Formato inválido para início!', 'error');
    const updatedStart = new Date(startIsoStr);
    const [h, m] = newStartTime.split(':');
    updatedStart.setHours(parseInt(h), parseInt(m));
    payload.start_time = toLocalISOStringWithOffset(updatedStart);
  }

  // 2. Edição do Horário de Fim (Se houver)
  if (endIsoStr) {
    const endFormatted = formatTime(endIsoStr);
    const newEndTime = prompt('Alterar horário de TÉRMINO (HH:MM):', endFormatted);

    if (newEndTime && newEndTime !== endFormatted) {
      if (!regex.test(newEndTime)) return toast('Formato inválido para término!', 'error');
      const updatedEnd = new Date(endIsoStr);
      const [h, m] = newEndTime.split(':');
      updatedEnd.setHours(parseInt(h), parseInt(m));
      payload.end_time = toLocalISOStringWithOffset(updatedEnd);
    }
  }

  if (Object.keys(payload).length === 0) return;

  try {
    await api.sleep.update(id, payload);
    toast('Horários do sono atualizados!');
    await loadSleeps();
    await updateSummary();
  } catch (err) {
    toast(err.message, 'error');
  }
};

window.deleteSleep = async (id) => {
  if (!confirm('Remover este sono?')) return;
  await api.sleep.delete(id);
  if (activeSleepId === id) {
    activeSleepId = null;
    updateSleepUI(false);
  }
  toast('Sono removido', 'success');
  await loadSleeps();
  await updateSummary();
};

// ════════════════════════════════════════════════════════════════════════════
//  CARD: BANHO 🛁
// ════════════════════════════════════════════════════════════════════════════

function setupBathCard() {
  document.getElementById('btn-bath').addEventListener('click', async (e) => {
    await withLoading(e.target, async () => {
      await api.bath.create();
      toast('🛁 Banho registrado!');
      await loadBaths();
    });
  });
}

async function loadBaths() {
  const dateStr = toISODate(currentDate);
  const records = await api.bath.list(dateStr);
  const list = document.getElementById('bath-list');
  const badge = document.getElementById('bath-badge');

  badge.textContent = records.length;

  if (records.length === 0) {
    list.innerHTML = '<p class="empty-state">Nenhum banho hoje 🛁</p>';
    return;
  }

  list.innerHTML = records.map(r => `
    <div class="record-item" id="bath-${r.id}">
      <span class="record-icon">🛁</span>
      <div class="record-info">
        <div class="record-time">
          ${formatTime(r.recorded_at)}
          <button class="record-edit-btn" onclick="editBath(${r.id}, '${r.recorded_at}')" title="Editar horário">✏️</button>
        </div>
        <div class="record-detail">Banho registrado</div>
      </div>
      <button class="record-delete" onclick="deleteBath(${r.id})" title="Remover">✕</button>
    </div>
  `).join('');
}

window.editBath = async (id, currentIsoStr) => {
  const currentFormatted = formatTime(currentIsoStr);
  const newTime = prompt('Alterar horário do banho (formato HH:MM):', currentFormatted);
  if (!newTime || newTime === currentFormatted) return;

  const regex = /^([01]\d|2[0-3]):([0-5]\d)$/;
  if (!regex.test(newTime)) return toast('Formato inválido! Use HH:MM', 'error');

  const updatedDateTime = new Date(currentIsoStr);
  const [hours, minutes] = newTime.split(':');
  updatedDateTime.setHours(parseInt(hours), parseInt(minutes));

  try {
    await api.bath.update(id, { recorded_at: toLocalISOStringWithOffset(updatedDateTime) });
    toast('Horário do banho atualizado!');
    await loadBaths();
  } catch (err) {
    toast(err.message, 'error');
  }
};

window.deleteBath = async (id) => {
  if (!confirm('Remover este banho?')) return;
  await api.bath.delete(id);
  toast('Banho removido', 'success');
  await loadBaths();
};

// ════════════════════════════════════════════════════════════════════════════
//  RESUMO DO DIA
// ════════════════════════════════════════════════════════════════════════════

async function updateSummary() {
  try {
    const s = await api.summary(toISODate(currentDate));
    document.getElementById('sum-ml-offered').textContent = `${s.total_ml_offered}ml`;
    document.getElementById('sum-ml-consumed').textContent = `${s.total_ml_consumed}ml`;
    document.getElementById('sum-breast').textContent = s.total_breast_feedings;
    document.getElementById('sum-diapers').textContent = s.total_diaper_changes;
    document.getElementById('sum-sleep').textContent = formatDuration(s.total_sleep_min);
  } catch {
    // silencia erros de summary (não crítico)
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  LOAD ALL
// ════════════════════════════════════════════════════════════════════════════

async function loadAll() {
  await Promise.all([
    loadFeeding(),
    loadDiapers(),
    loadSleeps(),
    loadBaths(),
    updateSummary(),
  ]);

  // Verifica sono ativo
  const active = await api.sleep.active();
  if (active && active.id) {
    activeSleepId = active.id;
    updateSleepUI(true);
  } else {
    activeSleepId = null;
    updateSleepUI(false);
  }
}

function setupToggleButtons() {
  document.querySelectorAll('.toggle-records-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const targetId = btn.getAttribute('data-target');
      const targetList = document.getElementById(targetId);
      if (targetList.style.display === 'none') {
        targetList.style.display = 'flex';
        btn.textContent = '▼';
        btn.style.opacity = '1';
      } else {
        targetList.style.display = 'none';
        btn.textContent = '◀';
        btn.style.opacity = '0.5';
      }
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
//  RELATÓRIOS 📊
// ════════════════════════════════════════════════════════════════════════════

let rawReports = [];

async function loadReports() {
  const tbody = document.getElementById('report-tbody');
  tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Carregando relatórios...</td></tr>';
  try {
    rawReports = await api.reports.history();
    renderReports();
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-state">Erro: ${err.message}</td></tr>`;
  }
}

function renderReports() {
  const filter = document.getElementById('report-filter').value;
  const tbody = document.getElementById('report-tbody');

  if (rawReports.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Nenhum registro encontrado.</td></tr>';
    return;
  }

  let aggregated = [];

  if (filter === 'all') {
    aggregated = rawReports.map(r => ({
      label: new Date(r.date + 'T12:00:00').toLocaleDateString('pt-BR'),
      ...r
    }));
  } else if (filter === 'month') {
    const map = {};
    rawReports.forEach(r => {
      const d = new Date(r.date + 'T12:00:00');
      const label = d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
      if (!map[label]) {
        map[label] = { label, total_ml_offered: 0, total_ml_consumed: 0, total_diaper_changes: 0, total_sleep_min: 0, total_baths: 0, total_breast_feedings: 0, sortKey: d.getTime() };
      }
      map[label].total_ml_offered += r.total_ml_offered;
      map[label].total_ml_consumed += r.total_ml_consumed;
      map[label].total_diaper_changes += r.total_diaper_changes;
      map[label].total_sleep_min += r.total_sleep_min;
      map[label].total_baths += r.total_baths;
      map[label].total_breast_feedings += r.total_breast_feedings;
    });
    aggregated = Object.values(map).sort((a, b) => b.sortKey - a.sortKey);
  } else if (filter === 'year') {
    const map = {};
    rawReports.forEach(r => {
      const d = new Date(r.date + 'T12:00:00');
      const label = d.getFullYear().toString();
      if (!map[label]) {
        map[label] = { label, total_ml_offered: 0, total_ml_consumed: 0, total_diaper_changes: 0, total_sleep_min: 0, total_baths: 0, total_breast_feedings: 0, sortKey: d.getFullYear() };
      }
      map[label].total_ml_offered += r.total_ml_offered;
      map[label].total_ml_consumed += r.total_ml_consumed;
      map[label].total_diaper_changes += r.total_diaper_changes;
      map[label].total_sleep_min += r.total_sleep_min;
      map[label].total_baths += r.total_baths;
      map[label].total_breast_feedings += r.total_breast_feedings;
    });
    aggregated = Object.values(map).sort((a, b) => b.sortKey - a.sortKey);
  }

  tbody.innerHTML = aggregated.map(r => `
    <tr>
      <td>${r.label}</td>
      <td>${r.total_breast_feedings}</td>
      <td>${r.total_ml_offered}ml / ${r.total_ml_consumed}ml</td>
      <td>${r.total_diaper_changes}</td>
      <td>${formatDuration(r.total_sleep_min)}</td>
      <td>${r.total_baths}</td>
    </tr>
  `).join('');
}

// ════════════════════════════════════════════════════════════════════════════
//  TABS E NAVEGAÇÃO
// ════════════════════════════════════════════════════════════════════════════

function setupTabs() {
  const tabDaily = document.getElementById('tab-daily');
  const tabReports = document.getElementById('tab-reports');
  const viewDaily = document.getElementById('view-daily');
  const viewReports = document.getElementById('view-reports');

  tabDaily.addEventListener('click', () => {
    tabDaily.classList.add('active');
    tabReports.classList.remove('active');
    viewDaily.classList.add('active');
    viewReports.classList.remove('active');
    document.querySelector('.app-header').style.display = 'block'; // mostra controle de data
  });

  tabReports.addEventListener('click', () => {
    tabReports.classList.add('active');
    tabDaily.classList.remove('active');
    viewReports.classList.add('active');
    viewDaily.classList.remove('active');
    document.querySelector('.app-header').style.display = 'none'; // oculta controle de data
    loadReports();
  });

  document.getElementById('report-filter').addEventListener('change', renderReports);
}


// ════════════════════════════════════════════════════════════════════════════
//  INICIALIZAÇÃO
// ════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
  updateDateLabel();
  setupTabs();
  setupToggleButtons();

  // Navegação de datas
  document.getElementById('btn-prev-day').addEventListener('click', () => navigate(-1));
  document.getElementById('btn-next-day').addEventListener('click', () => navigate(1));

  // Date picker nativo via click no label
  const picker = document.getElementById('date-picker-input');
  document.getElementById('current-date-label').addEventListener('click', () => {
    picker.value = toISODate(currentDate);
    picker.showPicker?.();
    picker.click();
  });
  picker.addEventListener('change', (e) => {
    if (e.target.value) {
      currentDate = new Date(e.target.value + 'T12:00:00');
      updateDateLabel();
      loadAll();
    }
  });

  // Setup dos cards
  setupFeedingCard();
  setupDiaperCard();
  setupSleepCard();
  setupBathCard();

  // Carrega dados do dia
  await loadAll();
});