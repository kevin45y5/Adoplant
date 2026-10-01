const API_URL = 'http://127.0.0.1:8000/api';

function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    }
}

function toggleForm(view) {
    const loginView = document.getElementById('loginView');
    const registerView = document.getElementById('registerView');
    const toggleLoginText = document.getElementById('toggleLoginText');
    const toggleRegisterText = document.getElementById('toggleRegisterText');
    const pageTitle = document.getElementById('pageTitle');
    const pageSubtitle = document.getElementById('pageSubtitle');

    if (view === 'register') {
        loginView.classList.add('hidden');
        registerView.classList.remove('hidden');
        toggleLoginText.classList.add('hidden');
        toggleRegisterText.classList.remove('hidden');
        pageTitle.textContent = 'Crear cuenta';
        pageSubtitle.textContent = 'Únete a PlantHaven y descubre el mundo vegetal';
    } else {
        registerView.classList.add('hidden');
        loginView.classList.remove('hidden');
        toggleRegisterText.classList.add('hidden');
        toggleLoginText.classList.remove('hidden');
        pageTitle.textContent = 'Bienvenido de nuevo';
        pageSubtitle.textContent = 'Ingresa tus credenciales para acceder';
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
        btn.innerHTML = '<span>Iniciar Sesión</span><i class="fa-solid fa-arrow-right text-sm"></i>';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const firstName = document.getElementById('regFirstName').value.trim();
    const lastName = document.getElementById('regLastName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const phone = document.getElementById('regPhone').value.trim();
    const pass = document.getElementById('regPassword').value;
    const passConfirm = document.getElementById('regPasswordConfirm').value;

    if (pass !== passConfirm) {
        showNotification('Las contraseñas no coinciden');
        return;
    }

    const hasLetter = /[a-zA-Z]/.test(pass);
    const hasNumber = /[0-9]/.test(pass);
    if (pass.length < 8 || !hasLetter || !hasNumber) {
        showNotification('Mín. 8 caracteres, una letra y un número');
        return;
    }

    const btn = document.getElementById('registerBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creando...';

    try {
        const res = await fetch(API_URL + '/auth/registro', {
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

        const data = await res.json();

        if (res.ok) {
            openWelcomeModal('¡Cuenta creada!', 'Bienvenido, ' + firstName + ' ' + lastName + '.');
            toggleForm('login');
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
        btn.innerHTML = '<span>Registrarse</span><i class="fa-solid fa-arrow-right text-sm"></i>';
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
    }, 200);
}

function showNotification(message) {
    const toast = document.getElementById('toast');
    document.getElementById('toastMessage').textContent = message;
    toast.classList.remove('translate-y-[-100px]', 'opacity-0');
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(function() {
        toast.classList.add('translate-y-[-100px]', 'opacity-0');
    }, 3500);
}
