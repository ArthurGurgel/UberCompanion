import mysql.connector
from mysql.connector import Error
from datetime import date
from decimal import Decimal

class Database:
    def __init__(self, host='joao.palmas.br', user='joaopa29_arthur', password='arthur2025', database='joaopa29_arthur', port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
    
    def conectar(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True,
                connection_timeout=10
            )
            return conn
        except Error as e:
            print(f"Erro ao conectar: {e}")
            return None
    
    def criar_tabelas(self):
        conn = self.conectar()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Criar tabela ganhos (se não existir)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ganhos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ganho DECIMAL(10,2) NOT NULL,
                    kmrodado INT NOT NULL,
                    mediacar DECIMAL(5,2) NOT NULL,
                    data VARCHAR(10) NOT NULL,
                    lucro DECIMAL(10,2) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Criar tabela abastecimentos (se não existir)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS abastecimentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    custo DECIMAL(10,2) NOT NULL,
                    custolt DECIMAL(10,2) NOT NULL,
                    litrosa DECIMAL(8,3),
                    data VARCHAR(10) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False

# Instância global do banco de dados
db = Database()
