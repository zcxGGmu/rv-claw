import { test, expect } from '@playwright/test';

const API_BASE = 'http://localhost:12001';

test.describe('Backend API Health & Connectivity', () => {
  test('health endpoint returns healthy', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.status).toBe('healthy');
    expect(body.checks).toHaveProperty('mongodb');
    expect(body.checks).toHaveProperty('postgres');
    expect(body.checks).toHaveProperty('redis');
  });

  test('ready endpoint returns ready', async ({ request }) => {
    const response = await request.get(`${API_BASE}/ready`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.status).toBe('ready');
  });

  test('auth status returns unauthenticated without token', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/v1/auth/status`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.code).toBe(0);
    expect(body.data.authenticated).toBe(false);
  });

  test('API wrapper format is consistent', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/v1/auth/status`);
    const body = await response.json();
    expect(body).toHaveProperty('code');
    expect(body).toHaveProperty('msg');
    expect(body).toHaveProperty('data');
    expect(typeof body.code).toBe('number');
    expect(typeof body.msg).toBe('string');
  });
});

test.describe('Authentication API', () => {
  test('login with default admin succeeds', async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/v1/auth/login`, {
      data: { username: 'admin', password: 'admin123' },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.code).toBe(0);
    expect(body.data).toHaveProperty('access_token');
    expect(body.data).toHaveProperty('refresh_token');
    expect(body.data.user).toHaveProperty('fullname');
  });

  test('login with invalid credentials fails', async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/v1/auth/login`, {
      data: { username: 'admin', password: 'wrongpassword' },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.code).toBe(401);
  });

  test('me endpoint requires authentication', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/v1/auth/me`);
    expect(response.status()).toBe(401);
  });

  test('full auth lifecycle', async ({ request }) => {
    const loginRes = await request.post(`${API_BASE}/api/v1/auth/login`, {
      data: { username: 'admin', password: 'admin123' },
    });
    expect(loginRes.ok()).toBeTruthy();
    const loginBody = await loginRes.json();
    const accessToken = loginBody.data.access_token;

    const meRes = await request.get(`${API_BASE}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(meRes.ok()).toBeTruthy();
    const meBody = await meRes.json();
    expect(meBody.data.fullname).toBeTruthy();

    const logoutRes = await request.post(`${API_BASE}/api/v1/auth/logout`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(logoutRes.ok()).toBeTruthy();
  });
});

test.describe('Sessions API', () => {
  let accessToken: string;

  test.beforeAll(async ({ request }) => {
    const res = await request.post(`${API_BASE}/api/v1/auth/login`, {
      data: { username: 'admin', password: 'admin123' },
    });
    const body = await res.json();
    accessToken = body.data.access_token;
  });

  test('create and list sessions', async ({ request }) => {
    const createRes = await request.put(`${API_BASE}/api/v1/sessions`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { mode: 'deep' },
    });
    expect(createRes.ok()).toBeTruthy();
    const createBody = await createRes.json();
    expect(createBody.code).toBe(0);
    expect(createBody.data).toHaveProperty('session_id');

    const listRes = await request.get(`${API_BASE}/api/v1/sessions`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(listRes.ok()).toBeTruthy();
    const listBody = await listRes.json();
    expect(listBody.code).toBe(0);
    expect(Array.isArray(listBody.data.sessions)).toBe(true);
  });
});

test.describe('Cases API', () => {
  let accessToken: string;

  test.beforeAll(async ({ request }) => {
    const res = await request.post(`${API_BASE}/api/v1/auth/login`, {
      data: { username: 'admin', password: 'admin123' },
    });
    const body = await res.json();
    accessToken = body.data.access_token;
  });

  test('create and list cases', async ({ request }) => {
    const createRes = await request.post(`${API_BASE}/api/v1/cases`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { target_repo: 'riscv/riscv-isa-manual', input_context: { arch: 'RV64I' } },
    });
    expect(createRes.ok()).toBeTruthy();
    const createBody = await createRes.json();
    expect(createBody.code).toBe(0);
    expect(createBody.data).toHaveProperty('id');
    expect(createBody.data.status).toBe('pending');

    const listRes = await request.get(`${API_BASE}/api/v1/cases`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(listRes.ok()).toBeTruthy();
    const listBody = await listRes.json();
    expect(listBody.code).toBe(0);
    expect(Array.isArray(listBody.data.cases)).toBe(true);
  });
});
