/**
 * api.js — Funções de comunicação com o backend FastAPI.
 */

const BASE = '';  // Mesmo host (FastAPI serve frontend)

async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });

    if (res.status === 204) return null;

    const data = await res.json();

    if (!res.ok) {
      const msg = data?.detail || `Erro ${res.status}`;
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError') {
      throw new Error('Não foi possível conectar ao servidor. O app está rodando?');
    }
    throw err;
  }
}

// ── API Modules ──────────────────────────────────────────────────────────────
export const api = {
  // Amamentação
  feeding: {
    create: (payload) => apiFetch('/api/feeding', { method: 'POST', body: JSON.stringify(payload) }),
    list:   (date)    => apiFetch(`/api/feeding?date=${date}`),
    update: (id, payload) => apiFetch(`/api/feeding/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
    delete: (id)      => apiFetch(`/api/feeding/${id}`, { method: 'DELETE' }),
  },

  // Troca de fralda
  diaper: {
    create: (payload) => apiFetch('/api/diaper', { method: 'POST', body: JSON.stringify(payload) }),
    list:   (date)    => apiFetch(`/api/diaper?date=${date}`),
    update: (id, payload) => apiFetch(`/api/diaper/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
    delete: (id)      => apiFetch(`/api/diaper/${id}`, { method: 'DELETE' }),
  },

  // Sono
  sleep: {
    start:  ()            => apiFetch('/api/sleep/start', { method: 'POST' }),
    end:    (id)          => apiFetch(`/api/sleep/${id}/end`, { method: 'PATCH' }),
    list:   (date)        => apiFetch(`/api/sleep?date=${date}`),
    active: ()            => apiFetch('/api/sleep/active'),
    update: (id, payload) => apiFetch(`/api/sleep/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
    delete: (id)          => apiFetch(`/api/sleep/${id}`, { method: 'DELETE' }),
  },

  // Banho
  bath: {
    create: ()            => apiFetch('/api/bath', { method: 'POST' }),
    list:   (date)        => apiFetch(`/api/bath?date=${date}`),
    update: (id, payload) => apiFetch(`/api/bath/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
    delete: (id)          => apiFetch(`/api/bath/${id}`, { method: 'DELETE' }),
  },

  // Resumo do dia
  summary: (date) => apiFetch(`/api/summary?date=${date}`),

  // Relatórios
  reports: {
    history: () => apiFetch('/api/reports/history'),
  }
};


