/**
 * Dashboard Controller
 * Gerencia KPIs, gráficos e dados do dashboard
 */

let movimentacoesChart = null;

// Update dashboard date
function updateDashboardDate() {
    const dateElement = document.getElementById('dashboardDate');
    if (dateElement) {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = now.toLocaleDateString('pt-BR', options);
    }
}

// Load Dashboard KPIs
async function loadDashboardKPIs() {
    try {
        const response = await API.get('/api/dashboard/kpis');
        const data = response.data;
        
        // Update KPI cards
        document.getElementById('kpiTotalProdutos').textContent = data.total_produtos;
        document.getElementById('kpiPercAbaixo').textContent = data.perc_abaixo_minimo;
        document.getElementById('kpiCountAbaixo').textContent = `${data.produtos_abaixo_minimo} produtos`;
        document.getElementById('kpiPecasFalta').textContent = data.pecas_em_falta;
        
        // Load Top 10
        loadTop10(data.top_10_menor_estoque);
        
        // Load Chart
        loadMovimentacoesChart(data.entradas_saidas);
        
        // Load Recent Orders
        loadPedidosRecentes(data.pedidos_recentes);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Erro ao carregar dashboard', 'danger');
    }
}

// Load Top 10 Menor Estoque
function loadTop10(produtos) {
    const list = document.getElementById('top10List');
    if (!list) return;
    
    if (!produtos || produtos.length === 0) {
        list.innerHTML = '<li class="text-center py-3"><small class="text-muted">Nenhum produto</small></li>';
        return;
    }
    
    list.innerHTML = produtos.map((produto, index) => {
        const isLow = produto.quantidade_estoque <= produto.minimo_alerta;
        const badgeClass = isLow ? 'bg-danger' : 'bg-success';
        
        return `
            <li class="d-flex mb-4 pb-1">
                <div class="avatar flex-shrink-0 me-3">
                    <span class="avatar-initial rounded ${badgeClass}">
                        ${index + 1}
                    </span>
                </div>
                <div class="d-flex w-100 flex-wrap align-items-center justify-content-between gap-2">
                    <div class="me-2">
                        <h6 class="mb-0">${produto.nome}</h6>
                        <small class="text-muted">${produto.codigo}</small>
                    </div>
                    <div class="user-progress">
                        <small class="fw-semibold ${isLow ? 'text-danger' : 'text-success'}">
                            ${produto.quantidade_estoque} un.
                        </small>
                    </div>
                </div>
            </li>
        `;
    }).join('');
}

// Load Movimentações Chart
function loadMovimentacoesChart(data) {
    const ctx = document.getElementById('movimentacoesChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (movimentacoesChart) {
        movimentacoesChart.destroy();
    }
    
    movimentacoesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Entradas',
                    data: data.entradas,
                    backgroundColor: 'rgba(105, 108, 255, 0.8)',
                    borderColor: 'rgb(105, 108, 255)',
                    borderWidth: 1
                },
                {
                    label: 'Saídas',
                    data: data.saidas,
                    backgroundColor: 'rgba(255, 99, 132, 0.8)',
                    borderColor: 'rgb(255, 99, 132)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Load Pedidos Recentes
function loadPedidosRecentes(pedidos) {
    const tbody = document.getElementById('pedidosRecentesTable');
    if (!tbody) return;
    
    if (!pedidos || pedidos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum pedido recente</td></tr>';
        return;
    }
    
    tbody.innerHTML = pedidos.map(pedido => {
        const statusBadge = getStatusBadge(pedido.status);
        const tipoBadge = pedido.tipo === 'compra' 
            ? '<span class="badge bg-label-primary">Compra</span>'
            : '<span class="badge bg-label-info">Venda</span>';
        
        const data = new Date(pedido.data).toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <tr>
                <td><strong>#${pedido.id}</strong></td>
                <td>${tipoBadge}</td>
                <td>${data}</td>
                <td>${statusBadge}</td>
                <td><small>${pedido.observacoes || '-'}</small></td>
            </tr>
        `;
    }).join('');
}

// Get Status Badge
function getStatusBadge(status) {
    const badges = {
        'pendente': '<span class="badge bg-label-warning">Pendente</span>',
        'pronto': '<span class="badge bg-label-success">Pronto</span>',
        'cancelado': '<span class="badge bg-label-danger">Cancelado</span>'
    };
    return badges[status] || '<span class="badge bg-label-secondary">-</span>';
}

// Toast Notification
function showToast(message, type = 'info') {
    // Simple alert for now
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateDashboardDate();
    loadDashboardKPIs();
    
    // Refresh data every 30 seconds
    setInterval(loadDashboardKPIs, 30000);
});
