# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: api-health.spec.ts >> Sessions API >> create and list sessions
- Location: e2e/api-health.spec.ts:102:3

# Error details

```
Error: expect(received).toBeTruthy()

Received: false
```

# Test source

```ts
  7   |     const response = await request.get(`${API_BASE}/health`);
  8   |     expect(response.ok()).toBeTruthy();
  9   |     const body = await response.json();
  10  |     expect(body.status).toBe('healthy');
  11  |     expect(body.checks).toHaveProperty('mongodb');
  12  |     expect(body.checks).toHaveProperty('postgres');
  13  |     expect(body.checks).toHaveProperty('redis');
  14  |   });
  15  | 
  16  |   test('ready endpoint returns ready', async ({ request }) => {
  17  |     const response = await request.get(`${API_BASE}/ready`);
  18  |     expect(response.ok()).toBeTruthy();
  19  |     const body = await response.json();
  20  |     expect(body.status).toBe('ready');
  21  |   });
  22  | 
  23  |   test('auth status returns unauthenticated without token', async ({ request }) => {
  24  |     const response = await request.get(`${API_BASE}/api/v1/auth/status`);
  25  |     expect(response.ok()).toBeTruthy();
  26  |     const body = await response.json();
  27  |     expect(body.code).toBe(0);
  28  |     expect(body.data.authenticated).toBe(false);
  29  |   });
  30  | 
  31  |   test('API wrapper format is consistent', async ({ request }) => {
  32  |     const response = await request.get(`${API_BASE}/api/v1/auth/status`);
  33  |     const body = await response.json();
  34  |     expect(body).toHaveProperty('code');
  35  |     expect(body).toHaveProperty('msg');
  36  |     expect(body).toHaveProperty('data');
  37  |     expect(typeof body.code).toBe('number');
  38  |     expect(typeof body.msg).toBe('string');
  39  |   });
  40  | });
  41  | 
  42  | test.describe('Authentication API', () => {
  43  |   test('login with default admin succeeds', async ({ request }) => {
  44  |     const response = await request.post(`${API_BASE}/api/v1/auth/login`, {
  45  |       data: { username: 'admin', password: 'admin123' },
  46  |     });
  47  |     expect(response.ok()).toBeTruthy();
  48  |     const body = await response.json();
  49  |     expect(body.code).toBe(0);
  50  |     expect(body.data).toHaveProperty('access_token');
  51  |     expect(body.data).toHaveProperty('refresh_token');
  52  |     expect(body.data.user).toHaveProperty('fullname');
  53  |   });
  54  | 
  55  |   test('login with invalid credentials fails', async ({ request }) => {
  56  |     const response = await request.post(`${API_BASE}/api/v1/auth/login`, {
  57  |       data: { username: 'admin', password: 'wrongpassword' },
  58  |     });
  59  |     expect(response.ok()).toBeTruthy();
  60  |     const body = await response.json();
  61  |     expect(body.code).toBe(401);
  62  |   });
  63  | 
  64  |   test('me endpoint requires authentication', async ({ request }) => {
  65  |     const response = await request.get(`${API_BASE}/api/v1/auth/me`);
  66  |     expect(response.status()).toBe(401);
  67  |   });
  68  | 
  69  |   test('full auth lifecycle', async ({ request }) => {
  70  |     const loginRes = await request.post(`${API_BASE}/api/v1/auth/login`, {
  71  |       data: { username: 'admin', password: 'admin123' },
  72  |     });
  73  |     expect(loginRes.ok()).toBeTruthy();
  74  |     const loginBody = await loginRes.json();
  75  |     const accessToken = loginBody.data.access_token;
  76  | 
  77  |     const meRes = await request.get(`${API_BASE}/api/v1/auth/me`, {
  78  |       headers: { Authorization: `Bearer ${accessToken}` },
  79  |     });
  80  |     expect(meRes.ok()).toBeTruthy();
  81  |     const meBody = await meRes.json();
  82  |     expect(meBody.data.fullname).toBeTruthy();
  83  | 
  84  |     const logoutRes = await request.post(`${API_BASE}/api/v1/auth/logout`, {
  85  |       headers: { Authorization: `Bearer ${accessToken}` },
  86  |     });
  87  |     expect(logoutRes.ok()).toBeTruthy();
  88  |   });
  89  | });
  90  | 
  91  | test.describe('Sessions API', () => {
  92  |   let accessToken: string;
  93  | 
  94  |   test.beforeAll(async ({ request }) => {
  95  |     const res = await request.post(`${API_BASE}/api/v1/auth/login`, {
  96  |       data: { username: 'admin', password: 'admin123' },
  97  |     });
  98  |     const body = await res.json();
  99  |     accessToken = body.data.access_token;
  100 |   });
  101 | 
  102 |   test('create and list sessions', async ({ request }) => {
  103 |     const createRes = await request.put(`${API_BASE}/api/v1/sessions`, {
  104 |       headers: { Authorization: `Bearer ${accessToken}` },
  105 |       data: { mode: 'deep' },
  106 |     });
> 107 |     expect(createRes.ok()).toBeTruthy();
      |                            ^ Error: expect(received).toBeTruthy()
  108 |     const createBody = await createRes.json();
  109 |     expect(createBody.code).toBe(0);
  110 |     expect(createBody.data).toHaveProperty('session_id');
  111 | 
  112 |     const listRes = await request.get(`${API_BASE}/api/v1/sessions`, {
  113 |       headers: { Authorization: `Bearer ${accessToken}` },
  114 |     });
  115 |     expect(listRes.ok()).toBeTruthy();
  116 |     const listBody = await listRes.json();
  117 |     expect(listBody.code).toBe(0);
  118 |     expect(Array.isArray(listBody.data.sessions)).toBe(true);
  119 |   });
  120 | });
  121 | 
  122 | test.describe('Cases API', () => {
  123 |   let accessToken: string;
  124 | 
  125 |   test.beforeAll(async ({ request }) => {
  126 |     const res = await request.post(`${API_BASE}/api/v1/auth/login`, {
  127 |       data: { username: 'admin', password: 'admin123' },
  128 |     });
  129 |     const body = await res.json();
  130 |     accessToken = body.data.access_token;
  131 |   });
  132 | 
  133 |   test('create and list cases', async ({ request }) => {
  134 |     const createRes = await request.post(`${API_BASE}/api/v1/cases`, {
  135 |       headers: { Authorization: `Bearer ${accessToken}` },
  136 |       data: { target_repo: 'riscv/riscv-isa-manual', input_context: { arch: 'RV64I' } },
  137 |     });
  138 |     expect(createRes.ok()).toBeTruthy();
  139 |     const createBody = await createRes.json();
  140 |     expect(createBody.code).toBe(0);
  141 |     expect(createBody.data).toHaveProperty('id');
  142 |     expect(createBody.data.status).toBe('pending');
  143 | 
  144 |     const listRes = await request.get(`${API_BASE}/api/v1/cases`, {
  145 |       headers: { Authorization: `Bearer ${accessToken}` },
  146 |     });
  147 |     expect(listRes.ok()).toBeTruthy();
  148 |     const listBody = await listRes.json();
  149 |     expect(listBody.code).toBe(0);
  150 |     expect(Array.isArray(listBody.data.cases)).toBe(true);
  151 |   });
  152 | });
  153 | 
```