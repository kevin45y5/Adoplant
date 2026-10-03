'use strict';
const el = id => document.getElementById(id);
let recoveryEmail = '';
let busy = false;
let resendAt = 0;

function message(text, error = false) {
  el('message').textContent = text;
  el('message').className = error ? 'error' : '';
  el('message').hidden = false;
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll('button').forEach(button => { button.disabled = value; });
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
      if (response.status === 404) throw new Error('No se encontró el servicio de recuperación. Comprueba que la web esté actualizada.');
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
    el('destination').textContent = 'Correo: ' + email;
    el('requestForm').hidden = true;
    el('resetForm').hidden = false;
    el('code').value = '';
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
  el('resetForm').hidden = true;
  el('requestForm').hidden = false;
  el('message').hidden = true;
  el('email').focus();
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
    el('resetForm').hidden = true;
    el('message').hidden = true;
    el('success').hidden = false;
    el('success').querySelector('a').focus();
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});
