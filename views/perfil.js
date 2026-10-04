'use strict';
const profileEl=id=>document.getElementById(id);
const profileFields={nombre:'profileFirstName',apellido:'profileLastName',correo:'profileMail',telefono:'profilePhone'};
const profileToken=sessionStorage.getItem('token');
let profileUser=null,profileEditing=false,profileSaving=false;
function profileLogout(){sessionStorage.removeItem('token');localStorage.removeItem('token');localStorage.removeItem('user');profileEl('profileContent').hidden=true;window.location.replace('/views/index.html');}
function profileMessage(text,error=false){profileEl('profileMessage').textContent=text;profileEl('profileMessage').className='status'+(error?' error':'');}
async function profileApi(options={}){
  if(!profileToken||sessionStorage.getItem('token')!==profileToken){window.location.replace('/views/index.html');throw new Error('Inicia sesión para consultar tu perfil.');}
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
  try{
    const response=await fetch(window.ADOPPLANT_API_URL+'/usuarios/me',{...options,headers:{Authorization:'Bearer '+profileToken,'Content-Type':'application/json'},cache:'no-store',signal:controller.signal});
    if(response.status===401||response.status===403){profileLogout();throw new Error('Tu sesión venció. Vuelve a iniciar sesión.');}
    const data=await response.json();
    if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:Array.isArray(data.detail)?data.detail.map(d=>d.msg).join('. '):'No se pudo guardar el perfil.');
    if(sessionStorage.getItem('token')!==profileToken)throw new Error('Tu sesión cambió. Recarga la página.');
    if(!Number.isInteger(data.id_usuario)||Object.keys(profileFields).some(key=>typeof data[key]!=='string'))throw new Error('No se pudo confirmar la respuesta del servidor.');
    return data;
  }catch(error){if(error.name==='AbortError')throw new Error('El servidor tardó demasiado. Vuelve a consultar tu perfil antes de reintentar.');throw error;}finally{clearTimeout(timer);}
}
function renderProfile(){
  profileEl('profileName').textContent=profileUser.nombre+' '+profileUser.apellido;
  profileEl('profileEmail').textContent=profileUser.correo;
  const since=new Date(profileUser.fecha_registro);
  profileEl('profileSince').textContent=Number.isNaN(since.getTime())?'':'Miembro desde '+since.toLocaleDateString('es-SV');
  Object.entries(profileFields).forEach(([field,id])=>{profileEl(id).value=profileUser[field];});
}
function editProfile(editing){profileEditing=editing;Object.values(profileFields).forEach(id=>{profileEl(id).readOnly=!editing;});profileEl('profileEdit').hidden=editing;profileEl('profileEditActions').hidden=!editing;}
async function loadProfile(){
  profileEl('profileRetry').hidden=true;profileEl('profileStatus').textContent='Cargando tu perfil…';
  try{profileUser=await profileApi();renderProfile();editProfile(false);profileEl('profileContent').hidden=false;profileEl('profileStatus').textContent='';}
  catch(error){profileEl('profileStatus').textContent=error.message;profileEl('profileRetry').hidden=false;}
}
profileEl('profileEdit').onclick=()=>{if(!profileUser||profileSaving)return;profileMessage('');editProfile(true);profileEl('profileFirstName').focus();};
profileEl('profileCancel').onclick=()=>{if(profileSaving)return;renderProfile();editProfile(false);profileMessage('');};
profileEl('profileForm').onsubmit=async event=>{
  event.preventDefault();if(!profileEditing||profileSaving||!event.currentTarget.reportValidity())return;
  const changes={};for(const [field,id] of Object.entries(profileFields)){const value=profileEl(id).value.trim();if(!value){profileMessage('Completa todos los campos.',true);profileEl(id).focus();return;}if(value!==profileUser[field])changes[field]=value;}
  if(!Object.keys(changes).length){editProfile(false);profileMessage('No hay cambios para guardar.');return;}
  profileSaving=true;profileEl('profileSave').disabled=true;profileEl('profileCancel').disabled=true;Object.values(profileFields).forEach(id=>{profileEl(id).readOnly=true;});profileMessage('Guardando cambios…');
  try{profileUser=await profileApi({method:'PATCH',body:JSON.stringify(changes)});renderProfile();editProfile(false);profileMessage('Tu perfil se actualizó correctamente.');}
  catch(error){profileMessage(error.message,true);}
  finally{profileSaving=false;profileEl('profileSave').disabled=false;profileEl('profileCancel').disabled=false;editProfile(profileEditing);}
};
profileEl('profileLogout').onclick=profileLogout;profileEl('profileRetry').onclick=loadProfile;
loadProfile();
