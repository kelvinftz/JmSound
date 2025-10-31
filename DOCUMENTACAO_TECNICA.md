# 📚 Documentação Técnica - JmSound Estoque

## Arquitetura do Sistema

### Visão Geral
Sistema web full-stack para controle de estoque automotivo com arquitetura monolítica servindo API REST + frontend estático.

```
┌─────────────────────────────────────────────┐
│           CLIENTE (Navegador)              │
│  HTML + CSS + JavaScript + Bootstrap 5      │
└─────────────────┬───────────────────────────┘
                  │ HTTP/REST
                  ▼
┌─────────────────────────────────────────────┐
│         SERVIDOR FastAPI (Python)          │
├─────────────────────────────────────────────┤
│  ┌─────────────┐      ┌──────────────┐    │
│  │  API REST   │      │   Static     │    │
│  │  Endpoints  │      │   Files      │    │
│  └─────────────┘      └──────────────┘    │
├─────────────────────────────────────────────┤
│         MockDataManager (in-memory)         │
│              ou MySQL (opcional)            │
└─────────────────────────────────────────────┘
```

### Stack Tecnológica

**Backend:**
- Python 3.8+
- FastAPI 0.104+ (framework web assíncrono)
- Pydantic 2.5+ (validação de dados)
- Uvicorn (servidor ASGI)

**Frontend:**
- HTML5 semântico
- CSS3 com Bootstrap 5.3
- JavaScript Vanilla (ES6+)
- Chart.js 4.4 (gráficos)
- Font Awesome 6.4 (ícones)

**Armazenamento:**
- Mock Data (JSON em memória) - padrão
- MySQL 8.0+ (opcional)

---

## Estrutura de Dados

### Produto
```python
{
    "id": int,                      # Auto-increment
    "nome": str,                    # Ex: "Alternador 12V 90A"
    "codigo": str,                  # Ex: "ALT001" (único)
    "valor_unitario": float,        # Ex: 450.00 (> 0)
    "quantidade_estoque": int,      # Ex: 5 (>= 0)
    "minimo_alerta": int,           # Ex: 2 (>= 0)
    "descricao": str | None         # Opcional
}
```

### Pedido
```python
{
    "id": int,
    "tipo": "compra" | "venda",
    "data": str,                    # ISO 8601 datetime
    "status": "pendente" | "pronto" | "cancelado",
    "itens": [ItemPedido],
    "observacoes": str | None
}
```

### ItemPedido
```python
{
    "produto_id": int,
    "quantidade": int,              # > 0
    "valor_unitario": float         # > 0
}
```

### Movimentação
```python
{
    "id": int,
    "produto_id": int,
    "tipo": "entrada" | "saida",
    "quantidade": int,              # > 0
    "referencia_pedido": int | None,
    "data": str,                    # ISO 8601
    "usuario": str                  # Default: "admin"
}
```

---

## API REST - Endpoints

### Autenticação
```
POST /api/auth/login
Body: {"username": str, "password": str}
Response: {"success": bool, "user": str, "token": str}
```

### Produtos

#### Listar todos (com busca)
```
GET /api/produtos?busca={termo}
Response: {"success": bool, "data": [Produto]}
```

#### Buscar por ID
```
GET /api/produtos/{id}
Response: {"success": bool, "data": Produto}
```

#### Criar
```
POST /api/produtos
Body: Produto (sem id)
Response: {"success": bool, "data": Produto, "message": str}
```

#### Atualizar
```
PUT /api/produtos/{id}
Body: Produto
Response: {"success": bool, "data": Produto, "message": str}
```

#### Deletar
```
DELETE /api/produtos/{id}
Response: {"success": bool, "message": str}
```

### Pedidos

#### Listar (com filtros)
```
GET /api/pedidos?tipo={compra|venda}&status={pendente|pronto|cancelado}
Response: {"success": bool, "data": [Pedido]}
```

#### Buscar por ID
```
GET /api/pedidos/{id}
Response: {"success": bool, "data": Pedido}
```

#### Criar
```
POST /api/pedidos
Body: Pedido (sem id, data é gerada automaticamente)
Response: {"success": bool, "data": Pedido, "message": str}
```

#### Atualizar (processa estoque se status = pronto)
```
PUT /api/pedidos/{id}
Body: Pedido
Response: {"success": bool, "data": Pedido, "message": str}
Errors: 400 se estoque insuficiente (venda)
```

#### Deletar
```
DELETE /api/pedidos/{id}
Response: {"success": bool, "message": str}
```

### Movimentações

#### Listar (com filtro)
```
GET /api/movimentacoes?produto_id={id}
Response: {"success": bool, "data": [Movimentacao]}
```

### Dashboard

#### KPIs
```
GET /api/dashboard/kpis
Response: {
    "success": bool,
    "data": {
        "perc_abaixo_minimo": float,
        "pecas_em_falta": int,
        "total_produtos": int,
        "produtos_abaixo_minimo": int,
        "top_10_menor_estoque": [Produto],
        "pedidos_recentes": [Pedido],
        "entradas_saidas": {
            "labels": [str],
            "entradas": [int],
            "saidas": [int]
        },
        "alertas": [Produto]
    }
}
```

#### Notificações
```
GET /api/notificacoes
Response: {
    "success": bool,
    "data": [Produto],  # Produtos com quantidade <= minimo
    "count": int
}
```

---

## Lógica de Negócio

### Processamento de Pedidos

Quando um pedido tem seu status alterado para "pronto":

1. **Validação:**
   - Verifica se o pedido existe
   - Se tipo = "venda", verifica estoque disponível
   - Lança erro HTTP 400 se estoque insuficiente

2. **Atualização de Estoque:**
   - **Compra:** `estoque_atual + quantidade`
   - **Venda:** `estoque_atual - quantidade`

3. **Registro de Movimentação:**
   - Cria registro automático em `movimentacoes`
   - Tipo: "entrada" (compra) ou "saida" (venda)
   - Vincula ao pedido (`referencia_pedido`)

### Alertas de Estoque

Produtos são considerados em alerta quando:
```python
produto.quantidade_estoque <= produto.minimo_alerta
```

Exemplos:
- Estoque = 3, Mínimo = 5 → ALERTA ⚠️
- Estoque = 0, Mínimo = 2 → ALERTA CRÍTICO 🚨
- Estoque = 10, Mínimo = 5 → OK ✅

---

## Frontend - Arquitetura JavaScript

### Módulos

#### auth.js
**Responsabilidades:**
- Verificação de autenticação
- Gestão de sessão (sessionStorage)
- API helper com interceptors
- Logout global
- Carregamento de alertas na navbar

**Funções principais:**
```javascript
checkAuth()                    // Verifica se usuário está logado
logout()                       // Remove sessão e redireciona
API.get(endpoint)              // GET request
API.post(endpoint, data)       // POST request
API.put(endpoint, data)        // PUT request
API.delete(endpoint)           // DELETE request
loadNavbarAlerts()             // Atualiza badges de alerta
```

#### dashboard.js
**Responsabilidades:**
- Carregamento de KPIs
- Renderização de gráficos (Chart.js)
- Atualização de dados em tempo real (30s)

**Funções principais:**
```javascript
loadDashboardKPIs()            // Carrega todos dados do dashboard
loadTop10(produtos)            // Renderiza lista Top 10
loadMovimentacoesChart(data)   // Cria gráfico de barras
loadPedidosRecentes(pedidos)   // Renderiza tabela de pedidos
```

#### produtos.js
**Responsabilidades:**
- CRUD de produtos
- Busca/filtro em tempo real
- Validação de formulários

**Funções principais:**
```javascript
loadProdutos(searchTerm)       // Carrega produtos
renderProdutosTable()          // Renderiza tabela
openModalCreate()              // Abre modal vazio
openModalEdit(id)              // Carrega e abre modal com dados
saveProduto(event)             // Salva (create ou update)
deleteProduto(id)              // Deleta com confirmação
handleSearch()                 // Busca com debounce (500ms)
```

### Padrões de Código

**Nomenclatura:**
- Funções: camelCase (`loadProdutos`)
- Variáveis: camelCase (`produtos`, `editingId`)
- Constantes: UPPER_CASE (`API`)
- Classes: PascalCase (`MockDataManager`)

**Async/Await:**
Todas as chamadas à API usam async/await:
```javascript
async function loadProdutos() {
    try {
        const response = await API.get('/api/produtos');
        produtos = response.data || [];
        renderTable();
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar produtos');
    }
}
```

**Error Handling:**
- Try-catch em todas funções async
- Mensagens user-friendly
- Log de erros no console para debug

---

## Performance & Otimizações

### Backend
1. **Uvicorn com reload** - desenvolvimento
2. **Pydantic validation** - dados validados na entrada
3. **In-memory data** - latência < 5ms (mock)
4. **Lazy loading** - rotas carregadas sob demanda

### Frontend
1. **CDN para bibliotecas** - cache do navegador
2. **Debounce na busca** - reduz requests (500ms)
3. **Eventos delegados** - menos listeners
4. **Gráficos otimizados** - Chart.js com responsive
5. **Fetch API** - nativo, sem jQuery

### Sugestões para Produção
```python
# app.py - produção
uvicorn.run(
    "app:app",
    host="0.0.0.0",
    port=8000,
    reload=False,           # Desabilitar em produção
    log_level="warning",    # Menos verboso
    workers=4               # Múltiplos processos
)
```

---

## Segurança

### Implementado (Demo)
- ✅ Validação de dados (Pydantic)
- ✅ CORS configurado
- ✅ Sessão em memória

### **NÃO** Implementado (Produção Required)
- ❌ Autenticação real (JWT, OAuth2)
- ❌ Hash de senhas
- ❌ HTTPS/SSL
- ❌ Rate limiting
- ❌ SQL injection protection (se usar MySQL)
- ❌ CSRF protection
- ❌ XSS sanitization
- ❌ Logging de auditoria

### Checklist para Produção
```python
# Implementar:
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
import secrets

# 1. JWT Authentication
# 2. Password hashing (bcrypt)
# 3. Environment variables (.env)
# 4. Rate limiting (slowapi)
# 5. HTTPS enforcement
# 6. Secure headers (helmet)
# 7. Input sanitization
# 8. Audit logs
```

---

## Testes

### Manual Testing
1. Login com credenciais corretas/incorretas
2. CRUD completo de produtos
3. Busca de produtos
4. Criação de pedidos (compra/venda)
5. Mudança de status (pendente → pronto)
6. Verificação de estoque após pedido
7. Alertas de estoque baixo
8. Dashboard KPIs
9. Responsividade mobile

### Automated Testing (Sugerido)
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_login():
    response = client.post("/api/auth/login", json={
        "username": "Admin",
        "password": "1234"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_get_produtos():
    response = client.get("/api/produtos")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
```

---

## Deployment

### Desenvolvimento (Local)
```bash
cd backend
python app.py
```

### Produção (Linux Server)
```bash
# 1. Instalar dependências
pip install -r requirements.txt gunicorn

# 2. Usar Gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 3. Nginx reverse proxy (recomendado)
# /etc/nginx/sites-available/jmsound
server {
    listen 80;
    server_name jmsound.com.br;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker (Opcional)
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Logs & Monitoring

### Logs do Sistema
- **Terminal:** Todas requisições HTTP
- **Uvicorn:** Access logs automáticos
- **Python logging:** Configure conforme necessário

### Métricas Sugeridas
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active connections
- Database queries (se MySQL)
- Memory usage

### Tools Sugeridos
- **Prometheus** - métricas
- **Grafana** - dashboards
- **Sentry** - error tracking
- **ELK Stack** - logs centralizados

---

## Manutenção

### Backup (Mock Data)
```bash
# Backup automático diário
cp backend/mock_data/*.json backup/$(date +%Y%m%d)/
```

### Backup (MySQL)
```bash
mysqldump -u root -p jmsound_estoque > backup_$(date +%Y%m%d).sql
```

### Updates
```bash
# Atualizar dependências
pip install --upgrade -r requirements.txt

# Verificar breaking changes
pip list --outdated
```

---

## FAQ Técnico

**Q: Por que FastAPI e não Flask?**
A: FastAPI é mais moderno, assíncrono por padrão, tem validação automática (Pydantic) e documenta a API automaticamente (Swagger).

**Q: Por que não separar backend e frontend?**
A: Para simplificar o deployment e setup. Em produção, considere servir o frontend via CDN/Nginx.

**Q: Como escalar horizontalmente?**
A: Use load balancer (Nginx) + múltiplas instâncias Gunicorn + banco de dados centralizado (MySQL).

**Q: Mock data é thread-safe?**
A: Não. Use locks se múltiplos workers ou migre para database.

**Q: Como adicionar novos endpoints?**
A:
```python
@app.get("/api/nova-funcionalidade")
async def nova_funcionalidade():
    return {"data": "..."}
```

---

**Documentação mantida por:** Equipe de Desenvolvimento
**Última atualização:** 2024
**Versão do sistema:** 1.0.0
