'use strict';
const ownEl = id => document.getElementById(id);
let ownPage = 1, ownLoading = false;
const ownRetiring = new Set();
async function ownRequest(path, options = {}) {
  const token = sessionStorage.getItem('token');
  if (!token) { window.location.replace('/views/index.html'); throw new Error('Inicia sesión para consultar tus publicaciones.'); }
  const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(window.ADOPPLANT_API_URL + path, {...options, headers:{Authorization:'Bearer '+token}, signal:controller.signal, cache:'no-store'});
    if (response.status === 401) { sessionStorage.removeItem('token'); window.location.replace('/views/index.html'); throw new Error('Tu sesión venció.'); }
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo completar la operación.');
    if (sessionStorage.getItem('token') !== token) throw new Error('Tu sesión cambió. Recarga la página.');
    return data;
  } catch (error) { if (error.name === 'AbortError') throw new Error('El servidor tardó demasiado. Revisa el estado antes de reintentar.'); throw error; }
  finally { clearTimeout(timer); }
}
function ownCard(plant) {
  const card = document.createElement('article'); card.className = 'plant-card';
  const photo = document.createElement('div'); photo.className = 'photo-wrap';
  const image = document.createElement('img'); image.alt = plant.nombre;
  image.src = '/views/icon.jpeg';
  try { const url = new URL(plant.fotografia_url); if (['http:','https:'].includes(url.protocol)) image.src = url.href; } catch (_) {}
  image.onerror = () => { image.onerror = null; image.src = '/views/icon.jpeg'; };
  photo.append(image);
  const body = document.createElement('div'); body.className = 'card-body';
  const title = document.createElement('h2'); title.textContent = plant.nombre;
  const state = document.createElement('p'); state.className = 'own-state'; state.textContent = plant.eliminada ? 'Retirada' : plant.estado_planta;
  const actions = document.createElement('div'); actions.className = 'own-actions';
  if (!plant.eliminada && plant.visible) {
    const detail = document.createElement('a'); detail.href = '/views/planta.html?id=' + plant.id_planta; detail.textContent = 'Ver detalle'; actions.append(detail);
  }
  if (!plant.eliminada && plant.estado_planta === 'DISPONIBLE') {
    const edit = document.createElement('a'); edit.href = '/views/publicar.html?editar=' + plant.id_planta; edit.textContent = 'Editar publicación'; actions.append(edit);
    const retire = document.createElement('button'); retire.type = 'button'; retire.textContent = 'Retirar publicación';
    retire.addEventListener('click', async () => {
      if (ownRetiring.has(plant.id_planta) || !window.confirm('¿Retirar esta publicación? Dejará de aparecer en el catálogo.')) return;
      ownRetiring.add(plant.id_planta); retire.disabled = true;
      try {
        const result = await ownRequest('/plantas/' + plant.id_planta, {method:'DELETE'});
        if (!result.eliminada || result.visible) throw new Error('No se pudo confirmar el retiro. Recarga tus publicaciones para revisar su estado.');
        state.textContent = 'Retirada'; actions.replaceChildren(); ownEl('ownStatus').textContent = 'Publicación retirada correctamente.';
      } catch (error) { ownEl('ownStatus').textContent = error.message; }
      finally { ownRetiring.delete(plant.id_planta); retire.disabled = false; }
    });
    actions.append(retire);
  }
  body.append(title, state, actions); card.append(photo, body); return card;
}
async function loadOwn(reset = false) {
  if (ownLoading) return;
  ownLoading = true; ownEl('ownRetry').hidden = true; ownEl('ownMore').disabled = true;
  if (reset) { ownPage = 1; ownEl('ownGrid').replaceChildren(); }
  try {
    const rows = await ownRequest('/plantas/mias?pagina=' + ownPage + '&limite=20');
    if (!Array.isArray(rows)) throw new Error('No se pudieron cargar tus publicaciones.');
    rows.forEach(plant => ownEl('ownGrid').append(ownCard(plant)));
    ownEl('ownStatus').textContent = ownPage === 1 && !rows.length ? 'Todavía no has publicado plantas.' : '';
    ownEl('ownMore').hidden = rows.length < 20; ownPage++;
  } catch (error) { ownEl('ownStatus').textContent = error.message; ownEl('ownRetry').hidden = false; }
  finally { ownLoading = false; ownEl('ownMore').disabled = false; }
}
ownEl('ownRetry').addEventListener('click', () => loadOwn(true));
ownEl('ownMore').addEventListener('click', () => loadOwn());
loadOwn(true);
