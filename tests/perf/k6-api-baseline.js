// SCRUM-92 - Prueba de carga BASICA de la API de AdopPlant (FastAPI).
//
// Escenarios exigidos por el ticket:
//   1) 1 usuario virtual durante 1 minuto.
//   2) 5 usuarios virtuales durante 2 minutos.
// Endpoints: GET / y GET /api/plantas.
// Criterio: HTTP 200, 0 % de errores y p95 <= 2 s (sin contar el acceso en frio).
//
// Uso local (k6 instalado):
//   k6 run -e BASE_URL=http://127.0.0.1:8000 Adoplant/tests/perf/k6-api-baseline.js
//
// Uso con Docker (desde la raiz del workspace):
//   docker compose -f docker-compose.yml -f compose.k6-api.yaml run --rm k6-api

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const BASE_URL = (__ENV.BASE_URL || 'http://api:8000').replace(/\/+$/, '');
const ADMIN_USER = __ENV.ADMIN_USER || 'admin.panel@adopplant.com';
const ADMIN_PASSWORD = __ENV.ADMIN_PASSWORD || 'Admin2026panel';

const erroresHttp = new Rate('errores_http');

export const options = {
  scenarios: {
    un_usuario: {
      executor: 'constant-vus',
      vus: 1,
      duration: '60s',
      tags: { escenario: '1vu' },
    },
    cinco_usuarios: {
      executor: 'constant-vus',
      vus: 5,
      duration: '120s',
      startTime: '65s',
      tags: { escenario: '5vu' },
    },
  },
  thresholds: {
    'http_req_failed{escenario:1vu}': ['rate==0'],
    'http_req_failed{escenario:5vu}': ['rate==0'],
    'http_req_duration{escenario:1vu,endpoint:raiz}': ['p(95)<2000'],
    'http_req_duration{escenario:1vu,endpoint:catalogo}': ['p(95)<2000'],
    'http_req_duration{escenario:5vu,endpoint:raiz}': ['p(95)<2000'],
    'http_req_duration{escenario:5vu,endpoint:catalogo}': ['p(95)<2000'],
    errores_http: ['rate==0'],
  },
};

export function setup() {
  const respuesta = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ identificador: ADMIN_USER, contrasena: ADMIN_PASSWORD }),
    {
      headers: { 'Content-Type': 'application/json' },
      tags: { endpoint: 'login' },
    },
  );

  check(respuesta, {
    'login de administrador devuelve 200': (r) => r.status === 200,
    'login devuelve access_token': (r) => Boolean(r.json('access_token')),
  });

  return { token: respuesta.json('access_token') };
}

export default function (data) {
  const cabeceras = { Authorization: `Bearer ${data.token}` };

  const raiz = http.get(`${BASE_URL}/`, { tags: { endpoint: 'raiz' } });
  check(raiz, {
    'GET / responde 200': (r) => r.status === 200,
    'GET / devuelve JSON': (r) =>
      String(r.headers['Content-Type'] || '').includes('application/json'),
  });
  erroresHttp.add(raiz.status !== 200);

  // El catalogo es publico: se consulta sin token, como lo hace la web.
  const catalogo = http.get(`${BASE_URL}/api/plantas?limite=20`, {
    tags: { endpoint: 'catalogo' },
  });
  check(catalogo, {
    'GET /api/plantas responde 200': (r) => r.status === 200,
    'GET /api/plantas devuelve plantas': (r) =>
      Array.isArray(r.json('plantas')),
  });
  erroresHttp.add(catalogo.status !== 200);

  // Una pausa corta por iteracion evita saturar sin querer el escenario de 5 VU.
  sleep(1);

  const perfil = http.get(`${BASE_URL}/api/usuarios/me`, {
    headers: cabeceras,
    tags: { endpoint: 'perfil' },
  });
  check(perfil, {
    'GET /api/usuarios/me con token responde 200': (r) => r.status === 200,
  });
  erroresHttp.add(perfil.status !== 200);
}
