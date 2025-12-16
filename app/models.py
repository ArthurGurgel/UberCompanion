from app.database import db
from datetime import date, timedelta
from decimal import Decimal

def _to_float(value):
    """Converter Decimal para float se necessário"""
    return float(value) if isinstance(value, Decimal) else value

def _get_data_automática(data_input):
    """Retorna data automática (hoje) se input vazio"""
    if not data_input or str(data_input).strip() == "":
        return date.today().strftime("%d-%m-%Y")
    return _normalize_date(str(data_input).strip())


def _normalize_date(s):
    """Normalize strings like 'dd/mm/YYYY' or 'dd-mm-YYYY' to 'dd-mm-YYYY' with zero padding.
    Returns the original string if it can't be interpreted."""
    if not s:
        return s
    s = s.replace('/', '-')
    parts = s.split('-')
    if len(parts) != 3:
        return s
    day, month, year = parts
    try:
        d = int(day)
        m = int(month)
        y = int(year)
        dd = str(d).zfill(2)
        mm = str(m).zfill(2)
        yyyy = str(y)
        return f"{dd}-{mm}-{yyyy}"
    except Exception:
        return s

class Ganho:
    @staticmethod
    def criar(user_id, ganho, kmrodado, mediacar, data, lucro):
        conn = db.conectar()
        if conn is None:
            return False
        
        data = _get_data_automática(data)
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ganhos (user_id, ganho, kmrodado, mediacar, data, lucro) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, ganho, kmrodado, mediacar, data, lucro)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao inserir ganho: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def listar(user_id):
        conn = db.conectar()
        if conn is None:
            return []
        
        try:
            cursor = conn.cursor()
            # Order by actual date (convert stored dd-mm-YYYY to DATE for correct ordering)
            cursor.execute("SELECT id, ganho, kmrodado, mediacar, data, lucro FROM ganhos WHERE user_id = %s ORDER BY STR_TO_DATE(data, '%d-%m-%Y') DESC", (user_id,))
            resultados = cursor.fetchall()
            resultados = [(r[0], _to_float(r[1]), r[2], _to_float(r[3]), r[4], _to_float(r[5])) for r in resultados]
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Erro ao listar ganhos: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def obter(id, user_id):
        conn = db.conectar()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ganho, kmrodado, mediacar, data, lucro FROM ganhos WHERE id = %s AND user_id = %s", (id, user_id))
            resultado = cursor.fetchone()
            cursor.close()
            if resultado:
                return (resultado[0], _to_float(resultado[1]), resultado[2], _to_float(resultado[3]), resultado[4], _to_float(resultado[5]))
            return None
        except Exception as e:
            print(f"Erro ao obter ganho: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def atualizar(id, user_id, ganho, kmrodado, mediacar, data, lucro):
        conn = db.conectar()
        if conn is None:
            return False
        # Normalize incoming date
        data = _normalize_date(data)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ganhos SET ganho = %s, kmrodado = %s, mediacar = %s, data = %s, lucro = %s WHERE id = %s AND user_id = %s",
                (ganho, kmrodado, mediacar, data, lucro, id, user_id)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar ganho: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def deletar(id, user_id):
        conn = db.conectar()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ganhos WHERE id = %s AND user_id = %s", (id, user_id))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao deletar ganho: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def total_por_mes(mes, user_id):
        conn = db.conectar()
        if conn is None:
            return 0
        
        try:
            cursor = conn.cursor()
            # mes expected as 'mm-YYYY'
            search_pattern = f"%{mes}%"
            cursor.execute(
                "SELECT SUM(lucro) FROM ganhos WHERE data LIKE %s AND user_id = %s",
                (search_pattern, user_id)
            )
            total = cursor.fetchone()[0]
            cursor.close()
            return _to_float(total) if total else 0
        except Exception as e:
            print(f"Erro ao calcular total: {e}")
            return 0
        finally:
            conn.close()
    
    @staticmethod
    def total_semana_atual(user_id):
        conn = db.conectar()
        if conn is None:
            return 0
        
        try:
            cursor = conn.cursor()
            
            hoje = date.today()
            dias_desde_segunda = hoje.weekday()
            segunda = hoje - timedelta(days=dias_desde_segunda)
            domingo = segunda + timedelta(days=6)
            
            cursor.execute("""
                SELECT SUM(lucro) FROM ganhos 
                WHERE STR_TO_DATE(data, '%d-%m-%Y') BETWEEN %s AND %s AND user_id = %s
            """, (segunda, domingo, user_id))
            
            resultado = cursor.fetchone()
            cursor.close()
            
            total = _to_float(resultado[0]) if resultado and resultado[0] else 0
            return total
        except Exception as e:
            print(f"Erro ao calcular total da semana: {e}")
            return 0
        finally:
            conn.close()

class Abastecimento:
    @staticmethod
    def criar(user_id, custo, custolt, data, litrosa):
        conn = db.conectar()
        if conn is None:
            return False
        
        data = _get_data_automática(data)
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO abastecimentos (user_id, custo, custolt, data, litrosa) VALUES (%s, %s, %s, %s, %s)",
                (user_id, custo, custolt, data, litrosa)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao inserir abastecimento: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def listar(user_id):
        conn = db.conectar()
        if conn is None:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, custo, custolt, data, litrosa FROM abastecimentos WHERE user_id = %s ORDER BY data DESC", (user_id,))
            resultados = cursor.fetchall()
            converted = []
            for r in resultados:
                converted.append((
                    r[0],
                    _to_float(r[1]) if r[1] is not None else None,
                    _to_float(r[2]) if r[2] is not None else None,
                    r[3],
                    _to_float(r[4]) if r[4] is not None else None
                ))
            cursor.close()
            return converted
        except Exception as e:
            print(f"Erro ao listar abastecimentos: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def obter(id, user_id):
        conn = db.conectar()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, custo, custolt, data, litrosa FROM abastecimentos WHERE id = %s AND user_id = %s", (id, user_id))
            resultado = cursor.fetchone()
            cursor.close()
            if resultado:
                return (resultado[0], _to_float(resultado[1]), _to_float(resultado[2]), resultado[3], _to_float(resultado[4]))
            return None
        except Exception as e:
            print(f"Erro ao obter abastecimento: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def atualizar(id, user_id, custo, custolt, data, litrosa):
        conn = db.conectar()
        if conn is None:
            return False
        data = _normalize_date(data)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE abastecimentos SET custo = %s, custolt = %s, data = %s, litrosa = %s WHERE id = %s AND user_id = %s",
                (custo, custolt, data, litrosa, id, user_id)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar abastecimento: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def deletar(id, user_id):
        conn = db.conectar()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM abastecimentos WHERE id = %s AND user_id = %s", (id, user_id))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao deletar abastecimento: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def obter_ultimo_custolt(user_id):
        conn = db.conectar()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT custolt FROM abastecimentos WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            if resultado and resultado[0] is not None:
                return _to_float(resultado[0])
            return None
        except Exception as e:
            print(f"Erro ao obter último custolt: {e}")
            return None
        finally:
            conn.close()
class User:
    @staticmethod
    def criar_usuario(usuario, email, telefone, senha):
        """Cria um novo usuário. Retorna (True, None) em sucesso ou (False, mensagem) em erro."""
        conn = db.conectar()
        if conn is None:
            return False, "Erro ao conectar ao banco de dados"

        try:
            cursor = conn.cursor()
            # Verificar se já existe pelo email ou usuário
            cursor.execute("SELECT id FROM usuarios WHERE email = %s OR usuario = %s OR telefone = %s", (email, usuario, telefone))
            existe = cursor.fetchone()
            if existe:
                cursor.close()
                return False, "Usuário, email ou telefone já cadastrado"

            # Hash da senha
            from werkzeug.security import generate_password_hash
            senha_hash = generate_password_hash(senha)

            cursor.execute("INSERT INTO usuarios (usuario, telefone, email, senha) VALUES (%s, %s, %s, %s)",
                           (usuario, telefone, email, senha_hash))
            conn.commit()
            cursor.close()
            return True, None
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False, "Erro ao criar usuário"
        finally:
            conn.close()

    @staticmethod
    def autenticar(login, senha):
        """Autentica um usuário por usuário/email/telefone. Retorna dicionário do usuário (sem senha) ou None."""
        conn = db.conectar()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, usuario, telefone, email, senha FROM usuarios WHERE usuario = %s OR email = %s OR telefone = %s LIMIT 1", (login, login, login))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None

            user_id, usuario, telefone, email, senha_hash = row
            from werkzeug.security import check_password_hash
            if check_password_hash(senha_hash, senha):
                return {
                    'id': user_id,
                    'usuario': usuario,
                    'telefone': telefone,
                    'email': email
                }
            return None
        except Exception as e:
            print(f"Erro ao autenticar usuário: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def atualizar_perfil(user_id, usuario, email, telefone):
        conn = db.conectar()
        if conn is None:
            return False, "Erro ao conectar ao banco"

        try:
            cursor = conn.cursor()
            # verificar se email/usuario em uso por outro id
            cursor.execute("SELECT id FROM usuarios WHERE (email = %s OR usuario = %s OR telefone = %s) AND id != %s LIMIT 1", (email, usuario, telefone, user_id))
            existe = cursor.fetchone()
            if existe:
                cursor.close()
                return False, "Email, usuário ou telefone já em uso"

            cursor.execute("UPDATE usuarios SET usuario = %s, email = %s, telefone = %s WHERE id = %s", (usuario, email, telefone, user_id))
            conn.commit()
            cursor.close()
            return True, None
        except Exception as e:
            print(f"Erro ao atualizar perfil: {e}")
            return False, "Erro ao atualizar perfil"
        finally:
            conn.close()

    @staticmethod
    def alterar_senha(user_id, senha_atual, senha_nova):
        conn = db.conectar()
        if conn is None:
            return False, "Erro ao conectar ao banco"

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT senha FROM usuarios WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close()
                return False, "Usuário não encontrado"

            from werkzeug.security import check_password_hash, generate_password_hash
            senha_hash = row[0]
            if not check_password_hash(senha_hash, senha_atual):
                cursor.close()
                return False, "Senha atual incorreta"

            nova_hash = generate_password_hash(senha_nova)
            cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (nova_hash, user_id))
            conn.commit()
            cursor.close()
            return True, None
        except Exception as e:
            print(f"Erro ao alterar senha: {e}")
            return False, "Erro ao alterar senha"
        finally:
            conn.close()
