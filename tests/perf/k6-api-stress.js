// SCRUM-121 - Prueba de ESTRES de las APIs (punto de ruptura).
//
// Escenarios:
//   C-STR-01  rampa lineal 0 -> 200 usuarios en 5 minutos.
//   C-STR-02  rampa agresiva hasta 300 usuarios para encontrar el umbral.
//   C-STR-03  pico (spike) de 150 usuarios durante 30 s.
//   C-STR-04  endpoints criticos: login, catalogo, detalle y metricas.
//   C-STR-05  comprobacion de recuperacion: 5 VU durante 1 minuto al final.
//
// Esta prueba NO lleva thresholds estrictos: su objetivo es observar donde se
// degrada el sistema. El reporte HTML/JSON queda en /reports.
//
// Uso con Docker (desde la raiz del workspace):
//   docker compose -f docker-compose.yml -f compose.k6-stress.yaml run --rm k6-stress
//
// Variables:
//   BASE_URL       API FastAPI (http://api:8000 por defecto)
//   ANALYTICS_URL  API .NET    (http://analytics:8080 por defecto)
//   K6_VUS         techo de la rampa (200 por defecto)

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = (__ENV.BASE_URL || 'http://api:8000').replace(/\/+$/, '');
const ANALYTICS_URL = (__ENV.ANALYTICS_URL || 'http://analytics:8080').replace(/\/+$/, '');
const TECHO = Number(__ENV.K6_VUS || 200);
const ADMIN_USER = __ENV.ADMIN_USER || 'admin.panel@adopplant.com';
const ADMIN_PASSWORD = __ENV.ADMIN_PASSWORD || 'Admin2026panel';
const DONOR_USER = __ENV.DONOR_USER || 'donante.pruebas@adopplant.com';
const DONOR_PASSWORD = __ENV.DONOR_PASSWORD || 'Donante2026!';

const erroresHttp = new Rate('errores_http');
const latenciaResumen = new Trend('latencia_metricas_resumen');

export const options = {
  scenarios: {
    rampa_200: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: Math.round(TECHO * 0.25) },
        { duration: '1m', target: Math.round(TECHO * 0.5) },
        { duration: '1m', target: Math.round(TECHO * 0.75) },
        { duration: '2m', target: TECHO },
        { duration: '1m', target: 0 },
      ],
      gracefulRampDown: '30s',
      tags: { escenario: 'rampa' },
    },
    pico: {
      executor: 'ramping-vus',
      startVUs: 0,
      startTime: '7m',
      stages: [
        { duration: '10s', target: 0 },
        { duration: '30s', target: Math.round(TECHO * 0.75) },
        { duration: '20s', target: 0 },
      ],
      gracefulRampDown: '15s',
      tags: { escenario: 'pico' },
    },
    recuperacion: {
      executor: 'constant-vus',
      vus: 5,
      duration: '60s',
      // Un minuto de calma despues del pico: mide la recuperacion real, no la
      // cola de peticiones que quedaron en vuelo durante la saturacion.
      startTime: '9m',
      tags: { escenario: 'recuperacion' },
    },
  },
  thresholds: {
    // Solo se exige que el sistema se recupere despues del pico.
    'http_req_failed{escenario:recuperacion}': ['rate<=0.01'],
    'http_req_duration{escenario:recuperacion,endpoint:catalogo}': ['p(95)<3000'],
  },
};

export function setup() {
  const loginAdmin = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ identificador: ADMIN_USER, contrasena: ADMIN_PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } },
  );
  const loginDonante = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ identificador: DONOR_USER, contrasena: DONOR_PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } },
  );

  const tokenAdmin = loginAdmin.status === 200 ? loginAdmin.json('access_token') : null;
  const tokenDonante = loginDonante.status === 200 ? loginDonante.json('access_token') : null;

  const catalogo = http.get(`${BASE_URL}/api/plantas?limite=5`, {
    headers: tokenDonante ? { Authorization: `Bearer ${tokenDonante}` } : {},
  });
  const plantas = catalogo.status === 200 ? catalogo.json('plantas') : null;
  const idPlanta = Array.isArray(plantas) && plantas.length ? plantas[0].id_planta : null;

  check(loginAdmin, { 'login admin 200': (r) => r.status === 200 });
  check(loginDonante, { 'login donante 200': (r) => r.status === 200 });
  check(catalogo, { 'catalogo disponible': (r) => r.status === 200 });

  return { tokenAdmin, tokenDonante, idPlanta };
}

export default function (data) {
  const cabecerasDonante = data.tokenDonante
    ? { Authorization: `Bearer ${data.tokenDonante}` }
    : {};

  // C-STR-04: login (endpoint sensible a Argon2 y a la base de datos).
  const login = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ identificador: DONOR_USER, contrasena: DONOR_PASSWORD }),
    {
      headers: { 'Content-Type': 'application/json' },
      tags: { endpoint: 'login' },
    },
  );
  check(login, { 'login responde 200': (r) => r.status === 200 });
  erroresHttp.add(login.status !== 200);

  // C-STR-04: catalogo.
  const catalogo = http.get(`${BASE_URL}/api/plantas?limite=20`, {
    headers: cabecerasDonante,
    tags: { endpoint: 'catalogo' },
  });
  check(catalogo, { 'catalogo responde 200': (r) => r.status === 200 });
  erroresHttp.add(catalogo.status >= 400 || catalogo.status === 0);

  // C-STR-04: detalle.
  if (data.idPlanta !== null) {
    const detalle = http.get(`${BASE_URL}/api/plantas/${data.idPlanta}`, {
      headers: cabecerasDonante,
      tags: { endpoint: 'detalle' },
    });
    check(detalle, { 'detalle responde 200': (r) => r.status === 200 });
    erroresHttp.add(detalle.status >= 400 || detalle.status === 0);
  }

  // C-STR-04: metricas de la API .NET (protegidas con JWT de administrador).
  if (data.tokenAdmin) {
    const resumen = http.get(`${ANALYTICS_URL}/api/metricas/resumen`, {
      headers: { Authorization: `Bearer ${data.tokenAdmin}` },
      tags: { endpoint: 'metricas_resumen' },
    });
    latenciaResumen.add(resumen.timings.duration);
    check(resumen, { 'metricas/resumen responde 200': (r) => r.status === 200 });
    erroresHttp.add(resumen.status !== 200);

    const categorias = http.get(
      `${ANALYTICS_URL}/api/metricas/plantas-por-categoria`,
      {
        headers: { Authorization: `Bearer ${data.tokenAdmin}` },
        tags: { endpoint: 'metricas_categorias' },
      },
    );
    check(categorias, {
      'metricas/plantas-por-categoria responde 200': (r) => r.status === 200,
    });
    erroresHttp.add(categorias.status !== 200);
  }

  sleep(0.5);
}

export function handleSummary(data) {
  const resumen = {
    peticiones: data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0,
    p95_ms: data.metrics.http_req_duration
      ? data.metrics.http_req_duration.values['p(95)']
      : 0,
    errores: data.metrics.http_req_failed
      ? data.metrics.http_req_failed.values.rate
      : 0,
  };

  const salida = { stdout: JSON.stringify(resumen, null, 2) };
  if (__ENV.K6_REPORT_DIR) {
    salida[`${__ENV.K6_REPORT_DIR}/k6-stress-summary.json`] = JSON.stringify(
      data,
      null,
      2,
    );
  }
  return salida;
}
