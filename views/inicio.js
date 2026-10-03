'use strict';
const homeElement = id => document.getElementById(id);
let checkingSession = false;
function logout() {
  sessionStorage.removeItem('token');
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  homeElement('welcome').hidden = true;
  window.location.replace('/views/index.html');
}
async function checkSession() {
  if (checkingSession) return;
  const token = sessionStorage.getItem('token');
  if (!token) { logout(); return; }
  checkingSession = true;
  homeElement('welcome').hidden = true;
  homeElement('retry').hidden = true;
  homeElement('status').textContent = 'Comprobando tu sesión…';
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(window.ADOPPLANT_API_URL + '/usuarios/me', {
      headers: {Authorization: 'Bearer ' + token}, signal: controller.signal,
      cache: 'no-store',
    });
    if (response.status === 401 || response.status === 403) { logout(); return; }
    if (!response.ok) throw new Error();
    const user = await response.json();
    // Si se cerró la sesión mientras la petición estaba en curso, no mostrar datos.
    if (sessionStorage.getItem('token') !== token) return;
    homeElement('greeting').textContent = 'Hola, ' + user.nombre;
    homeElement('email').textContent = 'Correo: ' + user.correo;
    homeElement('phone').textContent = 'Teléfono: ' + user.telefono;
    homeElement('status').textContent = '';
    homeElement('welcome').hidden = false;
  } catch (_) {
    homeElement('status').textContent = 'No se pudo comprobar tu sesión. Revisa tu conexión e inténtalo nuevamente.';
    homeElement('retry').hidden = false;
  } finally { clearTimeout(timeout); checkingSession = false; }
}
homeElement('logout').addEventListener('click', logout);
homeElement('retry').addEventListener('click', checkSession);
window.addEventListener('pageshow', checkSession);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') checkSession();
});
checkSession();
