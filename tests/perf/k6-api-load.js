// SCRUM-95 - Prueba de CARGA SOSTENIDA de la API de AdopPlant (FastAPI).
//
// Escenarios exigidos por el ticket:
//   1) 5 usuarios virtuales durante 1 minuto.
//   2) 10 usuarios virtuales durante 5 minutos.
// Endpoints: GET /api/plantas y GET /api/plantas/{id}.
// Criterio: 0 errores 500, p95 < 3 s y tasa de errores <= 1 %.
//
// El detalle de planta exige un token valido, por eso el setup inicia sesion
// con la cuenta donante creada por scripts/seed_pruebas.py.
//
// Uso local:
//   k6 run -e BASE_URL=http://127.0.0.1:8000 Adoplant/tests/perf/k6-api-load.js
//
// Uso con Docker (desde la raiz del workspace):
//   docker compose -f docker-compose.yml -f compose.k6-api.yaml run --rm k6-api-load

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const BASE_URL = (__ENV.BASE_URL || 'http://api:8000').replace(/\/+$/, '');
const DONOR_USER = __ENV.DONOR_USER || 'donante.pruebas@adopplant.com';
const DONOR_PASSWORD = __ENV.DONOR_PASSWORD || 'Donante2026!';

const erroresHttp = new Rate('errores_http');

export const options = {
  scenarios: {
    cinco_usuarios: {
      executor: 'constant-vus',
      vus: 5,
      duration: '60s',
      tags: { escenario: '5vu' },
    },
    diez_usuarios: {
      executor: 'constant-vus',
      vus: 10,
      duration: '300s',
      startTime: '65s',
      tags: { escenario: '10vu' },
    },
  },
  thresholds: {
    'http_req_failed{escenario:5vu}': ['rate<=0.01'],
    'http_req_failed{escenario:10vu}': ['rate<=0.01'],
    'http_req_duration{escenario:5vu,endpoint:catalogo}': ['p(95)<3000'],
    'http_req_duration{escenario:5vu,endpoint:detalle}': ['p(95)<3000'],
    'http_req_duration{escenario:10vu,endpoint:catalogo}': ['p(95)<3000'],
    'http_req_duration{escenario:10vu,endpoint:detalle}': ['p(95)<3000'],
    errores_http: ['rate<=0.01'],
  },
};

export function setup() {
  const login = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ identificador: DONOR_USER, contrasena: DONOR_PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } },
  );

  if (login.status !== 200) {
    throw new Error(
      `No se pudo iniciar sesion para la prueba: HTTP ${login.status}. ` +
        'Ejecuta antes: python -m scripts.seed_pruebas',
    );
  }

  const token = login.json('access_token');
  const catalogo = http.get(`${BASE_URL}/api/plantas?limite=10`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const plantas = catalogo.status === 200 ? catalogo.json('plantas') : null;
  const idPlanta = Array.isArray(plantas) && plantas.length ? plantas[0].id_planta : null;

  check(catalogo, {
    'el catalogo responde 200 en el setup': (r) => r.status === 200,
    'hay al menos una planta publicada': () => idPlanta !== null,
  });

  return { token, idPlanta };
}

export default function (data) {
  const cabeceras = { Authorization: `Bearer ${data.token}` };

  const catalogo = http.get(`${BASE_URL}/api/plantas?limite=20`, {
    headers: cabeceras,
    tags: { endpoint: 'catalogo' },
  });
  check(catalogo, {
    'GET /api/plantas responde 200': (r) => r.status === 200,
  });
  erroresHttp.add(catalogo.status >= 400 || catalogo.status === 0);

  if (data.idPlanta !== null) {
    const detalle = http.get(`${BASE_URL}/api/plantas/${data.idPlanta}`, {
      headers: cabeceras,
      tags: { endpoint: 'detalle' },
    });
    check(detalle, {
      'GET /api/plantas/{id} responde 200': (r) => r.status === 200,
    });
    erroresHttp.add(detalle.status >= 400 || detalle.status === 0);
  }

  sleep(0.5);
}
