function salvarToken(token, userData) {
    localStorage.setItem(CONFIG.TOKEN_KEY, token);
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(userData));
}

function getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
}

function getUser() {
    const user = localStorage.getItem(CONFIG.USER_KEY);
    return user ? JSON.parse(user) : null;
}

function isAuthenticated() {
    return !!getToken();
}

function isVendedor() {
    const user = getUser();
    return user && (user.role === 'vendedor' || user.role === 'admin' || user.role === 'root');
}

function isAdmin() {
    const user = getUser();
    return user && (user.role === 'admin' || user.role === 'root');
}

function logout() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
    window.location.href = 'login.html';
}

function getAuthHeaders() {
    const token = getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function verificarAutenticacao(redirectIfNot = true) {
    if (!isAuthenticated() && redirectIfNot) {
        const protectedPages = ['perfil.html', 'carrinho.html', 'checkout.html', 
                                'meus-pedidos.html', 'dashboard-vendedor.html', 'mensagens.html'];
        const currentPage = window.location.pathname.split('/').pop();
        
        if (protectedPages.includes(currentPage)) {
            window.location.href = 'login.html';
            return false;
        }
    }
    return true;
}

async function fazerLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    loading(true);
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro ao fazer login');
        }
        
        salvarToken(data.token, data.usuario);
        mostrarMensagem('Login realizado com sucesso!');
        
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

async function fazerCadastro(event) {
    event.preventDefault();
    
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    const confirmarSenha = document.getElementById('confirmar-senha')?.value;
    
    if (senha !== confirmarSenha) {
        mostrarMensagem('As senhas não conferem', 'error');
        return;
    }
    
    loading(true);
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/auth/registrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, email, senha })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro ao cadastrar');
        }
        
        mostrarMensagem('Cadastro realizado! Faça login.');
        
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

function atualizarMenuUsuario() {
    const userMenu = document.getElementById('user-menu');
    if (!userMenu) return;
    
    if (isAuthenticated()) {
        const user = getUser();
        userMenu.innerHTML = `
            <div class="dropdown">
                <button class="dropdown-btn">👤 ${user.nome.split(' ')[0]}</button>
                <div class="dropdown-content">
                    <a href="perfil.html">Meu Perfil</a>
                    <a href="meus-pedidos.html">Meus Pedidos</a>
                    ${isVendedor() ? '<a href="dashboard-vendedor.html">Meus Produtos</a>' : ''}
                    <a href="mensagens.html">Mensagens</a>
                    <hr>
                    <a href="#" onclick="logout()">Sair</a>
                </div>
            </div>
        `;
    } else {
        userMenu.innerHTML = `
            <a href="login.html" class="btn-outline">Entrar</a>
            <a href="cadastro.html" class="btn-primary">Cadastrar</a>
        `;
    }
}