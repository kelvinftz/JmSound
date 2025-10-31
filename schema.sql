-- ========================================
-- JmSound Estoque - Schema SQL
-- Sistema de Controle de Estoque
-- ========================================

-- Database
CREATE DATABASE IF NOT EXISTS jmsound_estoque
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE jmsound_estoque;

-- Tabela de Produtos
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    valor_unitario DECIMAL(10, 2) NOT NULL CHECK (valor_unitario > 0),
    quantidade_estoque INT NOT NULL DEFAULT 0 CHECK (quantidade_estoque >= 0),
    minimo_alerta INT NOT NULL DEFAULT 0 CHECK (minimo_alerta >= 0),
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_codigo (codigo),
    INDEX idx_nome (nome),
    INDEX idx_estoque_baixo (quantidade_estoque, minimo_alerta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('compra', 'venda') NOT NULL,
    data DATETIME NOT NULL,
    status ENUM('pendente', 'pronto', 'cancelado') NOT NULL DEFAULT 'pendente',
    observacoes TEXT,
    valor_total DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tipo (tipo),
    INDEX idx_status (status),
    INDEX idx_data (data)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Itens do Pedido
CREATE TABLE IF NOT EXISTS pedido_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    valor_unitario DECIMAL(10, 2) NOT NULL CHECK (valor_unitario > 0),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT,
    INDEX idx_pedido (pedido_id),
    INDEX idx_produto (produto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Movimentações
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    tipo ENUM('entrada', 'saida') NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    referencia_pedido INT,
    data DATETIME NOT NULL,
    usuario VARCHAR(100) NOT NULL DEFAULT 'admin',
    observacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT,
    FOREIGN KEY (referencia_pedido) REFERENCES pedidos(id) ON DELETE SET NULL,
    INDEX idx_produto (produto_id),
    INDEX idx_tipo (tipo),
    INDEX idx_data (data),
    INDEX idx_pedido (referencia_pedido)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Usuários (para futuro)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nome_completo VARCHAR(200),
    email VARCHAR(200) UNIQUE,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Views úteis

-- View: Produtos com estoque baixo
CREATE OR REPLACE VIEW v_produtos_estoque_baixo AS
SELECT 
    p.*,
    (p.minimo_alerta - p.quantidade_estoque) AS diferenca_minimo
FROM produtos p
WHERE p.quantidade_estoque <= p.minimo_alerta
ORDER BY p.quantidade_estoque ASC;

-- View: Resumo de movimentações por produto
CREATE OR REPLACE VIEW v_movimentacoes_resumo AS
SELECT 
    p.id AS produto_id,
    p.nome AS produto_nome,
    p.codigo AS produto_codigo,
    SUM(CASE WHEN m.tipo = 'entrada' THEN m.quantidade ELSE 0 END) AS total_entradas,
    SUM(CASE WHEN m.tipo = 'saida' THEN m.quantidade ELSE 0 END) AS total_saidas,
    COUNT(DISTINCT m.id) AS total_movimentacoes
FROM produtos p
LEFT JOIN movimentacoes m ON p.id = m.produto_id
GROUP BY p.id, p.nome, p.codigo;

-- View: Valor total do estoque
CREATE OR REPLACE VIEW v_valor_estoque AS
SELECT 
    SUM(quantidade_estoque * valor_unitario) AS valor_total_estoque,
    COUNT(*) AS total_produtos,
    SUM(quantidade_estoque) AS total_pecas
FROM produtos;

-- Triggers

DELIMITER //

-- Trigger: Atualizar valor total do pedido ao inserir item
CREATE TRIGGER trg_pedido_item_insert
AFTER INSERT ON pedido_itens
FOR EACH ROW
BEGIN
    UPDATE pedidos
    SET valor_total = (
        SELECT SUM(quantidade * valor_unitario)
        FROM pedido_itens
        WHERE pedido_id = NEW.pedido_id
    )
    WHERE id = NEW.pedido_id;
END//

-- Trigger: Atualizar valor total do pedido ao atualizar item
CREATE TRIGGER trg_pedido_item_update
AFTER UPDATE ON pedido_itens
FOR EACH ROW
BEGIN
    UPDATE pedidos
    SET valor_total = (
        SELECT SUM(quantidade * valor_unitario)
        FROM pedido_itens
        WHERE pedido_id = NEW.pedido_id
    )
    WHERE id = NEW.pedido_id;
END//

-- Trigger: Atualizar valor total do pedido ao deletar item
CREATE TRIGGER trg_pedido_item_delete
AFTER DELETE ON pedido_itens
FOR EACH ROW
BEGIN
    UPDATE pedidos
    SET valor_total = COALESCE((
        SELECT SUM(quantidade * valor_unitario)
        FROM pedido_itens
        WHERE pedido_id = OLD.pedido_id
    ), 0)
    WHERE id = OLD.pedido_id;
END//

DELIMITER ;

-- Stored Procedures

DELIMITER //

-- Procedure: Processar pedido (atualizar estoque e criar movimentações)
CREATE PROCEDURE sp_processar_pedido(IN p_pedido_id INT)
BEGIN
    DECLARE v_tipo VARCHAR(10);
    DECLARE v_status VARCHAR(20);
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_produto_id INT;
    DECLARE v_quantidade INT;
    
    DECLARE cur_itens CURSOR FOR 
        SELECT produto_id, quantidade 
        FROM pedido_itens 
        WHERE pedido_id = p_pedido_id;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Obter tipo e status do pedido
    SELECT tipo, status INTO v_tipo, v_status
    FROM pedidos
    WHERE id = p_pedido_id;
    
    -- Verificar se pedido está pronto
    IF v_status != 'pronto' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pedido deve estar com status pronto';
    END IF;
    
    OPEN cur_itens;
    
    read_loop: LOOP
        FETCH cur_itens INTO v_produto_id, v_quantidade;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Atualizar estoque
        IF v_tipo = 'compra' THEN
            UPDATE produtos 
            SET quantidade_estoque = quantidade_estoque + v_quantidade
            WHERE id = v_produto_id;
            
            -- Registrar movimentação
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, referencia_pedido, data, usuario)
            VALUES (v_produto_id, 'entrada', v_quantidade, p_pedido_id, NOW(), 'system');
        ELSE
            -- Venda: verificar estoque disponível
            IF (SELECT quantidade_estoque FROM produtos WHERE id = v_produto_id) < v_quantidade THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Estoque insuficiente para venda';
            END IF;
            
            UPDATE produtos 
            SET quantidade_estoque = quantidade_estoque - v_quantidade
            WHERE id = v_produto_id;
            
            -- Registrar movimentação
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, referencia_pedido, data, usuario)
            VALUES (v_produto_id, 'saida', v_quantidade, p_pedido_id, NOW(), 'system');
        END IF;
    END LOOP;
    
    CLOSE cur_itens;
END//

DELIMITER ;

-- Comentários nas tabelas
ALTER TABLE produtos COMMENT = 'Cadastro de produtos do estoque';
ALTER TABLE pedidos COMMENT = 'Pedidos de compra e venda';
ALTER TABLE pedido_itens COMMENT = 'Itens dos pedidos';
ALTER TABLE movimentacoes COMMENT = 'Histórico de movimentações de estoque';
ALTER TABLE usuarios COMMENT = 'Usuários do sistema';

-- Índices de performance adicionais
CREATE INDEX idx_produtos_search ON produtos(nome, codigo);
CREATE INDEX idx_movimentacoes_data_tipo ON movimentacoes(data DESC, tipo);
CREATE INDEX idx_pedidos_data_status ON pedidos(data DESC, status);
