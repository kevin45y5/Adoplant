import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 },  // Incremento a 20 usuarios
    { duration: '20s', target: 100 }, // Carga de estrés con 100 usuarios
    { duration: '10s', target: 0 },   // Reducción gradual
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% de peticiones en menos de 500ms
    http_req_failed: ['rate<0.01'],    // Menos del 1% de errores
  },
};

export default function () {
  // Petición al endpoint de la API
  const res = http.get('http://localhost:8000/api/v1/plants');

  check(res, {
    'Estado 200 OK': (r) => r.status === 200,
  });

  sleep(1);
}