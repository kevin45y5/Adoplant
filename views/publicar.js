'use strict';
const pubEl = id => document.getElementById(id);
const publicationFields = ['nombre','id_categoria','tamano','nivel_cuidado','necesidad_luz','necesidad_agua','estado_salud','ubicacion','descripcion'];
let publishedPlant = null;
let editingPublication = false;
let publicationUser = null, publishing = false, previewUrl = null, booting = false;
function pubMessage(text, error=false) {pubEl('formMessage').hidden=false;pubEl('formMessage').textContent=text;pubEl('formMessage').className=error?'error':'';}
function endPublicationSession() {sessionStorage.removeItem('token');window.location.replace('/views/index.html');}
async function publicationRequest(path, options={}) {
 const token=sessionStorage.getItem('token');if(!token){endPublicationSession();throw new Error('Inicia sesión para publicar.');}
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),90000);
 try {const response=await fetch(window.ADOPPLANT_API_URL+path,{...options,headers:{Authorization:'Bearer '+token},signal:controller.signal,cache:'no-store'});
 if(response.status===401||response.status===403){endPublicationSession();throw new Error('Tu sesión no está disponible. Vuelve a iniciar sesión.');}
 const data=await response.json().catch(()=>{throw new Error('No se pudo confirmar la respuesta. Revisa el catálogo antes de volver a publicar.');});
 if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:Array.isArray(data.detail)?data.detail.map(d=>d.msg).join('. '):'No se pudo completar la solicitud.');
 if(sessionStorage.getItem('token')!==token)throw new Error('Tu sesión cambió. Recarga la página.');return data;
 }catch(error){if(error.name==='AbortError')throw new Error('El servidor tardó demasiado. Revisa el catálogo antes de volver a publicar para evitar duplicados.');throw error;}finally{clearTimeout(timer);}
}
async function initializePublication() {
 if(booting)return;booting=true;pubEl('retryPage').hidden=true;
 try {publicationUser=await publicationRequest('/usuarios/me');const categories=await publicationRequest('/categorias');if(!Array.isArray(categories))throw new Error('No se pudieron cargar las categorías.');
 const select=pubEl('plantCategory');while(select.options.length>1)select.remove(1);
 categories.filter(c=>c.estado==='ACTIVA').forEach(c=>{const option=document.createElement('option');option.value=c.id_categoria;option.textContent=c.nombre;select.append(option);});
 if(select.options.length===1)throw new Error('No hay categorías activas para publicar. Intenta más tarde.');
 pubEl('publishForm').hidden=false;pubEl('pageStatus').textContent='';
 try {const saved=JSON.parse(sessionStorage.getItem('plantDraft:'+publicationUser.id_usuario)||'null');if(saved){publicationFields.forEach(name=>{if(typeof saved[name]==='string')pubEl('publishForm').elements.namedItem(name).value=saved[name];});pubMessage('Borrador recuperado. Adjunta nuevamente la fotografía antes de publicar.');}}catch(_){/* Un borrador inválido no impide publicar. */}
 }catch(error){pubEl('pageStatus').textContent=error.message;pubEl('retryPage').hidden=false;}finally{booting=false;}
}
function validatePublicationPhoto(file) {
 if(!file)throw new Error('Adjunta una fotografía de tu planta.');
 if(!['image/jpeg','image/png','image/webp'].includes(file.type))throw new Error('Selecciona una imagen JPG, PNG o WebP.');
 if(file.size>8*1024*1024)throw new Error('La fotografía no debe superar 8 MB.');
}
pubEl('photograph').addEventListener('change',()=>{
 const file=pubEl('photograph').files[0];pubEl('photoError').hidden=true;
 if(previewUrl){URL.revokeObjectURL(previewUrl);previewUrl=null;}
 pubEl('photoPreview').hidden=true;pubEl('photoPlaceholder').hidden=false;
 try{validatePublicationPhoto(file);previewUrl=URL.createObjectURL(file);pubEl('photoPreview').src=previewUrl;pubEl('photoPreview').hidden=false;pubEl('photoPlaceholder').hidden=true;}
 catch(error){pubEl('photograph').value='';pubEl('photoError').textContent=error.message;pubEl('photoError').hidden=false;}
});
pubEl('photoPreview').addEventListener('error',()=>{pubEl('photograph').value='';pubEl('photoPreview').hidden=true;pubEl('photoPlaceholder').hidden=false;pubEl('photoError').textContent='No se pudo leer la imagen. Selecciona otra fotografía.';pubEl('photoError').hidden=false;});
pubEl('saveDraft').addEventListener('click',()=>{if(!publicationUser||publishing)return;const data=new FormData(pubEl('publishForm'));const draft={};publicationFields.forEach(name=>draft[name]=String(data.get(name)||''));try{sessionStorage.setItem('plantDraft:'+publicationUser.id_usuario,JSON.stringify(draft));pubMessage('Borrador guardado en esta sesión. La fotografía no se guarda.');}catch(_){pubMessage('No se pudo guardar el borrador en este navegador.',true);}});
pubEl('publishForm').addEventListener('submit',async event=>{
 event.preventDefault();if(publishing||!publicationUser||!event.currentTarget.reportValidity())return;
 try{if(!editingPublication || pubEl('photograph').files[0]) validatePublicationPhoto(pubEl('photograph').files[0]);}catch(error){pubMessage(error.message,true);return;}
 const form=pubEl('publishForm');const data=new FormData(form);
 if(editingPublication && !pubEl('photograph').files[0])data.delete('fotografia');
 for(const name of publicationFields){const value=String(data.get(name)||'').trim();if(name!=='descripcion'&&!value){pubMessage('Completa todos los campos obligatorios.',true);return;}data.set(name,value);}
 publishing=true;pubEl('publishButton').disabled=true;pubEl('saveDraft').disabled=true;pubEl('publishButton').textContent='Publicando…';pubMessage('Estamos guardando tu planta y su fotografía.');
 try{const plant=await publicationRequest(editingPublication ? '/plantas/'+publishedPlant.id_planta : '/plantas',{method:editingPublication?'PATCH':'POST',body:data});if(!Number.isInteger(plant.id_planta))throw new Error('No se pudo confirmar la publicación. Revisa el catálogo antes de volver a intentarlo.');
 try{sessionStorage.removeItem('plantDraft:'+publicationUser.id_usuario);}catch(_){}
 showPublicationSuccess(plant);
 form.reset();if(previewUrl){URL.revokeObjectURL(previewUrl);previewUrl=null;}pubEl('publishSuccess').scrollIntoView({behavior:'smooth',block:'center'});
 }catch(error){pubMessage(error instanceof TypeError?'No se pudo confirmar la publicación. Revisa tu conexión y el catálogo antes de reintentar.':error.message,true);}
 finally{publishing=false;pubEl('publishButton').disabled=false;pubEl('saveDraft').disabled=false;pubEl('publishButton').textContent=editingPublication?'Guardar cambios →':'Publicar planta →';}
});
pubEl('retryPage').addEventListener('click',initializePublication);
window.addEventListener('beforeunload',event=>{if(publishing){event.preventDefault();event.returnValue='';}});
function showPublicationSuccess(plant) {
 publishedPlant=plant;
 try {sessionStorage.setItem('catalogPublishedPlant',String(plant.id_planta));}catch(_){}
 pubEl('publishForm').hidden=true;pubEl('publicationHeading').hidden=true;pubEl('publishSuccess').hidden=false;
 pubEl('successTitle').textContent=editingPublication?'¡Publicación actualizada con éxito!':'¡Publicación creada con éxito!';
 pubEl('successMessage').textContent='Tu planta ahora aparece como disponible para adopción en la comunidad de PlantHaven.';
 pubEl('successPlantName').textContent=plant.nombre;
 pubEl('successCategory').textContent=plant.categoria?.nombre || 'Una nueva compañera verde';
 pubEl('successLocation').textContent='⌖ '+(plant.ubicacion || 'Ubicación por consultar');
 pubEl('successSize').textContent='↕ '+(plant.tamano || 'Tamaño por consultar');
 pubEl('successCare').textContent='♧ '+(plant.nivel_cuidado || 'Cuidados por consultar');
 pubEl('successReference').textContent='REF. PH-'+plant.id_planta;
 const photo=pubEl('successPhoto');photo.alt=plant.nombre;photo.onerror=()=>{photo.onerror=null;photo.src='/views/icon.jpeg';};
 let source='/views/icon.jpeg';try {const url=new URL(plant.fotografia_url);if(['https:','http:'].includes(url.protocol))source=url.href;}catch(_){}
 photo.src=source;
 pubEl('successTitle').focus();
}
pubEl('editPublication').addEventListener('click',()=>{
 if(!publishedPlant || publishing)return;
 editingPublication=true;
 const form=pubEl('publishForm');
 publicationFields.forEach(name=>{form.elements.namedItem(name).value=String(publishedPlant[name] ?? '');});
 pubEl('photograph').required=false;
 pubEl('photoPreview').src=pubEl('successPhoto').src;pubEl('photoPreview').hidden=false;pubEl('photoPlaceholder').hidden=true;
 pubEl('publishSuccess').hidden=true;pubEl('publicationHeading').hidden=false;form.hidden=false;
 pubEl('publishButton').textContent='Guardar cambios →';pubEl('saveDraft').hidden=true;
 pubMessage('Edita los datos de tu publicación. Si no seleccionas otra fotografía, conservaremos la actual.');
 form.scrollIntoView({behavior:'smooth',block:'start'});
});
initializePublication();
