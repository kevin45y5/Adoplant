'use strict';
const chatEl=id=>document.getElementById(id);
let chatUser=null,currentChat=null,chats=[],chatRows=[],busySend=false,loadingMessages=false,currentPage=1,selectionVersion=0;
let previewPosition=null,previewVersion=0,sharing=null,watchId=null,shareTimer=null,shareExpiry=null,liveSending=false;
const chatToken=sessionStorage.getItem('token');
const receivedMaps=new Map();
const renderedMessages=new Map();
const chatNode=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls;if(text!==undefined)n.textContent=text;return n;};
async function chatApi(path,options={}){
  if(!chatToken||sessionStorage.getItem('token')!==chatToken){window.location.replace('/views/index.html');throw new Error('Inicia sesión para consultar tus mensajes.');}
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
  try{const response=await fetch(window.ADOPPLANT_API_URL+path,{...options,headers:{Authorization:'Bearer '+chatToken,'Content-Type':'application/json'},cache:'no-store',signal:controller.signal});
    if(response.status===401){sessionStorage.removeItem('token');window.location.replace('/views/index.html');}
    const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'No se pudo completar la operación.');
    if(sessionStorage.getItem('token')!==chatToken)throw new Error('La sesión cambió.');return data;
  }catch(error){if(error.name==='AbortError')throw new Error('El servidor tardó demasiado. Revisa el chat antes de volver a enviar.');throw error;}finally{clearTimeout(timer);}
}
function photo(img,plant){img.alt=plant.nombre||'Planta';img.onerror=()=>{img.onerror=null;img.src='/views/icon.jpeg';};try{const url=new URL(plant.fotografia_url);if(!['https:','http:'].includes(url.protocol))throw new Error();img.src=url.href;}catch(_){img.src='/views/icon.jpeg';}}
function mapFrame(p,key){const frame=(key&&receivedMaps.get(key))||chatNode('iframe','map-frame');frame.title='Mapa de la ubicación compartida';frame.loading='lazy';frame.referrerPolicy='no-referrer';const src=ChatLocation.mapUrl(p);if(frame.src!==src)frame.src=src;if(key)receivedMaps.set(key,frame);return frame;}
function renderChats(){
  const query=chatEl('chatSearch').value.toLocaleLowerCase();chatEl('chatList').replaceChildren();
  for(const chat of chats.filter(c=>c.plant.nombre.toLocaleLowerCase().includes(query))){const button=chatNode('button','chat-item'+(currentChat?.id_chat===chat.id_chat?' selected':''));const img=chatNode('img','');photo(img,chat.plant);const text=chatNode('span','');text.append(chatNode('strong','',chat.plant.nombre),chatNode('small','','Coordinar entrega · #'+chat.id_chat));button.append(img,text);button.onclick=()=>selectChat(chat);chatEl('chatList').append(button);}
  if(!chats.length)chatEl('chatList').append(chatNode('p','','Todavía no tienes conversaciones. Abre el chat desde una solicitud aceptada.'));
}
function renderMessages(){
  const list=chatEl('messageList'),bottom=list.scrollHeight-list.scrollTop-list.clientHeight<80;
  const keys=new Set();
  const position=new Map();
  const messageKey=row=>{const p=ChatLocation.fromMessage(row);return p&&p.kind!=='point'?'live:'+row.id_usuario+':'+p.session:'message:'+row.id_mensaje;};
  chatRows.forEach((row,index)=>{const key=messageKey(row);if(!position.has(key))position.set(key,index);});
  const rows=ChatLocation.latest(chatRows).sort((a,b)=>position.get(messageKey(a))-position.get(messageKey(b)));
  for(const [index,row] of rows.entries()){
    const location=ChatLocation.fromMessage(row),mine=Number(row.id_usuario)===Number(chatUser.id_usuario);
    const key=location&&location.kind!=='point'?'live:'+row.id_usuario+':'+location.session:'message:'+row.id_mensaje;
    keys.add(key);
    let entry=renderedMessages.get(key);
    if(!entry){entry={bubble:chatNode('article',''),signature:null};renderedMessages.set(key,entry);}
    const bubble=entry.bubble,signature=JSON.stringify([row,location&&ChatLocation.active(location)]);
    if(signature!==entry.signature){
      bubble.className='message'+(mine?' mine':'')+(location?' location':'');
      if(location&&location.kind!=='stop'){
        if(!entry.map){
          entry.title=chatNode('strong','');entry.label=chatNode('p','');
          entry.map=mapFrame(location,key);entry.link=chatNode('a','map-link','Cómo llegar ↗');
          entry.link.target='_blank';entry.link.rel='noopener noreferrer';
          entry.updated=chatNode('small','');entry.time=chatNode('small','');
          bubble.replaceChildren(entry.title,entry.label,entry.map,entry.link,entry.updated,entry.time);
        }
        entry.title.textContent=location.kind==='point'?'⌖ Punto de encuentro':ChatLocation.active(location)?'● Ubicación en tiempo real':'⌖ Última ubicación · sin actualización en vivo';
        entry.label.textContent=location.label||'Ubicación compartida';
        // Keep the iframe attached: polling and new text must not reload its document.
        mapFrame(location,key);
        entry.link.href='https://www.google.com/maps/dir/?api=1&destination='+location.lat+','+location.lng;
        entry.updated.textContent='Actualizada: '+new Date(location.at).toLocaleTimeString('es-SV');
      }else{
        entry.map=null;receivedMaps.delete(key);entry.time=chatNode('small','');
        bubble.replaceChildren(chatNode(location?'strong':'p','',location?'Ubicación en tiempo real finalizada':row.contenido||''),entry.time);
      }
      entry.time.textContent=(mine?'Tú':'Participante')+' · '+new Date(row.fecha_hora).toLocaleString('es-SV');
      entry.signature=signature;
    }
    if(list.children[index]!==bubble)list.insertBefore(bubble,list.children[index]||null);
  }
  for(const [key,entry] of renderedMessages){if(!keys.has(key)){entry.bubble.remove();renderedMessages.delete(key);receivedMaps.delete(key);}}
  if(!rows.length&&!list.children.length){const bubble=chatNode('p','','Saluda y acuerda el lugar y la hora de entrega.');list.append(bubble);renderedMessages.set('empty',{bubble});}
  if(bottom)list.scrollTop=list.scrollHeight;
}
async function loadMessages(older=false){
  if(!currentChat||loadingMessages)return;loadingMessages=true;const id=currentChat.id_chat,version=selectionVersion;
  try{
    const first=await chatApi('/chats/'+id+'/mensajes?tamano_pagina=100&pagina=1');
    const last=Math.max(1,Math.ceil(first.total/100));
    const start=older?Math.max(1,currentPage-1):chatRows.length?Math.min(currentPage,last):last;
    const rows=[];for(let page=start;page<=last;page++){const result=page===1?first:await chatApi('/chats/'+id+'/mensajes?tamano_pagina=100&pagina='+page);rows.push(...result.mensajes);}
    if(version!==selectionVersion)return;currentPage=start;chatRows=rows;renderMessages();chatEl('olderMessages').hidden=start===1;
  }catch(error){chatEl('chatStatus').textContent=error.message;}finally{loadingMessages=false;}
}
async function selectChat(chat){
  if(sharing)await stopSharing();receivedMaps.clear();renderedMessages.clear();currentChat=chat;selectionVersion++;chatRows=[];currentPage=1;chatEl('chatEmpty').hidden=true;chatEl('chatPanel').hidden=false;chatEl('chatTitle').textContent='Chat sobre '+chat.plant.nombre;photo(chatEl('chatPhoto'),chat.plant);chatEl('chatPlantLink').href='/views/planta.html?id='+chat.id_planta;renderChats();chatEl('messageList').replaceChildren();await loadMessages();
}
async function sendContent(chatId,contenido){return chatApi('/chats/'+chatId+'/mensajes',{method:'POST',body:JSON.stringify(ChatLocation.requestBody(contenido))});}
chatEl('messageForm').onsubmit=async event=>{event.preventDefault();if(!currentChat||busySend)return;const value=chatEl('messageText').value.trim();if(!value)return;busySend=true;chatEl('sendMessage').disabled=true;const id=currentChat.id_chat;try{await sendContent(id,value);chatEl('messageText').value='';chatEl('chatStatus').textContent='';await loadMessages();chatEl('messageList').scrollTop=chatEl('messageList').scrollHeight;}catch(error){chatEl('chatStatus').textContent=error.message;}finally{busySend=false;chatEl('sendMessage').disabled=false;}};
function geoError(error){return error.code===1?'Permite el acceso a tu ubicación en el navegador para compartirla.':error.code===3?'No se pudo obtener la ubicación a tiempo. Intenta nuevamente.':'No se pudo obtener tu ubicación. Revisa el GPS del dispositivo.';}
chatEl('openLocation').onclick=()=>{if(!currentChat)return;previewVersion++;previewPosition=null;chatEl('sendLocation').disabled=true;chatEl('locationStatus').textContent='';chatEl('liveOption').checked=false;chatEl('locationPreview').replaceChildren(chatNode('p','','Usa tu ubicación actual para ver el mapa.'));chatEl('locationDialog').showModal();};
function closeLocation(){previewVersion++;chatEl('locationDialog').close();}
chatEl('closeLocation').onclick=closeLocation;chatEl('cancelLocation').onclick=closeLocation;
chatEl('locationDialog').addEventListener('cancel',()=>{previewVersion++;});
chatEl('locateMe').onclick=()=>{
  if(!navigator.geolocation||!window.isSecureContext){chatEl('locationStatus').textContent='La ubicación requiere HTTPS o localhost y un navegador compatible.';return;}
  const version=++previewVersion;chatEl('locationStatus').textContent='Buscando tu ubicación…';chatEl('sendLocation').disabled=true;
  navigator.geolocation.getCurrentPosition(position=>{if(version!==previewVersion)return;previewPosition={lat:position.coords.latitude,lng:position.coords.longitude,at:position.timestamp};chatEl('locationPreview').replaceChildren(mapFrame(previewPosition));chatEl('locationStatus').textContent='Precisión aproximada: '+Math.round(position.coords.accuracy)+' metros. Revisa el punto antes de enviarlo.';chatEl('sendLocation').disabled=false;},error=>{if(version===previewVersion)chatEl('locationStatus').textContent=geoError(error);},{enableHighAccuracy:true,timeout:15000,maximumAge:0});
};
function clearTracking(){if(watchId!==null)navigator.geolocation.clearWatch(watchId);watchId=null;clearInterval(shareTimer);clearTimeout(shareExpiry);shareTimer=null;shareExpiry=null;}
async function stopSharing(){
  const old=sharing;sharing=null;clearTracking();chatEl('stopLocation').hidden=true;chatEl('liveStatus').textContent='Ubicación en tiempo real detenida.';
  if(old){try{if(old.pending)await old.pending;await sendContent(old.chatId,ChatLocation.encode({kind:'stop',session:old.session}));await loadMessages();}catch(_){chatEl('liveStatus').textContent='Seguimiento detenido. Sin conexión: la otra persona verá el último punto como desactualizado.';}}
}
async function updateLive(){
  const live=sharing;if(!live||liveSending||!live.position)return;
  if(Date.now()>=live.until){await stopSharing();return;}
  if(Date.now()-live.position.at>40000){chatEl('liveStatus').textContent='Esperando una nueva señal de ubicación…';return;}
  liveSending=true;const payload={...live.position,kind:'live',session:live.session,until:live.until,label:live.label};
  try{live.pending=sendContent(live.chatId,ChatLocation.encode(payload));await live.pending;if(sharing===live){chatEl('liveStatus').textContent='● Compartiendo ubicación · hasta '+new Date(live.until).toLocaleTimeString('es-SV');await loadMessages();}}
  catch(_){chatEl('liveStatus').textContent='No se pudo actualizar la ubicación. Reintentando…';}finally{liveSending=false;live.pending=null;}
}
chatEl('sendLocation').onclick=async()=>{
  if(!previewPosition||!currentChat)return;const button=chatEl('sendLocation');if(button.disabled)return;button.disabled=true;
  if(Date.now()-previewPosition.at>60000){chatEl('locationStatus').textContent='Actualiza tu ubicación antes de enviarla.';return;}
  const live=chatEl('liveOption').checked,id=currentChat.id_chat,session=crypto.randomUUID(),label=chatEl('locationLabel').value.trim(),until=Date.now()+15*60000;
  try{
    if(sharing)await stopSharing();
    await sendContent(id,ChatLocation.encode({...previewPosition,kind:live?'live':'point',session,label,until}));
    if(live){sharing={chatId:id,session,label,until,position:previewPosition};chatEl('stopLocation').hidden=false;chatEl('liveStatus').textContent='● Compartiendo ubicación en tiempo real';
      watchId=navigator.geolocation.watchPosition(position=>{if(sharing?.session===session)sharing.position={lat:position.coords.latitude,lng:position.coords.longitude,at:position.timestamp};},error=>{chatEl('liveStatus').textContent=geoError(error);if(error.code===1)stopSharing();},{enableHighAccuracy:true,maximumAge:5000,timeout:20000});
      shareTimer=setInterval(updateLive,15000);shareExpiry=setTimeout(stopSharing,15*60000);
    }
    closeLocation();await loadMessages();
  }catch(error){chatEl('locationStatus').textContent=error.message;}finally{button.disabled=false;}
};
chatEl('stopLocation').onclick=stopSharing;chatEl('olderMessages').onclick=()=>loadMessages(true);chatEl('chatSearch').oninput=renderChats;
window.addEventListener('pagehide',()=>{sharing=null;clearTracking();});
async function initializeChat(){
  chatEl('retryChat').hidden=true;chatEl('chatStatus').textContent='Cargando tus conversaciones…';
  try{chatUser=await chatApi('/usuarios/me');const plantId=new URLSearchParams(window.location.search).get('planta');let opened=null;
    if(plantId){if(!/^[1-9][0-9]*$/.test(plantId))throw new Error('La referencia de planta no es válida.');opened=await chatApi('/chats',{method:'POST',body:JSON.stringify({id_planta:Number(plantId)})});}
    const rows=await chatApi('/chats');chats=await Promise.all(rows.map(async chat=>{let plant={nombre:'Planta #'+chat.id_planta};try{plant=await chatApi('/plantas/'+chat.id_planta);}catch(_){}return {...chat,plant};}));renderChats();chatEl('chatStatus').textContent='';if(opened){const chat=chats.find(c=>c.id_chat===opened.id_chat);if(chat)await selectChat(chat);}else if(chats.length)await selectChat(chats[0]);
  }catch(error){chatEl('chatStatus').textContent=error.message;chatEl('retryChat').hidden=false;}
}
chatEl('retryChat').onclick=initializeChat;
setInterval(()=>{if(document.visibilityState==='visible')loadMessages();if(sessionStorage.getItem('token')!==chatToken){sharing=null;clearTracking();window.location.replace('/views/index.html');}},5000);
initializeChat();
