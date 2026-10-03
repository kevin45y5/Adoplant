const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

function setup(file, token) {
  const elements = {}, calls = [], redirects = [], values = new Map();
  if (token) values.set('token', token);
  const el = id => elements[id] ??= {value:'', hidden:true, handlers:{},
    classList:{add(){}, remove(){}}, addEventListener(k,v){this.handlers[k]=v;}};
  let response = {ok:true,status:200,json:async()=>({access_token:'test-token',nombre:'Ana',correo:'ana@example.com',telefono:'12345678'})};
  const context = {document:{getElementById:el,querySelector:()=>null,addEventListener(){}},
    sessionStorage:{getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)},
    localStorage:{removeItem(){}}, window:{addEventListener(){},location:{replace:u=>redirects.push(u)}},
    fetch:async(url,options)=>{calls.push({url,options});return response;},
    AbortController,setTimeout:()=>0,clearTimeout(){}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../views/',file),'utf8'),context);
  return {el,calls,redirects,values,context,reply:r=>response=r};
}
const tick = () => new Promise(resolve=>setImmediate(resolve));
test('registro acepta letras Unicode como el backend',async()=>{
  const s=setup('main.js');
  for (const [id,value] of Object.entries({regFirstName:'Ana',regLastName:'Prueba',regEmail:'ana@example.com',regPhoneCode:'+503',regPhone:'12345678',regPassword:'ñññññññ1',regPasswordConfirm:'ñññññññ1'})) s.el(id).value=value;
  await s.context.handleRegister({preventDefault(){}});
  assert.equal(s.calls.length,1);
  assert.equal(s.calls[0].url,'/api/auth/registro');
});
test('login con teléfono guarda sesión y abre inicio; credenciales inválidas no redirigen',async()=>{
  const s=setup('main.js'); s.el('loginEmail').value='11113333';s.el('loginPassword').value='Prueba123';
  await s.context.handleLogin({preventDefault(){}});
  assert.equal(JSON.parse(s.calls[0].options.body).identificador,'11113333');
  assert.equal(s.calls[0].url,'/api/auth/login');
  assert.equal(s.values.get('token'),'test-token');
  assert.deepEqual(s.redirects,['/views/inicio.html']);
  s.redirects.length=0;
  s.el('loginPassword').value='Incorrecta123';
  s.reply({ok:false,status:401,json:async()=>({detail:'Credenciales inválidas'})});
  await s.context.handleLogin({preventDefault(){}});
  assert.equal(s.redirects.length,0);
  assert.equal(s.el('toastMessage').textContent,'Credenciales inválidas');
});
test('registro muestra conflicto sin anunciar éxito',async()=>{
  const s=setup('main.js');
  for (const [id,value] of Object.entries({regFirstName:'Ana',regLastName:'Prueba',regEmail:'ana@example.com',regPhoneCode:'+503',regPhone:'12345678',regPassword:'Prueba123',regPasswordConfirm:'Prueba123'})) s.el(id).value=value;
  s.reply({ok:false,status:409,json:async()=>({detail:'El correo ya está en uso'})});
  await s.context.handleRegister({preventDefault(){}});
  assert.equal(s.calls[0].url,'/api/auth/registro');
  assert.equal(s.el('toastMessage').textContent,'El correo ya está en uso');
  assert.equal(s.context.window._redirectAfterModal,undefined);
  s.reply({ok:true,status:201,json:async()=>({})});
  await s.context.handleRegister({preventDefault(){}});
  assert.equal(s.context.window._redirectAfterModal,'/views/index.html');
});
test('inicio requiere token y obtiene perfil real; cerrar sesión borra token',async()=>{
  const missing=setup('inicio.js');assert.deepEqual(missing.redirects,['/views/index.html']);
  assert.equal(missing.calls.length,0);
  const s=setup('inicio.js','test-token');await tick();
  assert.equal(s.calls[0].url,'/api/usuarios/me');
  assert.equal(s.calls[0].options.headers.Authorization,'Bearer test-token');
  assert.equal(s.el('greeting').textContent,'Hola, Ana');assert.equal(s.el('welcome').hidden,false);
  s.el('logout').handlers.click();assert.equal(s.values.has('token'),false);
  assert.equal(s.el('welcome').hidden,true);
});
test('sesión bloqueada o vencida vuelve al login sin mostrar perfil',async()=>{
  for (const status of [401,403]) {
    const s=setup('inicio.js','test-token');await tick();
    s.reply({ok:false,status});await s.context.checkSession();
    assert.equal(s.values.has('token'),false);assert.equal(s.el('welcome').hidden,true);
    assert.deepEqual(s.redirects,['/views/index.html']);
  }
});
