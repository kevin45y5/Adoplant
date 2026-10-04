'use strict';
const catalogEl = id => document.getElementById(id);
let plants = [], visibleCount = 9, catalogLoading = false;
const filterFields = {category: p => p.categoria?.nombre || p.categoria?.nombre_categoria || '', size: p => p.tamano, light: p => p.necesidad_luz, care: p => p.nivel_cuidado, zone: p => p.ubicacion};
const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function node(tag, className, text) { const n = document.createElement(tag); n.className = className; if (text !== undefined) n.textContent = text; return n; }
function plantPhoto(p) {
  const img = node('img', '', undefined); img.alt = p.nombre; img.loading = 'lazy';
  let valid = false;
  try { const url = new URL(p.fotografia_url); if (['https:', 'http:'].includes(url.protocol)) { img.src = url.href; valid = true; } } catch (_) {}
  const fallback = () => { img.onerror = null; img.src = '/views/icon.jpeg'; img.className = 'fallback'; img.alt = 'Fotografía no disponible'; };
  img.onerror = fallback; if (!valid) fallback(); return img;
}
function renderCatalog() {
  const search = normalize(catalogEl('search').value);
  const filtered = plants.filter(p => normalize([p.nombre,p.descripcion,filterFields.category(p),p.nivel_cuidado].join(' ')).includes(search) && Object.entries(filterFields).every(([id, get]) => !catalogEl(id).value || get(p) === catalogEl(id).value));
  catalogEl('plantGrid').replaceChildren();
  filtered.slice(0, visibleCount).forEach(p => {
    const card = node('article', 'plant-card'); const photo = node('div', 'photo-wrap'); photo.append(plantPhoto(p), node('span', 'available', '● Disponible para adopción'));
    const body = node('div','card-body'); body.append(node('span','category',filterFields.category(p) || 'Tu próxima compañera'),node('h3','',p.nombre));
    const traits = node('div','traits'); [ ['↕',p.tamano],['☀',p.necesidad_luz],['♧',p.nivel_cuidado] ].forEach(([icon,value]) => traits.append(node('div','trait',icon + ' ' + (value || 'No especificado'))));
    const button = node('button','detail-button','Ver detalles →'); button.addEventListener('click', () => showPlant(p.id_planta));
    body.append(traits,node('p','zone','⌖ ' + (p.ubicacion || 'Ubicación por consultar')),button);card.append(photo,body);catalogEl('plantGrid').append(card);
  });
  catalogEl('total').textContent = filtered.length + ' plantas disponibles';
  catalogEl('shown').textContent = 'Mostrando ' + Math.min(visibleCount,filtered.length) + ' de ' + filtered.length + ' plantas';
  catalogEl('loadMore').hidden = visibleCount >= filtered.length;
  catalogEl('catalogStatus').textContent = filtered.length ? '' : 'No encontramos plantas con estos filtros. Prueba otra búsqueda.';
  const count = Object.keys(filterFields).filter(id => catalogEl(id).value).length + (search ? 1 : 0);
  catalogEl('filterCount').textContent = count ? count + ' filtros activos' : '';
}
async function apiRead(path, token) {
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(),60000);
  try { const r = await fetch(window.ADOPPLANT_API_URL + path, {headers:{Authorization:'Bearer '+token},signal:controller.signal,cache:'no-store'});
    if (r.status === 401 || r.status === 403) { logout(); throw new Error('Tu sesión venció.'); }
    if (!r.ok) throw new Error('No se pudo cargar la información. Intenta nuevamente.');
    return await r.json();
  } finally {clearTimeout(timer);}
}
window.loadPlantCatalog = async function() {
  if (catalogLoading) return;
  const token = sessionStorage.getItem('token'); if (!token) return;
  catalogLoading = true;catalogEl('catalogStatus').textContent = 'Buscando una nueva compañera para ti…';catalogEl('retryCatalog').hidden = true;
  try {
    let all = [], page = 1, result;
    do {result = await apiRead('/plantas?estado=DISPONIBLE&limite=100&pagina='+page, token); if (!Array.isArray(result.plantas)) throw new Error('Respuesta del catálogo no válida.');all.push(...result.plantas);page++;} while (all.length < result.total && result.plantas.length);
    if (sessionStorage.getItem('token') !== token) return;
    plants = [...new Map(all.map(p => [p.id_planta,p])).values()].sort((a,b) => b.id_planta-a.id_planta);
    let publishedId = null;
    try {publishedId = sessionStorage.getItem('catalogPublishedPlant');}catch(_){}
    if(publishedId) {
      catalogEl('search').value='';
      Object.keys(filterFields).forEach(id=>catalogEl(id).value='');
      visibleCount=9;
      const index=plants.findIndex(p=>String(p.id_planta)===publishedId);
      if(index>=0){plants.unshift(...plants.splice(index,1));try{sessionStorage.removeItem('catalogPublishedPlant');}catch(_){}}
    }
    Object.entries(filterFields).forEach(([id,get]) => {const select = catalogEl(id);const previous = select.value;while(select.options.length > 1) select.remove(1); [...new Set(plants.map(get).filter(Boolean))].sort().forEach(value => {const option=node('option','',value);option.value=value;select.append(option);});select.value=[...select.options].some(option=>option.value===previous)?previous:'';});
    renderCatalog();
  } catch(error) {catalogEl('catalogStatus').textContent = error.name === 'AbortError' ? 'El servidor está tardando. Vuelve a intentarlo.' : error.message;catalogEl('retryCatalog').hidden=false;}
  finally {catalogLoading=false;}
};
async function showPlant(id) {
  window.location.href = '/views/planta.html?id=' + encodeURIComponent(id);
}
Object.keys(filterFields).forEach(id=>catalogEl(id).addEventListener('change',()=>{visibleCount=9;renderCatalog();}));
catalogEl('searchForm').addEventListener('submit',event=>{event.preventDefault();visibleCount=9;renderCatalog();});
catalogEl('search').addEventListener('input',()=>{visibleCount=9;renderCatalog();});
catalogEl('clear').addEventListener('click',()=>{Object.keys(filterFields).forEach(id=>catalogEl(id).value='');catalogEl('search').value='';visibleCount=9;renderCatalog();});
catalogEl('loadMore').addEventListener('click',()=>{visibleCount+=9;renderCatalog();});
catalogEl('retryCatalog').addEventListener('click',()=>window.loadPlantCatalog());
catalogEl('accountButton').addEventListener('click',()=>catalogEl('account').showModal());
catalogEl('guideButton').addEventListener('click',()=>catalogEl('guide').showModal());
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>catalogEl(button.dataset.close).close()));
