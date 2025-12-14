import mysql.connector
from mysql.connector import Error
from datetime import date
from decimal import Decimal
# Carregar variáveis de ambiente de um arquivo .env, se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Se python-dotenv não estiver disponível, continuar (variáveis podem vir de ambiente)
    pass

class Database:
    def __init__(self):
        import os
        # Prefer environment variables for credentials (safer for commits/pushes)
        self.host = os.environ.get('DB_HOST')
        self.user = os.environ.get('DB_USER')
        self.password = os.environ.get('DB_PASSWORD')
        self.database = os.environ.get('DB_NAME')
        self.port = int(os.environ.get('DB_PORT'))
    
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
                    user_id INT NOT NULL,
                    ganho DECIMAL(10,2) NOT NULL,
                    kmrodado INT NOT NULL,
                    mediacar DECIMAL(5,2) NOT NULL,
                    data VARCHAR(10) NOT NULL,
                    lucro DECIMAL(10,2) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_ganhos_user (user_id)
                )
            """)
            
            # Criar tabela abastecimentos (se não existir)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS abastecimentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    custo DECIMAL(10,2) NOT NULL,
                    custolt DECIMAL(10,2) NOT NULL,
                    litrosa DECIMAL(8,3),
                    data VARCHAR(10) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_abast_user (user_id)
                )
            """)

            # Criar tabela usuarios (se não existir)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(100) NOT NULL,
                    telefone VARCHAR(30),
                    email VARCHAR(150) NOT NULL,
                    senha VARCHAR(255) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_email (email)
                )
            """)
            
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False

        finally:
            # Tenta adicionar chaves estrangeiras caso já existam tabelas sem a coluna user_id
            try:
                cursor = conn.cursor()
                # função helper para checar coluna
                cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s", (self.database, 'ganhos', 'user_id'))
                if cursor.fetchone()[0] == 0:
                    try:
                        cursor.execute("ALTER TABLE ganhos ADD COLUMN user_id INT NOT NULL")
                    except Exception:
                        pass

                # adicionar FK se não existir
                try:
                    cursor.execute("ALTER TABLE ganhos ADD CONSTRAINT fk_ganhos_user FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE")
                except Exception:
                    pass

                cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s", (self.database, 'abastecimentos', 'user_id'))
                if cursor.fetchone()[0] == 0:
                    try:
                        cursor.execute("ALTER TABLE abastecimentos ADD COLUMN user_id INT NOT NULL")
                    except Exception:
                        pass

                try:
                    cursor.execute("ALTER TABLE abastecimentos ADD CONSTRAINT fk_abast_user FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE")
                except Exception:
                    pass

                cursor.close()
            except Exception:
                pass

# Instância global do banco de dados
db = Database()
