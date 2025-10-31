/**
 * Produtos Controller
 * Gerencia CRUD de produtos
 */

let produtos = [];
let editingId = null;

// Load all produtos
async function loadProdutos(searchTerm = '') {
    try {
        const url = searchTerm ? `/api/produtos?busca=${encodeURIComponent(searchTerm)}` : '/api/produtos';
        const response = await API.get(url);
        produtos = response.data || [];
        renderProdutosTable();
    } catch (error) {
        console.error('Error loading produtos:', error);
        alert('Erro ao carregar produtos');
    }
}

// Render produtos table
function renderProdutosTable() {
    const tbody = document.getElementById('produtosTableBody');
    
    if (produtos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhum produto encontrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = produtos.map(produto => {
        const isLow = produto.quantidade_estoque <= produto.minimo_alerta;
        const statusBadge = isLow 
            ? '<span class="badge bg-danger"><i class="fas fa-exclamation-triangle me-1"></i>Baixo</span>'
            : '<span class="badge bg-success"><i class="fas fa-check me-1"></i>OK</span>';
        
        return `
            <tr class="${isLow ? 'table-danger' : ''}">
                <td><strong>${produto.codigo}</strong></td>
                <td>
                    <div class="d-flex flex-column">
                        <span class="fw-semibold">${produto.nome}</span>
                        <small class="text-muted">${produto.descricao || '-'}</small>
                    </div>
                </td>
                <td>R$ ${produto.valor_unitario.toFixed(2)}</td>
                <td><strong>${produto.quantidade_estoque}</strong></td>
                <td>${produto.minimo_alerta}</td>
                <td>${statusBadge}</td>
                <td>
                    <div class="dropdown">
                        <button type="button" class="btn btn-sm btn-icon" data-bs-toggle="dropdown">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <div class="dropdown-menu">
                            <a class="dropdown-item" href="javascript:void(0);" onclick="openModalEdit(${produto.id})">
                                <i class="fas fa-edit me-2"></i>Editar
                            </a>
                            <a class="dropdown-item text-danger" href="javascript:void(0);" onclick="deleteProduto(${produto.id})">
                                <i class="fas fa-trash me-2"></i>Excluir
                            </a>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Open modal for create
function openModalCreate() {
    editingId = null;
    document.getElementById('produtoModalTitle').textContent = 'Novo Produto';
    document.getElementById('produtoForm').reset();
    document.getElementById('produtoId').value = '';
}

// Open modal for edit
async function openModalEdit(id) {
    editingId = id;
    document.getElementById('produtoModalTitle').textContent = 'Editar Produto';
    
    try {
        const response = await API.get(`/api/produtos/${id}`);
        const produto = response.data;
        
        document.getElementById('produtoId').value = produto.id;
        document.getElementById('produtoNome').value = produto.nome;
        document.getElementById('produtoCodigo').value = produto.codigo;
        document.getElementById('produtoValor').value = produto.valor_unitario;
        document.getElementById('produtoEstoque').value = produto.quantidade_estoque;
        document.getElementById('produtoMinimo').value = produto.minimo_alerta;
        document.getElementById('produtoDescricao').value = produto.descricao || '';
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('produtoModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading produto:', error);
        alert('Erro ao carregar produto');
    }
}

// Save produto (create or update)
async function saveProduto(e) {
    e.preventDefault();
    
    const produtoData = {
        nome: document.getElementById('produtoNome').value,
        codigo: document.getElementById('produtoCodigo').value,
        valor_unitario: parseFloat(document.getElementById('produtoValor').value),
        quantidade_estoque: parseInt(document.getElementById('produtoEstoque').value),
        minimo_alerta: parseInt(document.getElementById('produtoMinimo').value),
        descricao: document.getElementById('produtoDescricao').value || ''
    };
    
    try {
        if (editingId) {
            // Update
            await API.put(`/api/produtos/${editingId}`, produtoData);
            alert('Produto atualizado com sucesso!');
        } else {
            // Create
            await API.post('/api/produtos', produtoData);
            alert('Produto criado com sucesso!');
        }
        
        // Close modal and reload
        const modal = bootstrap.Modal.getInstance(document.getElementById('produtoModal'));
        modal.hide();
        loadProdutos();
        
    } catch (error) {
        console.error('Error saving produto:', error);
        alert('Erro ao salvar produto: ' + (error.message || 'Erro desconhecido'));
    }
}

// Delete produto
async function deleteProduto(id) {
    if (!confirm('Tem certeza que deseja excluir este produto?')) {
        return;
    }
    
    try {
        await API.delete(`/api/produtos/${id}`);
        alert('Produto excluído com sucesso!');
        loadProdutos();
    } catch (error) {
        console.error('Error deleting produto:', error);
        alert('Erro ao excluir produto');
    }
}

// Search handler
let searchTimeout;
function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const searchTerm = document.getElementById('searchInput').value;
        loadProdutos(searchTerm);
    }, 500);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadProdutos();
    
    // Setup search
    document.getElementById('searchInput').addEventListener('input', handleSearch);
    
    // Setup form submit
    document.getElementById('produtoForm').addEventListener('submit', saveProduto);
});
