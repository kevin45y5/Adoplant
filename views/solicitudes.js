'use strict';
const reqEl=id=>document.getElementById(id);
const requestParams=new URLSearchParams(window.location.search);
const requestType=requestParams.get('tipo')==='enviadas'?'enviadas':'recibidas';
let requestUser=null,selectedRequest=null,selectedPlant=null,decision=null,deciding=false,listBusy=false,listVersion=0;
let requestRows=[],requestOffset=0,acceptanceNodes=[];
const ownPlants=new Map();
const textNode=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls;if(text!==undefined)n.textContent=text;return n;};
const personName=r=>r.nombre_adoptante || 'Solicitante #'+r.id_adoptante;
const plantName=r=>r.nombre_planta || ownPlants.get(r.id_planta)?.nombre || 'Planta #'+r.id_planta;
const requestDate=value=>{const d=new Date(value);return Number.isNaN(d.getTime())?'Fecha no disponible':d.toLocaleString('es-SV',{dateStyle:'medium',timeStyle:'short'});};
function stateLabel(state){return {PENDIENTE:'● Pendiente',ACEPTADA:'✓ Aceptada',RECHAZADA:'× Rechazada'}[state] || state;}
function stateBadge(el,state){el.textContent=stateLabel(state);el.className='request-state'+(state==='ACEPTADA'?' accepted':state==='RECHAZADA'?' rejected':'');}
async function requestsApi(path,options={}){
  const token=sessionStorage.getItem('token');if(!token){window.location.replace('/views/index.html');throw new Error('Inicia sesión para consultar tus solicitudes.');}
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),60000);
  try{
    const r=await fetch(window.ADOPPLANT_API_URL+path,{...options,headers:{Authorization:'Bearer '+token,...options.headers},signal:controller.signal,cache:'no-store'});
    if(r.status===401){sessionStorage.removeItem('token');window.location.replace('/views/index.html');}
    const data=await r.json();
    if(!r.ok){const error=new Error(typeof data.detail==='string'?data.detail:'No se pudo completar la operación.');error.status=r.status;throw error;}
    if(sessionStorage.getItem('token')!==token)throw new Error('Tu sesión cambió. Recarga la página.');
    return data;
  }catch(error){if(error.name==='AbortError')throw new Error('No se pudo confirmar la respuesta. Recarga para consultar el estado antes de reintentar.');throw error;}
  finally{clearTimeout(timer);}
}
function requestPhoto(img,p){
  img.alt=p?.nombre || 'Planta solicitada';
  const fallback=()=>{img.onerror=null;img.src='/views/icon.jpeg';};img.onerror=fallback;
  try{const url=new URL(p?.fotografia_url);if(!['http:','https:'].includes(url.protocol))throw new Error();img.src=url.href;}catch(_){fallback();}
}
function plantPanel(container,p){
  container.replaceChildren();
  if(!p){container.append(textNode('div','sidebar-note','Seleccioná una de tus publicaciones para ver las personas interesadas en esa planta.'));return;}
  const card=textNode('article','plant-summary'),img=textNode('img','');requestPhoto(img,p);
  card.append(img,textNode('h2','',p.nombre || 'Planta #'+p.id_planta));
  [['⌖',p.ubicacion],['☀',p.necesidad_luz],['♧',p.necesidad_agua],['Estado',p.estado_planta]].forEach(([label,value])=>{if(value)card.append(textNode('div','summary-trait',label+' · '+value));});
  const link=textNode('a','','Ver detalles de la planta →');link.href='/views/planta.html?id='+p.id_planta;card.append(link);container.append(card,textNode('div','sidebar-note','Tu solicitud y tus mensajes solo son visibles para las personas involucradas en esta adopción.'));
}
function canDecideRequest(r,p,user){return Boolean(r&&p&&user&&Number(p.id_usuario)===Number(user.id_usuario)&&r.estado==='PENDIENTE'&&p.estado_planta==='DISPONIBLE'&&p.visible===true&&!p.eliminada);}
async function loadOwnPlants(){
  ownPlants.clear();let page=1,rows;
  do{rows=await requestsApi('/plantas/mias?limite=100&pagina='+page);if(!Array.isArray(rows))throw new Error('No se pudieron cargar tus publicaciones.');rows.forEach(p=>ownPlants.set(p.id_planta,p));page++;}while(rows.length===100);
  const select=reqEl('requestPlant');while(select.options.length>1)select.remove(1);
  ownPlants.forEach(p=>{const opt=textNode('option','',p.nombre+' · #'+p.id_planta);opt.value=String(p.id_planta);select.append(opt);});
  const initial=requestParams.get('planta');if(initial&&ownPlants.has(Number(initial)))select.value=initial;
}
function appendRequestCard(r){
  const card=textNode('article','request-card'),head=textNode('div','applicant-heading');
  const name=requestType==='recibidas'?personName(r):plantName(r);
  const identity=textNode('div','');identity.append(textNode('h3','',name),textNode('small','',requestDate(r.fecha_solicitud)));
  const state=textNode('span','');stateBadge(state,r.estado);head.append(textNode('span','applicant-avatar',name.slice(0,2).toUpperCase()),identity,state);
  const foot=textNode('div','request-card-footer');foot.append(textNode('span','',requestType==='recibidas'?'Para '+plantName(r):'Solicitud #'+r.id_solicitud));
  const link=textNode('a','primary-link','Ver solicitud →');link.href='/views/solicitudes.html?tipo='+requestType+'&id='+r.id_solicitud;foot.append(link);
  card.append(head,textNode('blockquote','',r.mensaje),foot);reqEl('requestCards').append(card);
}
async function loadRequestList(reset=true){
  if(listBusy&&!reset)return;
  const version=++listVersion;listBusy=true;reqEl('moreRequests').disabled=true;reqEl('requestsStatus').textContent='Consultando solicitudes…';reqEl('retryRequests').hidden=true;
  if(reset){requestRows=[];requestOffset=0;reqEl('requestCards').replaceChildren();reqEl('moreRequests').hidden=true;}
  const filter=reqEl('requestPlant').value;
  plantPanel(reqEl('listPlantPanel'),ownPlants.get(Number(filter)));
  reqEl('listPlantPanel').hidden=requestType==='enviadas';
  try{
    const query=new URLSearchParams({tipo:requestType,limite:'20',offset:String(requestOffset)});
    if(requestType==='recibidas'&&filter)query.set('id_planta',filter);
    if(reqEl('requestState').value)query.set('estado',reqEl('requestState').value);
    const rows=await requestsApi('/solicitudes?'+query);if(version!==listVersion)return;
    if(!Array.isArray(rows))throw new Error('Respuesta de solicitudes no válida.');
    const seen=new Set(requestRows.map(r=>r.id_solicitud));rows.filter(r=>!seen.has(r.id_solicitud)).forEach(r=>{requestRows.push(r);appendRequestCard(r);});requestOffset+=rows.length;
    reqEl('moreRequests').hidden=rows.length<20;reqEl('listEmpty').hidden=requestRows.length>0;reqEl('requestCount').textContent=requestRows.length+' solicitudes'+(rows.length===20?' cargadas':'');reqEl('requestsStatus').textContent='';
  }catch(error){if(version===listVersion){reqEl('requestsStatus').textContent=error.message;reqEl('retryRequests').hidden=false;}}
  finally{if(version===listVersion){listBusy=false;reqEl('moreRequests').disabled=false;}}
}
async function requestPlantData(r){
  if(requestType==='recibidas'&&requestParams.get('vista')!=='enviada')return requestsApi('/plantas/mias/'+r.id_planta);
  try{return await requestsApi('/plantas/'+r.id_planta);}catch(error){if(error.status===404)return {id_planta:r.id_planta,nombre:plantName(r)};throw error;}
}
async function completeRequestNames(r){
  // La lista incluye los nombres; algunas versiones del detalle solo devuelven IDs.
  if(r.nombre_adoptante&&r.nombre_planta)return r;
  const type=Number(r.id_adoptante)===Number(requestUser.id_usuario)?'enviadas':'recibidas';
  let offset=0,rows;
  do{
    rows=await requestsApi('/solicitudes?tipo='+type+'&id_planta='+r.id_planta+'&limite=100&offset='+offset);
    if(!Array.isArray(rows))throw new Error('No se pudo consultar la identidad del solicitante.');
    const match=rows.find(item=>item.id_solicitud===r.id_solicitud);
    if(match)return {...r,nombre_adoptante:match.nombre_adoptante||r.nombre_adoptante,nombre_planta:match.nombre_planta||r.nombre_planta};
    offset+=rows.length;
  }while(rows.length===100);
  return r;
}
function renderRequestDetail(){
  const r=selectedRequest,p=selectedPlant,own=Number(p.id_usuario)===Number(requestUser.id_usuario);
  showRequestChatLink(r);
  reqEl('requestTitle').textContent=own?'Solicitud de '+personName(r):'Tu solicitud de adopción';
  reqEl('applicantName').textContent=personName(r);reqEl('applicantAvatar').textContent=personName(r).slice(0,2).toUpperCase();reqEl('requestDate').textContent=requestDate(r.fecha_solicitud);
  reqEl('fullRequestMessage').textContent=r.mensaje;reqEl('requestedPlantName').textContent=p.nombre || plantName(r);reqEl('requestIdLabel').textContent='PH-'+r.id_solicitud;
  reqEl('requestReference').textContent='Solicitud #'+r.id_solicitud;stateBadge(reqEl('detailRequestState'),r.estado);plantPanel(reqEl('detailPlantPanel'),p);
  reqEl('decisionActions').hidden=!canDecideRequest(r,p,requestUser);reqEl('decisionNotice').hidden=!own;
  reqEl('returnList').href='/views/solicitudes.html?tipo='+(own?'recibidas':'enviadas');reqEl('backRequests').href=reqEl('returnList').href;reqEl('backRequests').textContent='← Volver a mis solicitudes';
}
function renderSentConfirmation(){
  const r=selectedRequest,p=selectedPlant;
  showRequestChatLink(r);
  if(Number(r.id_adoptante)!==Number(requestUser.id_usuario))throw new Error('Esta confirmación no corresponde a una solicitud enviada por tu cuenta.');
  requestPhoto(reqEl('confirmationPhoto'),p);stateBadge(reqEl('confirmationState'),r.estado);
  reqEl('confirmationTitle').textContent=r.estado==='PENDIENTE'?'¡Solicitud enviada!':'Estado de tu solicitud';
  reqEl('confirmationText').textContent='Tu solicitud para adoptar '+(p.nombre||plantName(r))+' fue enviada a la persona donante.';
  reqEl('confirmationFacts').replaceChildren();[['Tipo',p.categoria?.nombre],['Luz',p.necesidad_luz],['Zona',p.ubicacion]].forEach(([label,value])=>{const box=textNode('div','');box.append(textNode('small','',label),textNode('strong','',value||'No especificado'));reqEl('confirmationFacts').append(box);});
  reqEl('requestReference').textContent='Confirmación de adopción · PH-'+r.id_solicitud;reqEl('sentConfirmation').hidden=false;
}
function showRequestChatLink(r){
  const delivery=reqEl('requestDeliveryLink');
  if(delivery){delivery.hidden=r.estado!=='ACEPTADA';delivery.href='/views/adopciones.html?solicitud='+r.id_solicitud;}
  const link=reqEl('requestChatLink');
  if(link){link.hidden=r.estado!=='ACEPTADA';link.href='/views/mensajes.html?planta='+r.id_planta;}
}
async function initializeRequests(){
  reqEl('retryRequests').hidden=true;reqEl('requestsStatus').textContent='Cargando tus solicitudes…';
  try{
    requestUser=await requestsApi('/usuarios/me');
    const id=requestParams.get('id');
    if(id!==null){
      if(!/^[1-9][0-9]*$/.test(id))throw new Error('La referencia de solicitud no es válida.');
      selectedRequest=await requestsApi('/solicitudes/'+id);selectedRequest=await completeRequestNames(selectedRequest);selectedPlant=await requestPlantData(selectedRequest);
      if(requestParams.get('vista')==='enviada')renderSentConfirmation();else{renderRequestDetail();reqEl('requestDetail').hidden=false;}
      reqEl('requestsStatus').textContent='';
    }else{
      reqEl('listTitle').textContent=requestType==='recibidas'?'Solicitudes recibidas':'Mis solicitudes enviadas';
      reqEl('listDescription').textContent=requestType==='recibidas'?'Revisá quién quiere darle un nuevo hogar a tus plantas.':'Consultá el estado de las plantas que te gustaría adoptar.';
      reqEl(requestType==='recibidas'?'receivedTab':'sentTab').className='selected';reqEl('plantFilterLabel').hidden=requestType!=='recibidas';reqEl('donorNotice').hidden=requestType!=='recibidas';
      if(requestType==='recibidas')await loadOwnPlants();
      reqEl('requestsList').hidden=false;await loadRequestList();
    }
  }catch(error){reqEl('requestsStatus').textContent=error.message;reqEl('retryRequests').hidden=false;}
}
function prepareAcceptanceDialog(){
  const dialog=reqEl('decisionDialog');
  if(!acceptanceNodes.length){
    const progress=textNode('div','acceptance-progress');progress.append(textNode('span','', '● PASO DE CONFIRMACIÓN'),textNode('b','', 'Pendiente de tu confirmación'));
    const icon=textNode('div','acceptance-icon','♧');
    const summary=textNode('article','acceptance-summary'),photo=document.createElement('img');photo.id='decisionPhoto';
    const details=textNode('div','acceptance-summary-details');details.append(textNode('strong','',selectedPlant?.nombre||plantName(selectedRequest)),textNode('small','',selectedPlant?.ubicacion||'Ubicación no especificada'),textNode('small','','ID: PH-'+selectedRequest.id_solicitud));
    summary.append(photo,details);
    const person=textNode('div','acceptance-person');person.append(textNode('span','acceptance-person-avatar',personName(selectedRequest).slice(0,1).toUpperCase()),textNode('div','',personName(selectedRequest)+' · Adoptante verificada'),textNode('small','',selectedRequest.id_adoptante?'Solicitante #'+selectedRequest.id_adoptante:'Solicitud de adopción'));
    const warning=textNode('div','acceptance-warning');warning.append(textNode('strong','', '⚠ Advertencia importante de confirmación'),textNode('p','', 'Al aceptar esta solicitud, las demás solicitudes pendientes de esta planta se cerrarán automáticamente.'));
    const tip=textNode('div','acceptance-tip');tip.append(textNode('strong','', '💡 Recomendaciones antes de aceptar'),textNode('p','', 'Coordina con la persona adoptante la fecha, hora y punto de entrega mediante el chat de la comunidad.'));
    acceptanceNodes=[progress,icon,summary,person,warning,tip];dialog.append(progress,icon,summary,person,warning,tip);
  }
  const [, ,summary,person]=acceptanceNodes;acceptanceNodes.forEach(node=>{node.hidden=false;});
  const photo=reqEl('decisionPhoto');requestPhoto(photo,selectedPlant);
  const type=selectedPlant?.categoria?.nombre||selectedPlant?.tipo_planta||'Planta';
  const summaryDetails=summary.querySelectorAll?.('small');
  if(summaryDetails?.[0])summaryDetails[0].textContent=(selectedPlant?.ubicacion||'Ubicación no especificada')+' · '+type;
  if(summaryDetails?.[1])summaryDetails[1].textContent='ID: PH-'+selectedRequest.id_solicitud;
  person.querySelector?.('div') && (person.querySelector('div').textContent=personName(selectedRequest)+' · Adoptante verificada');
  dialog.classList?.add('accept-mode');
  reqEl('confirmDecision').textContent='◉ Sí, aceptar solicitud';reqEl('confirmDecision').className='primary-button accept-confirm';
  reqEl('cancelDecision').textContent='Cancelar';
}
function clearAcceptanceDialog(){
  const dialog=reqEl('decisionDialog');acceptanceNodes.forEach(node=>{node.hidden=true;});dialog.classList?.remove('accept-mode');
  reqEl('confirmDecision').textContent='Confirmar';reqEl('confirmDecision').className='primary-button';reqEl('cancelDecision').textContent='Cancelar';
}
function openDecision(state){
  if(deciding||!canDecideRequest(selectedRequest,selectedPlant,requestUser))return;
  decision=state;
  if(state==='ACEPTADA'){
    prepareAcceptanceDialog();
    reqEl('decisionTitle').textContent='¿Aceptar a '+personName(selectedRequest)+' como adoptante?';
    reqEl('decisionExplanation').textContent='Estás a punto de transferir la custodia responsable de tu planta.';
  }else{
    clearAcceptanceDialog();
    reqEl('decisionTitle').textContent='¿Rechazar esta solicitud?';
    reqEl('decisionExplanation').textContent='Esta solicitud quedará rechazada. Las demás personas interesadas conservarán sus solicitudes.';
  }
  reqEl('decisionDialog').showModal();
}
async function submitRequestDecision(state){
  const options={method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({estado:state})};
  try{return await requestsApi('/solicitudes/'+selectedRequest.id_solicitud+'/decision',options);}
  catch(error){
    // Permite trabajar con la versión anterior de la API mientras se despliega la ruta específica.
    if([404,405,422].includes(error.status))return requestsApi('/solicitudes/'+selectedRequest.id_solicitud,options);
    throw error;
  }
}
async function confirmRequestDecision(){
  if(deciding||!['ACEPTADA','RECHAZADA'].includes(decision)||!canDecideRequest(selectedRequest,selectedPlant,requestUser))return;
  deciding=true;reqEl('confirmDecision').disabled=true;reqEl('cancelDecision').disabled=true;reqEl('decisionStatus').className='';reqEl('decisionStatus').textContent='Guardando decisión…';
  try{
    const updated=await submitRequestDecision(decision);
    if(updated.id_solicitud!==selectedRequest.id_solicitud||updated.estado!==decision)throw new Error('No se pudo confirmar la decisión. Recarga para consultar el estado.');
    selectedRequest={...selectedRequest,...updated,nombre_adoptante:updated.nombre_adoptante||selectedRequest.nombre_adoptante,nombre_planta:updated.nombre_planta||selectedRequest.nombre_planta};if(decision==='ACEPTADA')selectedPlant.estado_planta='SOLICITADA';renderRequestDetail();reqEl('decisionStatus').textContent=decision==='ACEPTADA'?'Solicitud aceptada. La adopción está en proceso.':'Solicitud rechazada.';
  }catch(error){reqEl('decisionStatus').className='error';reqEl('decisionStatus').textContent=error.message;}
  finally{deciding=false;decision=null;reqEl('decisionDialog').close();reqEl('confirmDecision').disabled=false;reqEl('cancelDecision').disabled=false;}
}
reqEl('acceptRequest').addEventListener('click',()=>openDecision('ACEPTADA'));reqEl('rejectRequest').addEventListener('click',()=>openDecision('RECHAZADA'));reqEl('confirmDecision').addEventListener('click',confirmRequestDecision);
['closeDecision','cancelDecision'].forEach(id=>reqEl(id).addEventListener('click',()=>{if(!deciding){decision=null;reqEl('decisionDialog').close();}}));reqEl('decisionDialog').addEventListener('cancel',event=>{if(deciding)event.preventDefault();});
reqEl('requestPlant').addEventListener('change',()=>loadRequestList());reqEl('requestState').addEventListener('change',()=>loadRequestList());reqEl('moreRequests').addEventListener('click',()=>loadRequestList(false));reqEl('retryRequests').addEventListener('click',initializeRequests);
initializeRequests();
