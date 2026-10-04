'use strict';
const adoptionEl=id=>document.getElementById(id);
const adoptionNode=(tag,cls,text)=>{const node=document.createElement(tag);node.className=cls;if(text!==undefined)node.textContent=text;return node;};
let selectedAdoption=null,confirmingDelivery=false,loadingAdoptions=false;
const adoptionToken=sessionStorage.getItem('token');
async function adoptionApi(path,options={}){
  if(!adoptionToken||sessionStorage.getItem('token')!==adoptionToken){window.location.replace('/views/index.html');throw new Error('Inicia sesión.');}
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
  try{const response=await fetch(window.ADOPPLANT_API_URL+'/adopciones'+path,{...options,headers:{Authorization:'Bearer '+adoptionToken},cache:'no-store',signal:controller.signal});
    if(response.status===401){window.location.replace('/views/index.html');throw new Error('Tu sesión venció.');}
    if(response.status===404)throw new Error('Esta adopción no está disponible. Si acabas de actualizar el proyecto, despliega también la API.');
    const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'No se pudo consultar la adopción.');
    if(sessionStorage.getItem('token')!==adoptionToken)throw new Error('La sesión cambió.');return data;
  }catch(error){if(error.name==='AbortError')throw new Error('No se recibió la respuesta. Revisa el estado antes de reintentar.');throw error;}finally{clearTimeout(timer);}
}
function adoptionPhoto(img,p){img.alt=p.nombre;img.onerror=()=>{img.onerror=null;img.src='/views/icon.jpeg';};try{const u=new URL(p.fotografia_url);if(!['https:','http:'].includes(u.protocol))throw new Error();img.src=u.href;}catch(_){img.src='/views/icon.jpeg';}}
function confirmationDate(value){return value?new Date(value).toLocaleString('es-SV'):'Pendiente';}
function renderAdoption(a){
  selectedAdoption=a;const donor=a.rol==='donante',mine=donor?a.fecha_entrega:a.fecha_recepcion,done=a.estado==='COMPLETADA';
  adoptionEl('adoptionList').hidden=true;adoptionEl('adoptionDetail').hidden=false;adoptionEl('adoptionDetail').className=donor?'donor':'receiver';
  adoptionEl('deliveryTitle').textContent=donor?'Confirmar entrega de planta':'Confirmar recepción de planta';
  adoptionEl('deliveryIdentity').textContent=(donor?'Donante: '+a.donante:'Adoptante: '+a.adoptante)+' · PH-'+a.id_adopcion;
  adoptionEl('deliveryState').textContent=done?'✓ Adopción completada':mine?'Esperando la otra confirmación':a.fecha_entrega?'✓ Entrega confirmada':a.fecha_recepcion?'✓ Recepción confirmada':'● Adopción en proceso';
  adoptionPhoto(adoptionEl('deliveryPhoto'),a.planta);adoptionEl('deliveryPlant').textContent=a.planta.nombre;
  adoptionEl('deliveryDescription').textContent=a.planta.descripcion||'Una nueva oportunidad para crecer en un hogar responsable.';
  adoptionEl('deliveryLight').textContent=a.planta.luz||'Consulta al donante';adoptionEl('deliveryWater').textContent=a.planta.riego||'Consulta al donante';adoptionEl('deliverySize').textContent=a.planta.tamano||'No indicado';
  adoptionEl('counterpartRole').textContent=donor?'ADOPTANTE SELECCIONADO':'PERSONA DONANTE';adoptionEl('counterpartName').textContent=donor?a.adoptante:a.donante;
  adoptionEl('deliveryZone').textContent=a.planta.ubicacion||'Acuerda un punto en el chat';adoptionEl('deliveryChat').href='/views/mensajes.html?planta='+a.id_planta;
  adoptionEl('donorConfirmation').textContent='Entrega del donante: '+confirmationDate(a.fecha_entrega);adoptionEl('adopterConfirmation').textContent='Recepción del adoptante: '+confirmationDate(a.fecha_recepcion);
  adoptionEl('deliveryWarning').textContent=done?'Ambos confirmaron el intercambio. La planta ya está marcada como adoptada.':mine?'Tu confirmación está guardada. La adopción se completará cuando la otra persona confirme.':donor?'Marca la entrega únicamente cuando hayas entregado físicamente la planta al adoptante.':'Confirma únicamente cuando tengas la planta en tus manos.';
  adoptionEl('confirmDelivery').textContent=done?'✓ Adopción completada':mine?'✓ Tu confirmación está guardada':donor?'Marcar como entregada':'Marcar como recibida';adoptionEl('confirmDelivery').disabled=Boolean(mine)||done||confirmingDelivery;
}
function renderAdoptions(rows){
  adoptionEl('adoptionCards').replaceChildren();
  for(const a of rows){const card=adoptionNode('article','adoption-card'),img=adoptionNode('img','');adoptionPhoto(img,a.planta);const body=adoptionNode('div','');body.append(adoptionNode('h2','',a.planta.nombre),adoptionNode('p','',(a.rol==='donante'?'Donante':'Adoptante')+' · '+(a.estado==='COMPLETADA'?'Adopción completada':'Adopción en proceso')));const link=adoptionNode('a','',a.estado==='COMPLETADA'?'Ver adopción':a.rol==='donante'?'Confirmar entrega':'Confirmar recepción');link.href='/views/adopciones.html?id='+a.id_adopcion;card.append(img,body,link);adoptionEl('adoptionCards').append(card);}
  if(!rows.length)adoptionEl('adoptionCards').append(adoptionNode('p','','Todavía no tienes adopciones. Aparecerán aquí al aceptar una solicitud.'));
}
async function loadAdoptions(){
  if(loadingAdoptions||confirmingDelivery)return;loadingAdoptions=true;adoptionEl('retryAdoptions').hidden=true;
  try{const params=new URLSearchParams(window.location.search),id=params.get('id');
    if(id){if(!/^[1-9][0-9]*$/.test(id))throw new Error('Referencia no válida.');renderAdoption(await adoptionApi('/'+id));}
    else{const rows=await adoptionApi('');if(!Array.isArray(rows))throw new Error('Respuesta de adopciones no válida.');const match=rows.find(a=>String(a.id_solicitud)===params.get('solicitud')||String(a.id_planta)===params.get('planta'));if(match)renderAdoption(match);else renderAdoptions(rows);}
    adoptionEl('adoptionStatus').textContent='';
  }catch(error){adoptionEl('adoptionStatus').textContent=error.message;adoptionEl('retryAdoptions').hidden=false;}finally{loadingAdoptions=false;}
}
adoptionEl('confirmDelivery').onclick=()=>{if(!selectedAdoption||adoptionEl('confirmDelivery').disabled)return;adoptionEl('deliveryDialogText').textContent=selectedAdoption.rol==='donante'?'¿Ya entregaste físicamente la planta al adoptante?':'¿Ya recibiste físicamente la planta del donante?';adoptionEl('deliveryDialog').showModal();};
adoptionEl('cancelDelivery').onclick=()=>{if(!confirmingDelivery)adoptionEl('deliveryDialog').close();};
adoptionEl('deliveryDialog').addEventListener('cancel',event=>{if(confirmingDelivery)event.preventDefault();});
adoptionEl('saveDelivery').onclick=async()=>{
  if(confirmingDelivery||!selectedAdoption||adoptionEl('confirmDelivery').disabled)return;confirmingDelivery=true;adoptionEl('saveDelivery').disabled=true;adoptionEl('cancelDelivery').disabled=true;adoptionEl('confirmDelivery').disabled=true;
  try{const a=await adoptionApi('/'+selectedAdoption.id_adopcion+'/confirmar',{method:'POST'});renderAdoption(a);adoptionEl('deliveryFeedback').textContent='Confirmación guardada correctamente.';}
  catch(error){adoptionEl('deliveryFeedback').textContent=error.message;}
  finally{confirmingDelivery=false;adoptionEl('saveDelivery').disabled=false;adoptionEl('cancelDelivery').disabled=false;adoptionEl('deliveryDialog').close();renderAdoption(selectedAdoption);}
};
adoptionEl('retryAdoptions').onclick=loadAdoptions;
setInterval(()=>{if(document.visibilityState==='visible'&&!adoptionEl('deliveryDialog').open)loadAdoptions();},15000);
loadAdoptions();
