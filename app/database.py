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
        # Required vars: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
        # Optional: DB_PORT (defaults to 3306)
        def _env(name, required=False, default=None):
            v = os.environ.get(name, default)
            if required and (v is None or v == ''):
                raise RuntimeError(f"Missing required environment variable: {name}.\n" \
                                   f"Set {name} in your environment (e.g., Render dashboard -> Environment -> Environment Variables) or provide a .env for local development.")
            return v

        self.host = _env('DB_HOST', required=True)
        self.user = _env('DB_USER', required=True)
        self.password = _env('DB_PASSWORD', required=True)
        self.database = _env('DB_NAME', required=True)
        port_val = _env('DB_PORT', required=False, default='3306')
        try:
            self.port = int(port_val)
        except Exception:
            raise RuntimeError(f"Invalid DB_PORT value: {port_val}. It must be a number (e.g. 3306).")
    
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
