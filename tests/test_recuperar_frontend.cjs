const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function setup(status) {
  const elements = new Map();
  const calls = [];
  function el(id) {
    if (!elements.has(id)) elements.set(id, {
      value: '', hidden: true, style: {}, dataset: {}, handlers: {},
      addEventListener(type, handler) { this.handlers[type] = handler; },
      focus() {}, reportValidity() { return true; },
    });
    return elements.get(id);
  }
  const context = {
    document: {body: {dataset: {}}, getElementById: el, querySelectorAll: () => []},
    window: {ADOPPLANT_API_URL: 'https://api.example.test/api'},
    Date, AbortController, setTimeout, clearTimeout, setInterval() {},
    async fetch(url, options) {
      calls.push({url, body: JSON.parse(options.body)});
      return {ok: status === 200, status, async json() {
        return status === 200 ? {mensaje: 'Código verificado'} : {detail: 'Código inválido, vencido o utilizado'};
      }};
    },
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../views/recuperar.js'), 'utf8'), context);
  vm.runInContext("recoveryEmail = 'prueba@example.com'; expiresAt = Date.now() + 60000; showStep(2);", context);
  el('code').value = '12345678';
  return {el, context, calls, submit: () => el('codeForm').handlers.submit({preventDefault() {}, currentTarget: el('codeForm')})};
}

for (const status of [400, 404, 500]) {
  test(`no avanza si la API responde ${status}`, async () => {
    const app = setup(status);
    await app.submit();
    assert.equal(app.el('codeForm').hidden, false);
    assert.equal(app.el('resetForm').hidden, true);
    assert.equal(app.el('message').hidden, false);
    assert.equal(app.context.document.body.dataset.step, '2');
  });
}
test('avanza solamente después de verificar código y correo en la API', async () => {
  const app = setup(200);
  await app.submit();
  assert.equal(app.calls[0].url, 'https://api.example.test/api/auth/verificar-codigo');
  assert.deepEqual(app.calls[0].body, {correo: 'prueba@example.com', codigo: '12345678'});
  assert.equal(app.el('resetForm').hidden, false);
  assert.equal(app.context.document.body.dataset.step, '3');
});
