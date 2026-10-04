'use strict';
const homeElement = id => document.getElementById(id);
async function showAdminAccess(token){
  const link=homeElement('adminNav');if(!link)return;link.hidden=true;
  try{const response=await fetch(window.ADOPPLANT_API_URL+'/admin/me',{headers:{Authorization:'Bearer '+token},cache:'no-store'});
    if(response.ok){const user=await response.json();if(sessionStorage.getItem('token')===token)link.hidden=user.administrador!==true;}
  }catch(_){link.hidden=true;}
}
let checkingSession = false;
let loadingNotifications = false;
let notificationsViewRequested = false;
let unreadNotificationIds = [];
let pendingStatusNotificationIds = [];
let latestStatusRows = [];
const statusSeenStorageKey = 'plantHavenStatusNotificationsSeen';
const notificationText = {
  ACEPTADA: {className:'accepted',icon:'✓',label:'NUEVA NOTIFICACIÓN',title:'¡Tu solicitud fue aceptada!',action:'Ver adopción'},
  RECHAZADA: {className:'rejected',icon:'×',label:'SOLICITUD RECHAZADA',title:'Tu solicitud fue rechazada',action:'Ver solicitud'},
  PENDIENTE: {className:'pending',icon:'•',label:'SOLICITUD ENVIADA',title:'Tu solicitud está pendiente',action:'Ver estado'},
};
function notificationDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleDateString('es-SV', {day:'numeric', month:'short'});
}
function notificationPlant(row, plant) {
  return plant || {nombre:row.nombre_planta || 'Planta #'+row.id_planta, fotografia_url:row.fotografia_url};
}
function setNotificationPhoto(img, plant) {
  img.alt = plant.nombre || 'Planta de adopción';
  const fallback = () => { img.onerror = null; img.src = '/views/icon.jpeg'; };
  img.onerror = fallback;
  try {
    const url = new URL(plant.fotografia_url);
    if (!['http:','https:'].includes(url.protocol)) throw new Error();
    img.src = url.href;
  } catch (_) { fallback(); }
}
function renderAdoptionNotification(row, plant) {
  const meta = notificationText[row.estado] || notificationText.PENDIENTE;
  const card = document.createElement('article'); card.className = 'adoption-notification '+meta.className;
  const icon = document.createElement('span'); icon.className = 'notification-icon'; icon.textContent = meta.icon; icon.setAttribute?.('aria-hidden','true');
  const photo = document.createElement('img'); photo.className = 'notification-photo'; setNotificationPhoto(photo, notificationPlant(row, plant));
  const copy = document.createElement('div'); copy.className = 'notification-copy';
  const label = document.createElement('span'); label.className = 'notification-label'; label.textContent = meta.label;
  const title = document.createElement('h3'); title.textContent = meta.title;
  const description = document.createElement('p');
  const name = (plant && plant.nombre) || row.nombre_planta || 'tu planta solicitada';
  description.textContent = row.estado === 'ACEPTADA'
    ? 'La persona donante aceptó tu solicitud para adoptar '+name+'.'
    : row.estado === 'RECHAZADA'
      ? 'La persona donante no pudo aceptar esta solicitud para '+name+'.'
      : 'La persona donante todavía está revisando tu solicitud para '+name+'.';
  const date = document.createElement('small'); date.className = 'notification-date'; date.textContent = notificationDate(row.fecha_solicitud);
  copy.append(label,title,description,date);
  const action = document.createElement('a'); action.className = 'notification-action'; action.textContent = meta.action+' →'; action.href = '/views/solicitudes.html?tipo=enviadas&vista=enviada&id='+row.id_solicitud;
  card.append(icon,photo,copy,action); return card;
}
function setNotificationDot(items) {
  const dot = homeElement('notificationDot');
  unreadNotificationIds = Array.isArray(items)
    ? items.filter(item => !item.leida).map(item => item.id_notificacion)
    : [];
  if (dot) dot.hidden = unreadNotificationIds.length === 0 && pendingStatusNotificationIds.length === 0;
}
function statusSeenMap() {
  try { return JSON.parse(localStorage.getItem?.(statusSeenStorageKey) || '{}') || {}; }
  catch (_) { return {}; }
}
function setStatusNotificationDot(rows) {
  latestStatusRows = rows.filter(row => ['ACEPTADA','RECHAZADA'].includes(row.estado));
  const seen = statusSeenMap();
  pendingStatusNotificationIds = latestStatusRows.filter(row => seen[String(row.id_solicitud)] !== row.estado).map(row => row.id_solicitud);
  const dot = homeElement('notificationDot');
  if (dot) dot.hidden = unreadNotificationIds.length === 0 && pendingStatusNotificationIds.length === 0;
}
function markStatusNotificationsRead() {
  const seen = statusSeenMap();
  latestStatusRows.forEach(row => { seen[String(row.id_solicitud)] = row.estado; });
  try { localStorage.setItem?.(statusSeenStorageKey, JSON.stringify(seen)); } catch (_) { /* almacenamiento no disponible */ }
  pendingStatusNotificationIds = [];
  const dot = homeElement('notificationDot');
  if (dot) dot.hidden = unreadNotificationIds.length === 0;
}
async function loadUnreadNotifications(token) {
  try {
    const response = await fetch(window.ADOPPLANT_API_URL + '/notificaciones', {headers:{Authorization:'Bearer '+token},cache:'no-store'});
    if (response.ok) {
      const notices=await response.json();
      setNotificationDot(notices);
      const deliveries=homeElement('deliveryNotifications');
      if(deliveries&&Array.isArray(notices)){
        deliveries.replaceChildren();
        for(const notice of notices.filter(n=>['ENTREGA_PENDIENTE','CONFIRMACION_ENTREGA','ADOPCION_COMPLETADA'].includes(n.tipo))){
          const card=document.createElement('article');card.className='adoption-notification accepted';
          const copy=document.createElement('div');copy.className='notification-copy';
          const title=document.createElement('h3');title.textContent=notice.tipo==='ADOPCION_COMPLETADA'?'¡Adopción completada!':'Confirma la entrega de tu planta';
          const message=document.createElement('p');message.textContent=notice.mensaje;copy.append(title,message);
          const link=document.createElement('a');link.className='notification-action';link.textContent='Ver adopción →';
          link.href='/views/adopciones.html'+(notice.referencias?.id_solicitud?'?solicitud='+encodeURIComponent(notice.referencias.id_solicitud):'');
          card.append(copy,link);deliveries.append(card);
        }
      }
      if (notificationsViewRequested && unreadNotificationIds.length) await markNotificationsRead(token);
    }
  } catch (_) { /* El estado de las solicitudes sigue disponible aunque falle este indicador. */ }
}
async function markNotificationsRead(token) {
  const ids = [...unreadNotificationIds]; unreadNotificationIds = [];
  const dot = homeElement('notificationDot'); if (dot) dot.hidden = true;
  markStatusNotificationsRead();
  await Promise.all(ids.map(id => fetch(window.ADOPPLANT_API_URL + '/notificaciones/'+id, {
    method:'PATCH', headers:{Authorization:'Bearer '+token}, cache:'no-store',
  }).catch(() => null)));
}
function showExploreView(active='home') {
  notificationsViewRequested = false;
  homeElement('notifications').hidden = true;
  ['exploreShortcuts','exploreHero','exploreSearch','catalogue'].forEach(id => { homeElement(id).hidden = false; });
  homeElement('exploreNav').classList?.remove('active'); homeElement('homeNav').classList?.remove('active'); homeElement('notificationsNav').classList?.remove('active');
  homeElement(active === 'explore' ? 'exploreNav' : 'homeNav').classList?.add('active');
}
function showNotificationsView() {
  notificationsViewRequested = true;
  ['exploreShortcuts','exploreHero','exploreSearch','catalogue'].forEach(id => { homeElement(id).hidden = true; });
  homeElement('notifications').hidden = false;
  homeElement('homeNav').classList?.remove('active'); homeElement('exploreNav').classList?.remove('active'); homeElement('notificationsNav').classList?.add('active');
  const token = sessionStorage.getItem('token'); if (token) markNotificationsRead(token);
}
async function loadAdoptionNotifications() {
  if (loadingNotifications) return;
  const token = sessionStorage.getItem('token'); if (!token) return;
  loadingNotifications = true;
  const status = homeElement('notificationStatus'), section = homeElement('notifications'), feed = homeElement('notificationFeed');
  if (status) status.textContent = 'Consultando tus solicitudes…';
  try {
    const response = await fetch(window.ADOPPLANT_API_URL + '/solicitudes?tipo=enviadas&limite=20&offset=0', {
      headers:{Authorization:'Bearer '+token}, cache:'no-store',
    });
    if (response.status === 401 || response.status === 403) { logout(); return; }
    if (!response.ok) throw new Error('No se pudieron consultar tus notificaciones.');
    const rows = await response.json(); if (!Array.isArray(rows)) throw new Error('Respuesta de solicitudes no válida.');
    const visibleRows = rows.slice(0,6);
    setStatusNotificationDot(rows);
    const plants = await Promise.all(visibleRows.map(async row => {
      if (row.nombre_planta && row.fotografia_url) return row;
      try {
        const detail = await fetch(window.ADOPPLANT_API_URL + '/plantas/'+row.id_planta, {headers:{Authorization:'Bearer '+token},cache:'no-store'});
        return detail.ok ? {...row, ...(await detail.json())} : row;
      } catch (_) { return row; }
    }));
    feed.replaceChildren(...visibleRows.map((row,index)=>renderAdoptionNotification(row,notificationPlant(row,plants[index]))));
    section.hidden = !notificationsViewRequested;
    if (visibleRows.length === 0) feed.append(Object.assign(document.createElement('p'),{className:'notification-empty',textContent:'Todavía no tienes solicitudes de adopción enviadas.'}));
    if (status) status.textContent = '';
    await loadUnreadNotifications(token);
    if (notificationsViewRequested) markStatusNotificationsRead();
  } catch (error) {
    if (status) status.textContent = error.message;
    if (section) section.hidden = true;
  } finally { loadingNotifications = false; }
}
window.loadAdoptionNotifications = loadAdoptionNotifications;
const notificationRefresh = typeof setInterval === 'function' ? setInterval : null;
if (notificationRefresh) notificationRefresh(() => {
  if (sessionStorage.getItem('token')) loadAdoptionNotifications();
}, 30000);
function logout() {
  sessionStorage.removeItem('token');
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  homeElement('welcome').hidden = true;
  if (homeElement('notifications')) homeElement('notifications').hidden = true;
  if (homeElement('notificationDot')) homeElement('notificationDot').hidden = true;
  window.location.replace('/views/index.html');
}
async function checkSession() {
  if (checkingSession) return;
  const token = sessionStorage.getItem('token');
  if (!token) { logout(); return; }
  checkingSession = true;
  homeElement('welcome').hidden = true;
  notificationsViewRequested = false;
  ['exploreShortcuts','exploreHero','exploreSearch','catalogue'].forEach(id => { if (homeElement(id)) homeElement(id).hidden = false; });
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
    showAdminAccess(token);
    if (window.loadPlantCatalog) window.loadPlantCatalog();
    if (window.loadAdoptionNotifications) window.loadAdoptionNotifications();
  } catch (_) {
    homeElement('status').textContent = 'No se pudo comprobar tu sesión. Revisa tu conexión e inténtalo nuevamente.';
    homeElement('retry').hidden = false;
  } finally { clearTimeout(timeout); checkingSession = false; }
}
homeElement('logout').addEventListener('click', logout);
homeElement('retry').addEventListener('click', checkSession);
homeElement('notificationsNav').addEventListener('click', event => { event.preventDefault(); showNotificationsView(); });
homeElement('exploreNav').addEventListener('click', event => { event.preventDefault(); showExploreView('explore'); homeElement('catalogue').scrollIntoView?.({behavior:'smooth'}); });
homeElement('homeNav').addEventListener('click', event => { event.preventDefault(); showExploreView(); window.scrollTo?.({top:0,behavior:'smooth'}); });
window.addEventListener('pageshow', checkSession);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') checkSession();
});
checkSession();
