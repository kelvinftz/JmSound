# 🚗 JmSound - Sistema de Controle de Estoque para Auto Elétrica

Sistema web completo para gestão de estoque de auto elétrica, desenvolvido com FastAPI (Backend) e Bootstrap 5 (Frontend).

## 🎯 Características Principais

- ✅ **Modo DEMO** - Funciona sem banco de dados (mock data)
- ✅ **Execução Single-Command** - Um único comando para rodar tudo
- ✅ **CRUD Completo** - Produtos, Pedidos, Movimentações
- ✅ **Dashboard com KPIs** - Métricas em tempo real
- ✅ **Alertas de Estoque** - Notificações automáticas de estoque baixo
- ✅ **Controle de Pedidos** - Compra e venda com atualização automática de estoque
- ✅ **Tema Moderno** - Interface Sneat Bootstrap 5
- ✅ **Responsivo** - Funciona em desktop, tablet e mobile

## 📋 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação e Execução

### 1. Instalar Dependências

```bash
cd C:\Ia_Claude\novo_projeto\backend
pip install -r requirements.txt
```

### 2. Executar o Sistema

```bash
python app.py
```

O sistema estará disponível em: **http://localhost:8000**

### 3. Fazer Login

```
Usuário: Admin
Senha: 1234
```

## 📁 Estrutura do Projeto

```
C:\Ia_Claude\novo_projeto
│
├─ backend/
│  ├─ app.py                    # Aplicação principal (Backend + Frontend)
│  ├─ requirements.txt          # Dependências Python
│  ├─ mock_data/                # Dados de demonstração
│  │   ├─ produtos.json
│  │   ├─ pedidos.json
│  │   └─ movimentacoes.json
│  └─ db/                       # (Opcional) Scripts MySQL
│
├─ frontend/
│  ├─ index.html                # Tela de login
│  ├─ dashboard.html            # Dashboard principal
│  ├─ produtos.html             # Gestão de produtos
│  ├─ pedidos.html              # Gestão de pedidos
│  ├─ movimentacoes.html        # Histórico de movimentações
│  ├─ notificacoes.html         # Alertas de estoque
│  ├─ assets/                   # CSS customizado
│  │   └─ css/
│  │       └─ style.css
│  └─ src/                      # JavaScript
│      ├─ auth.js               # Autenticação
│      ├─ dashboard.js          # Lógica do dashboard
│      └─ produtos.js           # CRUD de produtos
│
├─ docs/
│  └─ especificacao.md
│
└─ README.md
```

## 🎨 Funcionalidades por Módulo

### 📊 Dashboard
- KPIs principais (Total de produtos, % abaixo do mínimo, peças em falta)
- Gráfico de movimentações (últimos 7 dias)
- Top 10 produtos com menor estoque
- Pedidos recentes
- Alertas em tempo real

### 📦 Produtos
- **Cadastro** completo de produtos
- **Busca** por nome ou código
- **Edição** de informações
- **Exclusão** de produtos
- **Alertas visuais** para estoque baixo
- Campos: código, nome, valor unitário, quantidade, estoque mínimo, descrição

### 🛒 Pedidos
- **Pedidos de compra** - aumentam estoque ao serem marcados como "pronto"
- **Pedidos de venda** - diminuem estoque (com validação de quantidade disponível)
- Status: pendente, pronto, cancelado
- Filtros por tipo (compra/venda)
- Histórico completo

### 📈 Movimentações
- **Registro automático** de todas entradas e saídas
- Vinculação com pedidos (referência)
- Histórico completo com data e usuário
- Rastreabilidade total do estoque

### 🔔 Alertas/Notificações
- Lista de produtos com estoque ≤ mínimo
- Destaque para produtos sem estoque (quantidade = 0)
- Contador de alertas no menu e navbar
- Sugestão de ações (comprar)

## 🔧 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login do usuário

### Produtos
- `GET /api/produtos` - Listar produtos (com busca opcional)
- `GET /api/produtos/{id}` - Buscar produto específico
- `POST /api/produtos` - Criar produto
- `PUT /api/produtos/{id}` - Atualizar produto
- `DELETE /api/produtos/{id}` - Excluir produto

### Pedidos
- `GET /api/pedidos` - Listar pedidos (filtros: tipo, status)
- `GET /api/pedidos/{id}` - Buscar pedido específico
- `POST /api/pedidos` - Criar pedido
- `PUT /api/pedidos/{id}` - Atualizar pedido (processa estoque se status = pronto)
- `DELETE /api/pedidos/{id}` - Excluir pedido

### Movimentações
- `GET /api/movimentacoes` - Listar movimentações (filtro: produto_id)

### Dashboard
- `GET /api/dashboard/kpis` - Obter KPIs e dados do dashboard
- `GET /api/notificacoes` - Obter alertas de estoque baixo

## 🗄️ Modo Database (Opcional)

O sistema está preparado para funcionar com MySQL. Para ativar:

1. Configure a variável de ambiente:
```bash
export USE_DATABASE=true  # Linux/Mac
set USE_DATABASE=true     # Windows
```

2. Crie o arquivo `backend/db/connection.py` com sua conexão MySQL

3. Execute os scripts SQL em `backend/db/schema.sql` e `backend/db/seed.sql`

## 🎓 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

### Frontend
- **HTML5/CSS3/JavaScript** - Base do frontend
- **Bootstrap 5** - Framework CSS responsivo
- **Font Awesome** - Ícones
- **Chart.js** - Gráficos interativos

## 📝 Regras de Negócio

### Produtos
- Código único por produto
- Valor unitário deve ser maior que zero
- Quantidade e estoque mínimo não podem ser negativos
- Alerta visual quando `quantidade_estoque <= minimo_alerta`

### Pedidos
- **Compra**: Ao marcar como "pronto", incrementa o estoque
- **Venda**: Ao marcar como "pronto", decrementa o estoque
  - ⚠️ Validação: bloqueia venda se estoque insuficiente
- Cada alteração de status gera registro em movimentações

### Movimentações
- Registro automático e imutável
- Tipos: "entrada" ou "saida"
- Sempre vinculado a um pedido (referência)
- Inclui: produto, quantidade, data, usuário

## 🧪 Dados de Teste

O sistema vem com 10 produtos pré-cadastrados:
- Alternador 12V 90A
- Bateria Moura 60Ah
- Farol H7 Osram
- Motor de Arranque Bosch
- Bobina de Ignição NGK
- Regulador de Voltagem
- Chicote Elétrico Universal
- Sensor MAP
- Central de Injeção Magneti
- Relé 5 Pinos Universal

Alguns produtos já possuem **estoque abaixo do mínimo** para demonstrar os alertas.

## 🔐 Segurança

⚠️ **ATENÇÃO**: Este é um sistema de demonstração. Para uso em produção:

1. Implemente autenticação real (JWT, OAuth2)
2. Use variáveis de ambiente para credenciais
3. Configure CORS adequadamente
4. Implemente rate limiting
5. Adicione validações de negócio mais rigorosas
6. Use HTTPS em produção

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique os logs do console
- Acesse a documentação automática em: http://localhost:8000/docs
- Revise o arquivo `docs/especificacao.md`

## 📄 Licença

Sistema desenvolvido para uso interno da JmSound Auto Elétrica.

---

**Desenvolvido com ❤️ para gestão eficiente de estoque automotivo**
