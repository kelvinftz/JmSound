# 🚀 Guia de Instalação - Windows

## Passo a Passo Completo

### 1️⃣ Pré-requisitos

Certifique-se de ter Python instalado no Windows:
- Baixe em: https://www.python.org/downloads/
- Durante a instalação, marque "Add Python to PATH"
- Versão recomendada: Python 3.8 ou superior

### 2️⃣ Extrair o Projeto

1. Extraia o arquivo `jmsound_estoque.zip` ou `jmsound_estoque.tar.gz`
2. Copie a pasta extraída para: `C:\Ia_Claude\novo_projeto`

### 3️⃣ Instalar Dependências

Abra o **Prompt de Comando** ou **PowerShell** e execute:

```cmd
cd C:\Ia_Claude\novo_projeto\backend
pip install -r requirements.txt
```

**Nota:** Se o comando `pip` não funcionar, tente `py -m pip install -r requirements.txt`

### 4️⃣ Executar o Sistema

#### Opção A: Usando o script .bat (Mais fácil)
1. Navegue até `C:\Ia_Claude\novo_projeto`
2. Dê duplo clique em `iniciar.bat`

#### Opção B: Pelo terminal
```cmd
cd C:\Ia_Claude\novo_projeto\backend
python app.py
```

### 5️⃣ Acessar o Sistema

1. Abra seu navegador (Chrome, Firefox, Edge)
2. Acesse: `http://localhost:8000`
3. Faça login com:
   - **Usuário:** Admin
   - **Senha:** 1234

---

## 🔧 Resolução de Problemas

### Erro: "Python não é reconhecido como comando"
**Solução:** Python não está no PATH. Reinstale o Python marcando "Add Python to PATH"

### Erro: "pip não é reconhecido"
**Solução:** Use `py -m pip install -r requirements.txt` ao invés de `pip install`

### Erro: "Address already in use" ou porta 8000 ocupada
**Solução:** 
1. Feche outros programas que possam estar usando a porta 8000
2. Ou edite `backend/app.py` e mude a porta 8000 para 8080

### Erro ao instalar dependências
**Solução:**
```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Sistema não abre no navegador
**Solução:**
1. Verifique se o servidor está rodando (deve mostrar mensagens no terminal)
2. Tente acessar `http://127.0.0.1:8000` ao invés de localhost
3. Desative temporariamente antivírus/firewall

---

## 📁 Estrutura de Pastas Esperada

```
C:\Ia_Claude\novo_projeto\
│
├── backend\
│   ├── app.py                      ← Arquivo principal
│   ├── requirements.txt            ← Dependências
│   ├── .env.example                ← Configurações
│   ├── mock_data\                  ← Dados de teste
│   │   ├── produtos.json
│   │   ├── pedidos.json
│   │   └── movimentacoes.json
│   └── db\                         ← Scripts MySQL (opcional)
│
├── frontend\
│   ├── index.html                  ← Tela de login
│   ├── dashboard.html              ← Dashboard
│   ├── produtos.html               ← Produtos
│   ├── pedidos.html                ← Pedidos
│   ├── movimentacoes.html          ← Histórico
│   ├── notificacoes.html           ← Alertas
│   ├── assets\css\style.css        ← Estilos
│   └── src\                        ← JavaScript
│       ├── auth.js
│       ├── dashboard.js
│       └── produtos.js
│
├── iniciar.bat                     ← Script de inicialização
└── README.md                       ← Documentação
```

---

## 🎯 Funcionalidades Disponíveis

✅ **Login** - Admin/1234
✅ **Dashboard** - KPIs, gráficos e alertas
✅ **Produtos** - CRUD completo
✅ **Pedidos** - Compra e venda com controle de estoque
✅ **Movimentações** - Histórico completo
✅ **Notificações** - Alertas de estoque baixo

---

## 💾 Modo Database (Opcional)

Por padrão, o sistema usa **mock data** (dados em memória). Para usar MySQL:

1. Instale MySQL: https://dev.mysql.com/downloads/installer/
2. Execute o script: `backend\db\schema.sql`
3. Configure o arquivo `.env`:
```env
USE_DATABASE=true
DB_HOST=localhost
DB_PORT=3306
DB_NAME=jmsound_estoque
DB_USER=root
DB_PASSWORD=sua_senha
```
4. Instale o driver MySQL:
```cmd
pip install mysql-connector-python
```

---

## 📞 Suporte

### Logs do Sistema
- Verifique o terminal onde executou `python app.py`
- Erros aparecerão em vermelho

### Documentação da API
- Acesse: `http://localhost:8000/docs`
- Interface interativa Swagger

### Verificar Instalação
Execute estes comandos para diagnóstico:
```cmd
python --version
pip --version
cd C:\Ia_Claude\novo_projeto\backend
dir
type requirements.txt
```

---

## 🎓 Comandos Úteis

### Parar o servidor
Pressione `CTRL + C` no terminal

### Recarregar após mudanças
O servidor recarrega automaticamente ao salvar arquivos Python

### Limpar cache
```cmd
cd C:\Ia_Claude\novo_projeto\backend
del /s /q __pycache__
```

### Verificar processos na porta 8000
```cmd
netstat -ano | findstr :8000
```

---

## ✨ Próximos Passos

1. ✅ Faça login e explore o sistema
2. 📦 Cadastre seus produtos
3. 🛒 Crie pedidos de compra/venda
4. 📊 Monitore KPIs no dashboard
5. 🔔 Configure alertas de estoque

**Desenvolvido para JmSound Auto Elétrica**
