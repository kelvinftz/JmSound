/**
 * Authentication Manager
 * Gerencia sessão e autenticação do usuário
 */

// Check if user is authenticated
function checkAuth() {
    const user = sessionStorage.getItem('user');
    const token = sessionStorage.getItem('token');
    
    if (!user || !token) {
        window.location.href = '/index.html';
        return false;
    }
    
    // Update username in navbar if element exists
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = user;
    }
    
    return true;
}

// Logout function
function logout() {
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('token');
    window.location.href = '/index.html';
}

// Setup logout button
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // Check auth on protected pages
    if (!window.location.pathname.includes('index.html')) {
        checkAuth();
    }
});

// API Helper
const API = {
    baseURL: '',
    
    async request(endpoint, options = {}) {
        const token = sessionStorage.getItem('token');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(this.baseURL + endpoint, {
                ...options,
                headers
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    logout();
                    throw new Error('Sessão expirada');
                }
                throw new Error(`HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

// Load alerts for navbar
async function loadNavbarAlerts() {
    try {
        const response = await API.get('/api/notificacoes');
        const alertas = response.data || [];
        const count = alertas.length;
        
        // Update badges
        const navBadge = document.getElementById('navAlertBadge');
        const navCount = document.getElementById('navAlertCount');
        const menuBadge = document.getElementById('menuAlertBadge');
        
        if (count > 0) {
            if (navBadge) {
                navBadge.textContent = count;
                navBadge.classList.remove('d-none');
            }
            if (navCount) {
                navCount.textContent = count;
            }
            if (menuBadge) {
                menuBadge.textContent = count;
                menuBadge.classList.remove('d-none');
            }
        }
        
        // Update list
        const navList = document.getElementById('navAlertList');
        if (navList && alertas.length > 0) {
            navList.innerHTML = alertas.slice(0, 5).map(alerta => `
                <li class="dropdown-notifications-item">
                    <div class="d-flex">
                        <div class="flex-shrink-0 me-3">
                            <div class="avatar">
                                <span class="avatar-initial rounded-circle bg-label-danger">
                                    <i class="fas fa-exclamation-triangle"></i>
                                </span>
                            </div>
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${alerta.nome}</h6>
                            <p class="mb-0">Estoque: ${alerta.quantidade_estoque} / Mínimo: ${alerta.minimo_alerta}</p>
                            <small class="text-muted">${alerta.codigo}</small>
                        </div>
                    </div>
                </li>
            `).join('');
        } else if (navList) {
            navList.innerHTML = '<li class="text-center py-3"><small class="text-muted">Nenhum alerta</small></li>';
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Load alerts on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadNavbarAlerts);
} else {
    loadNavbarAlerts();
}
