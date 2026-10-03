const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

function setup() {
  const elements = {};
  function el(id) {
    return elements[id] ??= {value:'', hidden: true, handlers: {},
      addEventListener(name, handler) { this.handlers[name] = handler; },
      focus() {}, reportValidity() {return true;}, reset() {}, querySelector() {return {focus(){}};},
    };
  }
  const calls = [];
  let response = {ok: true, status:202, json: async()=>({mensaje:'Solicitud recibida'})};
  const context = {window: {}, document: {getElementById: el, querySelectorAll:()=>[]},
    fetch: async(url, options)=> {calls.push({url, body:JSON.parse(options.body)}); return response;},
    AbortController, setTimeout, clearTimeout, Date, TypeError,
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../views/config.js'), 'utf8'), context);
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../views/recuperar.js'), 'utf8'), context);
  return {el, calls, reply(value) {response=value;},
    async submit(id) { await el(id).handlers.submit({preventDefault(){}, currentTarget:el(id)}); },
  };
}

test('envía código y valida junto a contraseña; no usa una ruta de verificación', async()=> {
  const s=setup();
  s.el('email').value='prueba@example.com';
  await s.submit('requestForm');
  assert.equal(s.calls[0].url, 'https://adopplant-api.onrender.com/api/auth/recuperacion');
  assert.equal(s.el('resetForm').hidden, false);
  s.el('code').value='00123456';
  s.el('password').value=s.el('confirmation').value='NuevaPrueba123';
  s.reply({ok:false, status:400, json:async()=>({detail:'Código inválido o vencido'})});
  await s.submit('resetForm');
  assert.equal(s.calls[1].url, 'https://adopplant-api.onrender.com/api/auth/restablecer-contrasena');
  assert.equal(s.calls[1].body.codigo,'00123456');
  assert.equal(s.el('success').hidden,true);
  assert.equal(s.el('resetForm').hidden,false);
  s.reply({ok:true, status:200, json:async()=>({})});
  await s.submit('resetForm');
  assert.equal(s.el('success').hidden,false);
  assert.equal(s.el('resetForm').hidden,true);
});

test('confirmación distinta no envía petición; 404 no se presenta como código inválido', async()=> {
  const s=setup();
  s.el('password').value='NuevaPrueba123'; s.el('confirmation').value='Diferente123';
  await s.submit('resetForm');
  assert.equal(s.calls.length,0);
  assert.match(s.el('message').textContent,/no coinciden/);
  s.el('email').value='prueba@example.com';
  s.reply({ok:false,status:404,json:async()=>({detail:'Not Found'})});
  await s.submit('requestForm');
  assert.match(s.el('message').textContent,/servicio de recuperación/);
  assert.equal(s.el('resetForm').hidden,true);
});

test('respuesta ilegible no anuncia contraseña actualizada', async()=> {
  const s=setup();
  s.el('email').value='prueba@example.com';
  await s.submit('requestForm');
  s.el('code').value='00123456';
  s.el('password').value=s.el('confirmation').value='NuevaPrueba123';
  s.reply({ok:true,status:200,json:async()=>{throw new SyntaxError('Invalid JSON');}});
  await s.submit('resetForm');
  assert.equal(s.el('success').hidden,true);
  assert.equal(s.el('resetForm').hidden,false);
  assert.match(s.el('message').textContent,/respuesta/i);
});
