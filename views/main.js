const API_URL = 'http://127.0.0.1:8000/api';

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
        const res = await fetch(API_URL + '/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identificador: email, contrasena: pass })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', email);
            openWelcomeModal('¡Bienvenido de nuevo!', 'Has iniciado sesión correctamente como ' + email + '.');
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
    openWelcomeModal('¿Necesitas ayuda?', 'Si tienes problemas para acceder a tu cuenta de AdopPlant o requieres soporte, escríbenos a soporte@adoplant.com');
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
