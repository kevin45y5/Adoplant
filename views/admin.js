'use strict';
const adm=id=>document.getElementById(id),adminToken=sessionStorage.getItem('token');
let adminUser=null,adminTab='usuarios',adminPage=1,adminRows=[],adminBusy=false,adminPending=null,adminVersion=0;
const adminNode=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
async function adminApi(path,options={}){
 if(!adminToken||sessionStorage.getItem('token')!==adminToken){window.location.replace('/views/index.html');throw new Error('Inicia sesión.');}
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
 try{const r=await fetch(window.ADOPPLANT_API_URL+'/admin'+path,{...options,headers:{Authorization:'Bearer '+adminToken,'Content-Type':'application/json'},cache:'no-store',signal:controller.signal});
 if(r.status===401||r.status===403){adminUser=null;adm('adminPanel').hidden=true;throw new Error('Tu cuenta no tiene acceso de administrador o la sesión venció.');}
 const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:'No se pudo completar la operación.');if(sessionStorage.getItem('token')!==adminToken)throw new Error('La sesión cambió.');return data;
 }catch(e){if(e.name==='AbortError')throw new Error('El servidor tardó demasiado. Consulta el estado antes de reintentar.');throw e;}finally{clearTimeout(timer);}
}
function adminAction(row){
 if(adminTab==='usuarios')return {path:'/usuarios/'+row.id_usuario+'/estado',body:{estado:row.estado==='ACTIVO'?'BLOQUEADO':'ACTIVO'},title:row.estado==='ACTIVO'?'Bloquear usuario':'Reactivar usuario',description:row.nombre+' · '+row.correo};
 if(adminTab==='plantas')return {path:'/plantas/'+row.id_planta+'/moderacion',body:{visible:!row.visible,eliminada:false},reason:true,title:row.visible?'Ocultar publicación':'Mostrar publicación',description:row.nombre};
 return {path:'/reportes/'+row.id_reporte,body:{estado:row.estado==='EN_REVISION'?'RESUELTO':'EN_REVISION'},title:row.estado==='EN_REVISION'?'Resolver reporte':'Reabrir reporte',description:row.motivo};
}
function renderAdminRows(){
 const columns=adminTab==='usuarios'?['Usuario','Correo','Estado','Acción']:adminTab==='plantas'?['Publicación','Donante','Visibilidad','Acción']:['Reporte','Motivo','Estado','Acción'];
 const head=adminNode('tr');columns.forEach(label=>head.append(adminNode('th',label)));adm('adminHead').replaceChildren(head);adm('adminRows').replaceChildren();
 for(const row of adminRows){const tr=adminNode('tr');let values;
 if(adminTab==='usuarios')values=[row.nombre+' '+row.apellido,row.correo,row.estado];else if(adminTab==='plantas')values=[row.nombre+' · #'+row.id_planta,'Usuario #'+row.id_usuario,row.eliminada?'Retirada':row.visible?'Visible':'Oculta'];else values=['#'+row.id_reporte,row.motivo,row.estado];
 values.forEach(value=>tr.append(adminNode('td',value)));const cell=adminNode('td'),action=adminAction(row),button=adminNode('button',action.title);button.className='row-action';button.disabled=(adminTab==='usuarios'&&row.id_usuario===adminUser.id_usuario)||(adminTab==='plantas'&&row.eliminada);button.onclick=()=>{adminPending=action;adm('adminDialogTitle').textContent=action.title;adm('adminDialogText').textContent=action.description;adm('adminReason').value='';adm('adminReason').hidden=!action.reason;adm('adminReasonLabel').hidden=!action.reason;adm('adminActionStatus').textContent='';adm('adminDialog').showModal();};cell.append(button);tr.append(cell);adm('adminRows').append(tr);}
 adm('adminEmpty').hidden=adminRows.length>0;adm('adminPage').textContent='Página '+adminPage;adm('adminPrev').disabled=adminPage===1;
}
async function loadAdminRows(){
 if(!adminUser)return;const version=++adminVersion;adm('adminStatus').textContent='Cargando…';adm('retryAdmin').hidden=true;
 try{const query=adm('adminQuery').value.trim(),offset=(adminPage-1)*20;let path;
 if(adminTab==='usuarios')path='/usuarios?limite=20&pagina='+adminPage+'&buscar='+encodeURIComponent(query);else if(adminTab==='plantas')path='/plantas?limit=20&skip='+offset+'&q='+encodeURIComponent(query);else path='/reportes?limit=20&skip='+offset;
 const data=await adminApi(path);if(version!==adminVersion)return;adminRows=adminTab==='usuarios'?data.usuarios:data;if(!Array.isArray(adminRows))throw new Error('Respuesta inválida.');renderAdminRows();adm('adminNext').disabled=adminTab==='usuarios'?adminPage*20>=data.total:adminRows.length<20;adm('adminStatus').textContent='';
 }catch(e){if(version===adminVersion){adm('adminStatus').textContent=e.message;adm('retryAdmin').hidden=false;}}
}
async function initializeAdmin(){try{adminUser=await adminApi('/me');adm('adminIdentity').textContent='Hola, '+adminUser.nombre+'. Gestiona los usuarios, publicaciones y reportes.';adm('adminPanel').hidden=false;await loadAdminRows();}catch(e){adm('adminIdentity').textContent='Acceso restringido';adm('adminStatus').textContent=e.message;adm('retryAdmin').hidden=false;}}
document.querySelectorAll('[data-admin-tab]').forEach(button=>button.onclick=()=>{if(adminBusy)return;adminTab=button.dataset.adminTab;adminPage=1;adm('adminQuery').value='';adm('adminSearch').hidden=adminTab==='reportes';document.querySelectorAll('[data-admin-tab]').forEach(b=>b.classList.toggle('selected',b===button));loadAdminRows();});
adm('adminSearch').onsubmit=event=>{event.preventDefault();adminPage=1;loadAdminRows();};adm('adminPrev').onclick=()=>{if(adminPage>1){adminPage--;loadAdminRows();}};adm('adminNext').onclick=()=>{adminPage++;loadAdminRows();};adm('retryAdmin').onclick=initializeAdmin;
adm('adminCancel').onclick=()=>{if(!adminBusy){adminPending=null;adm('adminDialog').close();}};adm('adminDialog').addEventListener('cancel',e=>{if(adminBusy)e.preventDefault();else adminPending=null;});
adm('adminConfirm').onclick=async()=>{if(adminBusy||!adminPending)return;const action=adminPending,body={...action.body};if(action.reason){body.motivo=adm('adminReason').value.trim();if(!body.motivo){adm('adminActionStatus').textContent='Escribe el motivo para continuar.';return;}}
 adminBusy=true;adm('adminConfirm').disabled=true;adm('adminCancel').disabled=true;
 try{await adminApi(action.path,{method:'PATCH',body:JSON.stringify(body)});adm('adminDialog').close();adminPending=null;await loadAdminRows();}catch(e){adm('adminActionStatus').textContent=e.message;}finally{adminBusy=false;adm('adminConfirm').disabled=false;adm('adminCancel').disabled=false;}
};initializeAdmin();
