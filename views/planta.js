'use strict';
const detailEl = id => document.getElementById(id);
let detailPlant = null, detailUser = null, sendingAdoption = false, adoptionSent = false;
function canAdopt(plant, user) {
  return Boolean(plant && user && Number(plant.id_usuario) !== Number(user.id_usuario) && plant.estado_planta === 'DISPONIBLE' && plant.visible === true && !plant.eliminada && plant.puede_solicitar === true);
}
async function detailRequest(path, options = {}) {
  const token = sessionStorage.getItem('token');
  if (!token) { window.location.replace('/views/index.html'); throw new Error('Inicia sesión para continuar.'); }
  const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 60000);
  try {
    const r = await fetch(window.ADOPPLANT_API_URL + path, {...options, headers:{Authorization:'Bearer '+token,...options.headers},signal:controller.signal,cache:'no-store'});
    if (r.status === 401) { sessionStorage.removeItem('token');window.location.replace('/views/index.html');throw new Error('Tu sesión venció.'); }
    const data = await r.json();
    if (!r.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo completar la operación.');
    if (sessionStorage.getItem('token') !== token) throw new Error('Tu sesión cambió. Recarga la página.');
    return data;
  } catch(error) { if(error.name === 'AbortError') throw new Error('El servidor tardó demasiado. Vuelve a consultar el estado antes de reintentar.'); throw error; }
  finally {clearTimeout(timer);}
}
function updateAdoptionButton() {
  const own = detailPlant && detailUser && Number(detailPlant.id_usuario) === Number(detailUser.id_usuario);
  const allowed = canAdopt(detailPlant, detailUser) && !adoptionSent;
  detailEl('requestAdoption').disabled = !allowed;
  detailEl('requestAdoption').textContent = own ? 'Esta es tu publicación' : adoptionSent ? 'Solicitud enviada' : allowed ? 'Solicitar adopción →' : 'No disponible para solicitar';
  detailEl('adoptionNotice').textContent = own ? 'No puedes solicitar la adopción de una planta que tú publicaste.' : adoptionSent ? 'Tu solicitud está pendiente de respuesta de la persona donante.' : !allowed ? 'Esta planta no está disponible para nuevas solicitudes.' : '';
}
function renderPlant() {
  const p = detailPlant;
  detailEl('plantTitle').textContent=p.nombre;document.title=p.nombre+' · PlantHaven';
  detailEl('plantType').textContent=p.categoria?.nombre || 'Planta en adopción';
  detailEl('plantRef').textContent='REF. PH-'+p.id_planta;
  const state = p.estado_planta === 'DISPONIBLE' ? '● Disponible para adopción' : p.estado_planta === 'ADOPTADA' ? 'Adoptada' : 'Adopción en proceso';
  detailEl('plantState').textContent=detailEl('photoState').textContent=state;
  const img=detailEl('plantImage');img.alt=p.nombre;img.className='';
  const fallback=()=>{img.onerror=null;img.src='/views/icon.jpeg';img.className='fallback';img.alt='Fotografía no disponible';};
  img.onerror=fallback;
  try {const url=new URL(p.fotografia_url);if(!['http:','https:'].includes(url.protocol))throw new Error();img.src=url.href;}catch(_){fallback();}
  detailEl('plantFacts').replaceChildren();
  [['Tipo',p.categoria?.nombre],['Tamaño',p.tamano],['Luz',p.necesidad_luz],['Cuidado',p.nivel_cuidado],['Salud',p.estado_salud],['Zona',p.ubicacion]].forEach(([label,value])=>{const box=document.createElement('div'),title=document.createElement('small'),text=document.createElement('strong');box.className='fact';title.textContent=label;text.textContent=value || 'No especificado';box.append(title,text);detailEl('plantFacts').append(box);});
  detailEl('plantDescription').textContent=p.descripcion || 'La persona donante no añadió una descripción.';
  detailEl('waterNeed').textContent=p.necesidad_agua;detailEl('lightNeed').textContent=p.necesidad_luz;detailEl('careNeed').textContent=p.nivel_cuidado;
  detailEl('ownerNote').textContent=Number(p.id_usuario)===Number(detailUser.id_usuario)?'Publicada por ti · Esta planta está buscando una nueva familia.':'Tu solicitud llegará a la persona que publicó esta planta.';
  updateAdoptionButton();
}
async function loadPlantDetail() {
  detailEl('retryDetail').hidden=true;detailEl('plantDetail').hidden=true;detailEl('detailStatus').textContent='Cargando la planta…';
  try {
    const id=new URLSearchParams(window.location.search).get('id');
    if(!/^[1-9][0-9]*$/.test(id || ''))throw new Error('La publicación no es válida. Vuelve al catálogo y selecciona una planta.');
    detailUser=await detailRequest('/usuarios/me');detailPlant=await detailRequest('/plantas/'+id);adoptionSent=false;
    if(canAdopt(detailPlant,detailUser)) {const pending=await detailRequest('/solicitudes?tipo=enviadas&estado=PENDIENTE&id_planta='+id+'&limite=1');adoptionSent=Array.isArray(pending)&&pending.length>0;}
    renderPlant();detailEl('plantDetail').hidden=false;detailEl('detailStatus').textContent='';
  }catch(error){detailEl('detailStatus').textContent=error.message;detailEl('retryDetail').hidden=false;}
}
detailEl('requestAdoption').addEventListener('click',()=>{if(!canAdopt(detailPlant,detailUser)||adoptionSent)return;detailEl('requestStatus').textContent='';detailEl('adoptionDialog').showModal();});
detailEl('closeAdoption').addEventListener('click',()=>{if(!sendingAdoption)detailEl('adoptionDialog').close();});
detailEl('adoptionDialog').addEventListener('cancel',event=>{if(sendingAdoption)event.preventDefault();});
detailEl('adoptionForm').addEventListener('submit',async event=>{
  event.preventDefault();if(sendingAdoption||adoptionSent||!canAdopt(detailPlant,detailUser)||!event.currentTarget.reportValidity())return;
  const message=detailEl('adoptionMessage').value.trim();if(!message){detailEl('requestStatus').textContent='Escribe un mensaje para la persona donante.';return;}
  sendingAdoption=true;detailEl('sendAdoption').disabled=true;detailEl('requestStatus').className='';detailEl('requestStatus').textContent='Enviando solicitud…';
  try {const result=await detailRequest('/solicitudes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id_planta:detailPlant.id_planta,mensaje:message})});if(!Number.isInteger(result.id_solicitud))throw new Error('No se pudo confirmar la solicitud. Recarga la página para consultar su estado.');adoptionSent=true;updateAdoptionButton();detailEl('adoptionDialog').close();window.location.href='/views/solicitudes.html?tipo=enviadas&vista=enviada&id='+result.id_solicitud;}
  catch(error){detailEl('requestStatus').className='error';detailEl('requestStatus').textContent=error.message;}
  finally{sendingAdoption=false;detailEl('sendAdoption').disabled=false;}
});
detailEl('retryDetail').addEventListener('click',loadPlantDetail);
loadPlantDetail();
