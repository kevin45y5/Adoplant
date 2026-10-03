'use strict';
const el = id => document.getElementById(id);
let recoveryEmail = '';
let busy = false;
let resendAt = 0;
let expiresAt = 0;
function showStep(step) {
  document.body.dataset.step = String(step);
  el('asideTitle').textContent = step === 1 ? 'La llave de tu santuario verde' : 'Protege tu santuario verde';
  ['requestForm', 'codeForm', 'resetForm', 'success'].forEach((id, index) => {
    el(id).hidden = index !== step - 1;
  });
  el('stepLabel').textContent = ['PASO 1 DE 3 Â· RECUPERACIÓN SEGURA', 'PASO 2 DE 3 Â· CÓDIGO DE RECUPERACIÓN', 'PASO 3 DE 3 Â· NUEVA CONTRASEÑA', 'ACCESO RECUPERADO'][step - 1];
  el('message').hidden = true;
}
setInterval(() => {
  const remaining = Math.max(0, Math.ceil((expiresAt - Date.now()) / 1000));
  el('timer').textContent = remaining ? 'Válido por ' + Math.floor(remaining / 60) + ':' + String(remaining % 60).padStart(2, '0') + ' min' : 'Código vencido. Solicita otro.';
  const wait = Math.max(0, Math.ceil((resendAt - Date.now()) / 1000));
  el('resend').textContent = wait ? 'Reenviar en ' + wait + ' s' : 'Reenviar código';
  el('resend').disabled = busy || wait > 0;
}, 1000);

function message(text, error = false) {
  el('message').textContent = text;
  el('message').className = error ? 'error' : '';
  el('message').hidden = false;
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll('button').forEach(button => {
    button.disabled = value;
    if (button.dataset.loading) {
      if (!button.dataset.label) button.dataset.label = button.textContent;
      button.textContent = value ? button.dataset.loading : button.dataset.label;
    }
  });
  el('resend').disabled = value || Date.now() < resendAt;
}

async function request(path, body) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(window.ADOPPLANT_API_URL + '/auth/' + path, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body), signal: controller.signal,
    });
    const data = await response.json().catch(() => {
      if (response.ok) throw new Error('No se pudo confirmar la respuesta del servidor. Intenta nuevamente.');
      return {};
    });
    if (!response.ok) {
      if (response.status === 404) throw new Error(path === 'verificar-codigo' ? 'La verificación de códigos todavía no está disponible en el servidor. Intenta más tarde.' : 'No se encontró el servicio de recuperación. Comprueba que la web esté actualizada.');
      if (response.status >= 500) throw new Error('El servicio no está disponible en este momento. Intenta nuevamente.');
      const detail = data.detail;
      throw new Error(typeof detail === 'string' ? detail : (Array.isArray(detail) ? detail.map(item => item.msg).join('. ') : 'No se pudo completar la solicitud.'));
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('El servidor tardó demasiado. Intenta nuevamente.');
    if (error instanceof TypeError) throw new Error('No se pudo conectar con el servidor. Revisa tu conexión.');
    throw error;
  } finally { clearTimeout(timeout); }
}

async function sendCode(email) {
  setBusy(true);
  try {
    const data = await request('recuperacion', { correo: email });
    recoveryEmail = email;
    resendAt = Date.now() + 60000;
    expiresAt = Date.now() + 15 * 60000;
    const [name, domain] = email.split('@');
    el('destination').textContent = name.slice(0, 2) + '•••@' + domain;
    el('resetForm').reset();
    el('password').type = el('confirmation').type = 'password';
    el('strengthBar').style.width = '0';
    showStep(2);
    el('code').value = '';
    syncCodeSlots();
    message(data.mensaje || 'Si la cuenta está registrada y activa, recibirás un código.');
    el('code').focus();
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
}

el('requestForm').addEventListener('submit', async event => {
  event.preventDefault();
  if (busy || !event.currentTarget.reportValidity()) return;
  await sendCode(el('email').value.trim());
});

el('resend').addEventListener('click', async () => {
  if (busy) return;
  if (Date.now() < resendAt) {
    message('Espera ' + Math.ceil((resendAt - Date.now()) / 1000) + ' segundos antes de pedir otro código.');
    return;
  }
  await sendCode(recoveryEmail);
});

el('changeEmail').addEventListener('click', () => {
  if (busy) return;
  el('resetForm').reset();
  el('password').type = el('confirmation').type = 'password';
  showStep(1);
  el('code').value = '';
    syncCodeSlots();
  recoveryEmail = '';
  el('message').hidden = true;
  el('email').focus();
});

el('codeForm').addEventListener('submit', async event => {
  event.preventDefault();
  if (busy || !event.currentTarget.reportValidity()) return;
  if (Date.now() >= expiresAt) { message('El código venció. Solicita uno nuevo.', true); return; }
  setBusy(true);
  try {
    await request('verificar-codigo', { correo: recoveryEmail, codigo: el('code').value });
    showStep(3);
    el('password').focus();
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});
el('backToCode').addEventListener('click', () => { if (!busy) { showStep(2); el('code').focus(); } });
el('password').addEventListener('input', event => {
  const value = event.target.value;
  const score = [value.length >= 8, /\p{L}/u.test(value), /\p{Nd}/u.test(value), value.length >= 12].filter(Boolean).length;
  el('strengthBar').style.width = value ? score * 25 + '%' : '0';
});

el('showPassword').addEventListener('change', event => {
  el('password').type = el('confirmation').type = event.target.checked ? 'text' : 'password';
});

el('resetForm').addEventListener('submit', async event => {
  event.preventDefault();
  if (busy || !event.currentTarget.reportValidity()) return;
  const password = el('password').value;
  if (!/\p{L}/u.test(password) || !/\p{Nd}/u.test(password)) {
    message('La contraseña debe incluir al menos una letra y un número.', true); return;
  }
  if (password !== el('confirmation').value) {
    message('Las contraseñas no coinciden.', true); return;
  }
  setBusy(true);
  try {
    await request('restablecer-contrasena', {
      correo: recoveryEmail, codigo: el('code').value,
      nueva_contrasena: password, confirmar_contrasena: el('confirmation').value,
    });
    el('resetForm').reset();
    el('code').value = '';
    syncCodeSlots();
    recoveryEmail = '';
    showStep(4);
    el('success').querySelector('a').focus();
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});

function syncCodeSlots() {
  const digits = el('code').value.replace(/[^0-9]/g, '').slice(0, 8);
  el('code').value = digits;
  document.querySelectorAll('.code-slots span').forEach((slot, index) => { slot.textContent = digits[index] || ''; });
}
el('code').addEventListener('input', syncCodeSlots);
