"""
Sistema de Controle de Estoque - JmSound Auto Elétrica
Ponto de entrada único: python app.py
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configuração
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
MOCK_DATA_DIR = BASE_DIR / "mock_data"

# Variável para controlar uso de banco de dados
USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"

# FastAPI App
app = FastAPI(
    title="JmSound Estoque API",
    description="Sistema de Controle de Estoque para Auto Elétrica",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# MODELS (Pydantic)
# =============================================================================

class Produto(BaseModel):
    id: Optional[int] = None
    nome: str
    codigo: str
    valor_unitario: float = Field(gt=0)
    quantidade_estoque: int = Field(ge=0)
    minimo_alerta: int = Field(ge=0)
    descricao: Optional[str] = ""

class ItemPedido(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)
    valor_unitario: float = Field(gt=0)

class Pedido(BaseModel):
    id: Optional[int] = None
    tipo: str  # "compra" ou "venda"
    data: str
    status: str = "pendente"  # pendente, pronto, cancelado
    itens: List[ItemPedido]
    observacoes: Optional[str] = ""

class Movimentacao(BaseModel):
    id: Optional[int] = None
    produto_id: int
    tipo: str  # "entrada" ou "saida"
    quantidade: int
    referencia_pedido: Optional[int] = None
    data: str
    usuario: str = "admin"

class LoginRequest(BaseModel):
    username: str
    password: str

# =============================================================================
# MOCK DATA MANAGER
# =============================================================================

class MockDataManager:
    """Gerencia dados mock em memória e arquivos JSON"""
    
    def __init__(self):
        self.produtos: List[Dict] = []
        self.pedidos: List[Dict] = []
        self.movimentacoes: List[Dict] = []
        self.load_mock_data()
    
    def load_mock_data(self):
        """Carrega dados dos arquivos JSON"""
        try:
            with open(MOCK_DATA_DIR / "produtos.json", "r", encoding="utf-8") as f:
                self.produtos = json.load(f)
            with open(MOCK_DATA_DIR / "pedidos.json", "r", encoding="utf-8") as f:
                self.pedidos = json.load(f)
            with open(MOCK_DATA_DIR / "movimentacoes.json", "r", encoding="utf-8") as f:
                self.movimentacoes = json.load(f)
            print("✓ Mock data carregado com sucesso")
        except FileNotFoundError:
            print("⚠ Arquivos mock não encontrados, iniciando com dados vazios")
            self.initialize_default_data()
    
    def initialize_default_data(self):
        """Inicializa dados padrão se arquivos não existirem"""
        self.produtos = [
            {"id": 1, "nome": "Alternador 12V 90A", "codigo": "ALT001", "valor_unitario": 450.00, "quantidade_estoque": 5, "minimo_alerta": 2, "descricao": "Alternador 12V 90A universal"},
            {"id": 2, "nome": "Bateria Moura 60Ah", "codigo": "BAT060", "valor_unitario": 380.00, "quantidade_estoque": 12, "minimo_alerta": 5, "descricao": "Bateria automotiva 60Ah"},
            {"id": 3, "nome": "Farol H7", "codigo": "FAR007", "valor_unitario": 55.00, "quantidade_estoque": 1, "minimo_alerta": 3, "descricao": "Lâmpada farol H7 55W"},
            {"id": 4, "nome": "Motor de Arranque", "codigo": "MOT001", "valor_unitario": 620.00, "quantidade_estoque": 3, "minimo_alerta": 2, "descricao": "Motor de partida 12V"},
            {"id": 5, "nome": "Bobina de Ignição", "codigo": "BOB001", "valor_unitario": 185.00, "quantidade_estoque": 8, "minimo_alerta": 4, "descricao": "Bobina de ignição universal"},
        ]
        
        self.pedidos = [
            {
                "id": 1,
                "tipo": "compra",
                "data": "2024-10-25T10:30:00",
                "status": "pronto",
                "itens": [{"produto_id": 1, "quantidade": 5, "valor_unitario": 450.00}],
                "observacoes": "Fornecedor ABC"
            },
            {
                "id": 2,
                "tipo": "venda",
                "data": "2024-10-28T14:20:00",
                "status": "pendente",
                "itens": [{"produto_id": 3, "quantidade": 2, "valor_unitario": 55.00}],
                "observacoes": "Cliente XYZ"
            }
        ]
        
        self.movimentacoes = [
            {
                "id": 1,
                "produto_id": 1,
                "tipo": "entrada",
                "quantidade": 5,
                "referencia_pedido": 1,
                "data": "2024-10-25T10:30:00",
                "usuario": "admin"
            }
        ]
    
    def get_next_id(self, collection: List[Dict]) -> int:
        """Retorna próximo ID disponível"""
        if not collection:
            return 1
        return max(item["id"] for item in collection) + 1

# Instância global do gerenciador de dados
mock_db = MockDataManager()

# =============================================================================
# AUTH
# =============================================================================

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    """Login simples (Admin/1234)"""
    if credentials.username == "Admin" and credentials.password == "1234":
        return {"success": True, "user": "Admin", "token": "mock-token-12345"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

# =============================================================================
# PRODUTOS CRUD
# =============================================================================

@app.get("/api/produtos")
async def get_produtos(busca: Optional[str] = None):
    """Lista todos os produtos com busca opcional"""
    produtos = mock_db.produtos
    
    if busca:
        busca = busca.lower()
        produtos = [
            p for p in produtos 
            if busca in p["nome"].lower() or busca in p["codigo"].lower()
        ]
    
    return {"success": True, "data": produtos}

@app.get("/api/produtos/{produto_id}")
async def get_produto(produto_id: int):
    """Busca produto por ID"""
    produto = next((p for p in mock_db.produtos if p["id"] == produto_id), None)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"success": True, "data": produto}

@app.post("/api/produtos")
async def create_produto(produto: Produto):
    """Cria novo produto"""
    novo_produto = produto.dict()
    novo_produto["id"] = mock_db.get_next_id(mock_db.produtos)
    mock_db.produtos.append(novo_produto)
    return {"success": True, "data": novo_produto, "message": "Produto criado com sucesso"}

@app.put("/api/produtos/{produto_id}")
async def update_produto(produto_id: int, produto: Produto):
    """Atualiza produto existente"""
    idx = next((i for i, p in enumerate(mock_db.produtos) if p["id"] == produto_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    produto_data = produto.dict()
    produto_data["id"] = produto_id
    mock_db.produtos[idx] = produto_data
    return {"success": True, "data": produto_data, "message": "Produto atualizado com sucesso"}

@app.delete("/api/produtos/{produto_id}")
async def delete_produto(produto_id: int):
    """Remove produto"""
    idx = next((i for i, p in enumerate(mock_db.produtos) if p["id"] == produto_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    mock_db.produtos.pop(idx)
    return {"success": True, "message": "Produto removido com sucesso"}

# =============================================================================
# PEDIDOS CRUD
# =============================================================================

@app.get("/api/pedidos")
async def get_pedidos(tipo: Optional[str] = None, status: Optional[str] = None):
    """Lista pedidos com filtros opcionais"""
    pedidos = mock_db.pedidos
    
    if tipo:
        pedidos = [p for p in pedidos if p["tipo"] == tipo]
    if status:
        pedidos = [p for p in pedidos if p["status"] == status]
    
    return {"success": True, "data": pedidos}

@app.get("/api/pedidos/{pedido_id}")
async def get_pedido(pedido_id: int):
    """Busca pedido por ID"""
    pedido = next((p for p in mock_db.pedidos if p["id"] == pedido_id), None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {"success": True, "data": pedido}

@app.post("/api/pedidos")
async def create_pedido(pedido: Pedido):
    """Cria novo pedido"""
    novo_pedido = pedido.dict()
    novo_pedido["id"] = mock_db.get_next_id(mock_db.pedidos)
    novo_pedido["data"] = datetime.now().isoformat()
    mock_db.pedidos.append(novo_pedido)
    return {"success": True, "data": novo_pedido, "message": "Pedido criado com sucesso"}

@app.put("/api/pedidos/{pedido_id}")
async def update_pedido(pedido_id: int, pedido: Pedido):
    """Atualiza pedido e processa estoque se status = pronto"""
    idx = next((i for i, p in enumerate(mock_db.pedidos) if p["id"] == pedido_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    pedido_data = pedido.dict()
    pedido_data["id"] = pedido_id
    pedido_anterior = mock_db.pedidos[idx]
    
    # Processar estoque se mudou para "pronto"
    if pedido_data["status"] == "pronto" and pedido_anterior["status"] != "pronto":
        processar_estoque(pedido_data)
    
    mock_db.pedidos[idx] = pedido_data
    return {"success": True, "data": pedido_data, "message": "Pedido atualizado com sucesso"}

@app.delete("/api/pedidos/{pedido_id}")
async def delete_pedido(pedido_id: int):
    """Remove pedido"""
    idx = next((i for i, p in enumerate(mock_db.pedidos) if p["id"] == pedido_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    mock_db.pedidos.pop(idx)
    return {"success": True, "message": "Pedido removido com sucesso"}

def processar_estoque(pedido: Dict):
    """Processa alterações no estoque baseado no pedido"""
    for item in pedido["itens"]:
        produto_id = item["produto_id"]
        quantidade = item["quantidade"]
        
        # Encontrar produto
        produto = next((p for p in mock_db.produtos if p["id"] == produto_id), None)
        if not produto:
            continue
        
        # Atualizar estoque
        if pedido["tipo"] == "compra":
            produto["quantidade_estoque"] += quantidade
            tipo_mov = "entrada"
        else:  # venda
            if produto["quantidade_estoque"] < quantidade:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Estoque insuficiente para {produto['nome']}. Disponível: {produto['quantidade_estoque']}"
                )
            produto["quantidade_estoque"] -= quantidade
            tipo_mov = "saida"
        
        # Registrar movimentação
        movimentacao = {
            "id": mock_db.get_next_id(mock_db.movimentacoes),
            "produto_id": produto_id,
            "tipo": tipo_mov,
            "quantidade": quantidade,
            "referencia_pedido": pedido["id"],
            "data": datetime.now().isoformat(),
            "usuario": "admin"
        }
        mock_db.movimentacoes.append(movimentacao)

# =============================================================================
# MOVIMENTAÇÕES
# =============================================================================

@app.get("/api/movimentacoes")
async def get_movimentacoes(produto_id: Optional[int] = None):
    """Lista movimentações com filtro opcional por produto"""
    movimentacoes = mock_db.movimentacoes
    
    if produto_id:
        movimentacoes = [m for m in movimentacoes if m["produto_id"] == produto_id]
    
    return {"success": True, "data": movimentacoes}

# =============================================================================
# DASHBOARD / NOTIFICAÇÕES
# =============================================================================

@app.get("/api/dashboard/kpis")
async def get_dashboard_kpis():
    """Retorna KPIs para o dashboard"""
    total_produtos = len(mock_db.produtos)
    produtos_abaixo_minimo = [
        p for p in mock_db.produtos 
        if p["quantidade_estoque"] <= p["minimo_alerta"]
    ]
    
    perc_abaixo_minimo = (len(produtos_abaixo_minimo) / total_produtos * 100) if total_produtos > 0 else 0
    pecas_em_falta = sum(
        max(0, p["minimo_alerta"] - p["quantidade_estoque"]) 
        for p in produtos_abaixo_minimo
    )
    
    # Top 10 menor estoque
    top_10_menor = sorted(
        mock_db.produtos, 
        key=lambda x: x["quantidade_estoque"]
    )[:10]
    
    # Pedidos recentes
    pedidos_recentes = sorted(
        mock_db.pedidos,
        key=lambda x: x["data"],
        reverse=True
    )[:5]
    
    # Movimentações últimos 7 dias (mock)
    entradas_saidas = {
        "labels": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"],
        "entradas": [5, 3, 8, 2, 6, 1, 4],
        "saidas": [3, 5, 2, 7, 4, 6, 3]
    }
    
    return {
        "success": True,
        "data": {
            "perc_abaixo_minimo": round(perc_abaixo_minimo, 1),
            "pecas_em_falta": pecas_em_falta,
            "total_produtos": total_produtos,
            "produtos_abaixo_minimo": len(produtos_abaixo_minimo),
            "top_10_menor_estoque": top_10_menor,
            "pedidos_recentes": pedidos_recentes,
            "entradas_saidas": entradas_saidas,
            "alertas": produtos_abaixo_minimo
        }
    }

@app.get("/api/notificacoes")
async def get_notificacoes():
    """Retorna alertas de estoque baixo"""
    alertas = [
        p for p in mock_db.produtos 
        if p["quantidade_estoque"] <= p["minimo_alerta"]
    ]
    
    return {
        "success": True,
        "data": alertas,
        "count": len(alertas)
    }

# =============================================================================
# FRONTEND ROUTES
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve login page"""
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/{page}.html", response_class=HTMLResponse)
async def serve_page(page: str):
    """Serve outras páginas HTML"""
    file_path = FRONTEND_DIR / f"{page}.html"
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Página não encontrada")

# Mount static files
app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
app.mount("/src", StaticFiles(directory=str(FRONTEND_DIR / "src")), name="src")

# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 JmSound - Sistema de Controle de Estoque")
    print("="*60)
    print(f"📁 Diretório: {BASE_DIR.parent}")
    print(f"🗄️  Modo: {'DATABASE' if USE_DATABASE else 'DEMO (Mock Data)'}")
    print(f"🌐 URL: http://localhost:8000")
    print(f"📊 API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
