const API_URL = '/api';

async function authRequest(path, options) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60000);
    try {
        const response = await fetch(API_URL + path, {...options, signal: controller.signal});
        const data = await response.json();
        return {res: response, data};
    } finally {
        clearTimeout(timeout);
    }
}

function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const pass = document.getElementById('loginPassword').value;

    if (!email || !pass) {
        showNotification('Completa todos los campos');
        return;
    }

    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Conectando...';

    try {
        const {res, data} = await authRequest('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identificador: email, contrasena: pass })
        });

        if (res.ok) {
            sessionStorage.setItem('token', data.access_token);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            document.getElementById('loginPassword').value = '';
            window.location.replace('/views/inicio.html');
        } else {
            showNotification(typeof data.detail === 'string' ? data.detail : 'Credenciales inválidas');
        }
    } catch (err) {
        showNotification('No se pudo conectar con el servidor');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Iniciar sesión</span><i class="fa-solid fa-arrow-right text-sm"></i>';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const firstName = document.getElementById('regFirstName').value.trim();
    const lastName = document.getElementById('regLastName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const codeSelect = document.getElementById('regPhoneCode');
    const codigo = codeSelect ? codeSelect.value : '+503';
    const numeroLocal = document.getElementById('regPhone').value.trim();
    const phone = numeroLocal.charAt(0) === '+' ? numeroLocal : codigo + ' ' + numeroLocal;
    const pass = document.getElementById('regPassword').value;
    const passConfirm = document.getElementById('regPasswordConfirm').value;

    if (!firstName || !lastName || !email || !numeroLocal || !pass || !passConfirm) {
        showNotification('Completa todos los campos');
        return;
    }

    if (pass !== passConfirm) {
        showNotification('Las contraseñas no coinciden. Por favor verifica.');
        return;
    }

    const hasLetter = /\p{L}/u.test(pass);
    const hasNumber = /\p{Nd}/u.test(pass);
    if (pass.length < 8 || !hasLetter || !hasNumber) {
        showNotification('La contraseña debe tener mínimo 8 caracteres, al menos una letra y un número.');
        return;
    }

    if (phone.length > 20) {
        showNotification('El número de teléfono no puede superar 20 caracteres.');
        return;
    }

    const btn = document.getElementById('registerBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creando...';

    try {
        const {res, data} = await authRequest('/auth/registro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nombre: firstName,
                apellido: lastName,
                correo: email,
                telefono: phone,
                contrasena: pass,
                confirmar_contrasena: passConfirm
            })
        });

        if (res.ok) {
            window._redirectAfterModal = '/views/index.html';
            openWelcomeModal('¡Cuenta Creada Con Éxito!', 'Bienvenido a PlantHaven, ' + firstName + ' ' + lastName + '. Tu cuenta con correo ' + email + ' ha sido registrada.');
        } else {
            if (Array.isArray(data.detail)) {
                showNotification(data.detail.map(function(e){ return e.msg; }).join(', '));
            } else {
                showNotification(typeof data.detail === 'string' ? data.detail : 'Error al registrar');
            }
        }
    } catch (err) {
        showNotification('No se pudo conectar con el servidor');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Crear cuenta</span><i class="fa-solid fa-arrow-right text-xs"></i>';
    }
}

function openWelcomeModal(title, message) {
    const modal = document.getElementById('welcomeModal');
    const modalContent = document.getElementById('modalContent');
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalMessage').textContent = message;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(function() {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeWelcomeModal() {
    const modal = document.getElementById('welcomeModal');
    const modalContent = document.getElementById('modalContent');
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    setTimeout(function() {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        if (window._redirectAfterModal) {
            const url = window._redirectAfterModal;
            window._redirectAfterModal = null;
            window.location.href = url;
        }
    }, 200);
}

function showNotification(msg) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMessage');

    toastMsg.textContent = msg;
    toast.classList.remove('translate-y-[-100px]', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(function() {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-[-100px]', 'opacity-0');
    }, 3500);
}

function showHelpModal() {
    openWelcomeModal('¿Necesitas ayuda?', 'Puedes entrar con tu correo o con el teléfono completo que registraste, incluido el prefijo si lo agregaste. Si olvidaste tu contraseña, utiliza el enlace de recuperación del formulario.');
}

function alinearEncabezados() {
    const h1 = document.querySelector('main h1');
    const header = document.getElementById('loginHeader');
    const hero = document.getElementById('loginHero');
    if (!h1 || !header || !hero) return;

    hero.style.marginTop = '0px';
    if (window.innerWidth < 768) {
        hero.style.marginTop = '';
        return;
    }

    const cont = hero.parentElement;
    let delta = h1.getBoundingClientRect().top - header.getBoundingClientRect().top;
    const max = cont.clientHeight - hero.offsetHeight - 70;
    if (delta < 0) delta = 0;
    if (delta > max) delta = max;
    hero.style.marginTop = Math.max(0, delta - 100) + 'px';  
}

window.addEventListener('load', alinearEncabezados);
window.addEventListener('resize', alinearEncabezados);
