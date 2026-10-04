const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
function setup(token='session'){
  const nodes=new Map(),calls=[];let redirect='',failure=null;
  let user={id_usuario:7,nombre:'Lucía',apellido:'Pérez',correo:'lucia@example.com',telefono:'71234567',fecha_registro:'2026-10-03T12:00:00Z'};
  const el=id=>{if(!nodes.has(id))nodes.set(id,{value:'',hidden:true,readOnly:true,disabled:false,focus(){},reportValidity(){return true;}});return nodes.get(id);};
  const context={document:{getElementById:el},window:{ADOPPLANT_API_URL:'https://api.example/api',location:{replace:url=>redirect=url}},sessionStorage:{getItem:()=>token,removeItem:()=>token=null},localStorage:{removeItem(){}},AbortController,setTimeout,clearTimeout,Date,fetch:async(url,options)=>{
    calls.push({url,...options});if(failure)return {ok:false,status:failure.status,json:async()=>({detail:failure.detail})};
    if(options.method==='PATCH')user={...user,...JSON.parse(options.body)};
    return {ok:true,status:200,json:async()=>({...user})};
  }};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../views/perfil.js'),'utf8'),context);
  return {el,calls,redirect:()=>redirect,fail:(status,detail)=>failure={status,detail},submit:()=>el('profileForm').onsubmit({preventDefault(){},currentTarget:el('profileForm')})};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
test('consulta perfil real, permite editar y conserva solo los cambios confirmados',async()=>{
  const s=setup();await tick();assert.equal(s.el('profileName').textContent,'Lucía Pérez');assert.equal(s.el('profileFirstName').readOnly,true);
  s.el('profileEdit').onclick();s.el('profileFirstName').value='Ana';await s.submit();
  assert.equal(s.calls[1].url,'https://api.example/api/usuarios/me');assert.equal(s.calls[1].headers.Authorization,'Bearer session');assert.deepEqual(JSON.parse(s.calls[1].body),{nombre:'Ana'});
  assert.equal(s.el('profileName').textContent,'Ana Pérez');assert.equal(s.el('profileFirstName').readOnly,true);
  s.el('profileEdit').onclick();s.el('profileFirstName').value='Cambio sin guardar';s.el('profileCancel').onclick();assert.equal(s.el('profileFirstName').value,'Ana');
});
test('correo duplicado mantiene los datos guardados y permite corregir el formulario',async()=>{
  const s=setup();await tick();s.el('profileEdit').onclick();s.el('profileMail').value='ocupado@example.com';s.fail(409,'El correo electrónico ya está registrado');await s.submit();
  assert.equal(s.el('profileEmail').textContent,'lucia@example.com');assert.equal(s.el('profileMail').value,'ocupado@example.com');assert.equal(s.el('profileMail').readOnly,false);assert.match(s.el('profileMessage').textContent,/ya está registrado/);
});
test('sin sesión no consulta datos y cerrar sesión oculta el perfil',async()=>{
  const empty=setup(null);await tick();assert.equal(empty.calls.length,0);assert.equal(empty.redirect(),'/views/index.html');
  const s=setup();await tick();s.el('profileLogout').onclick();assert.equal(s.el('profileContent').hidden,true);assert.equal(s.redirect(),'/views/index.html');
});
