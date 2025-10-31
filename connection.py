"""
MySQL Database Connection
Arquivo opcional - usado apenas quando USE_DATABASE=true
"""
import os
from typing import Optional
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

class DatabaseConnection:
    """Gerenciador de conexão MySQL"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME', 'jmsound_estoque')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self._connection: Optional[mysql.connector.MySQLConnection] = None
    
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self._connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                autocommit=False
            )
            if self._connection.is_connected():
                print(f"✓ Conectado ao MySQL: {self.database}")
                return self._connection
        except Error as e:
            print(f"✗ Erro ao conectar ao MySQL: {e}")
            raise
    
    def disconnect(self):
        """Encerra conexão com o banco"""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            print("✓ Conexão MySQL encerrada")
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager para cursor"""
        cursor = None
        try:
            if not self._connection or not self._connection.is_connected():
                self.connect()
            cursor = self._connection.cursor(dictionary=dictionary)
            yield cursor
            self._connection.commit()
        except Error as e:
            if self._connection:
                self._connection.rollback()
            print(f"✗ Erro no banco de dados: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None):
        """Executa query SELECT e retorna resultados"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None):
        """Executa query INSERT/UPDATE/DELETE"""
        with self.get_cursor(dictionary=False) as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

# Instância global
db = DatabaseConnection()

# Exemplo de uso:
"""
from db.connection import db

# SELECT
produtos = db.execute_query("SELECT * FROM produtos WHERE quantidade_estoque <= minimo_alerta")

# INSERT
produto_id = db.execute_update(
    "INSERT INTO produtos (nome, codigo, valor_unitario, quantidade_estoque, minimo_alerta) VALUES (%s, %s, %s, %s, %s)",
    ("Produto Teste", "TEST001", 10.50, 100, 10)
)

# UPDATE
db.execute_update(
    "UPDATE produtos SET quantidade_estoque = %s WHERE id = %s",
    (150, produto_id)
)

# Context manager para transações complexas
with db.get_cursor() as cursor:
    cursor.execute("INSERT INTO pedidos (...) VALUES (...)")
    pedido_id = cursor.lastrowid
    cursor.execute("INSERT INTO pedido_itens (...) VALUES (...)", (pedido_id, ...))
"""
