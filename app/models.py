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
    return str(data_input).strip()

class Ganho:
    @staticmethod
    def criar(ganho, kmrodado, mediacar, data, lucro):
        conn = db.conectar()
        if conn is None:
            return False
        
        data = _get_data_automática(data)
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ganhos (ganho, kmrodado, mediacar, data, lucro) VALUES (%s, %s, %s, %s, %s)",
                (ganho, kmrodado, mediacar, data, lucro)
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
    def listar():
        conn = db.conectar()
        if conn is None:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ganho, kmrodado, mediacar, data, lucro FROM ganhos ORDER BY data DESC")
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
    def obter(id):
        conn = db.conectar()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ganho, kmrodado, mediacar, data, lucro FROM ganhos WHERE id = %s", (id,))
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
    def atualizar(id, ganho, kmrodado, mediacar, data, lucro):
        conn = db.conectar()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ganhos SET ganho = %s, kmrodado = %s, mediacar = %s, data = %s, lucro = %s WHERE id = %s",
                (ganho, kmrodado, mediacar, data, lucro, id)
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
    def deletar(id):
        conn = db.conectar()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ganhos WHERE id = %s", (id,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao deletar ganho: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def total_por_mes(mes):
        conn = db.conectar()
        if conn is None:
            return 0
        
        try:
            cursor = conn.cursor()
            search_pattern = f"%{mes}%"
            cursor.execute(
                "SELECT SUM(lucro) FROM ganhos WHERE data LIKE %s",
                (search_pattern,)
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
    def total_semana_atual():
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
                WHERE STR_TO_DATE(data, '%d-%m-%Y') BETWEEN %s AND %s
            """, (segunda, domingo))
            
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
    def criar(custo, custolt, data, litrosa):
        conn = db.conectar()
        if conn is None:
            return False
        
        data = _get_data_automática(data)
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO abastecimentos (custo, custolt, data, litrosa) VALUES (%s, %s, %s, %s)",
                (custo, custolt, data, litrosa)
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
    def listar():
        conn = db.conectar()
        if conn is None:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, custo, custolt, data, litrosa FROM abastecimentos ORDER BY data DESC")
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
    def obter(id):
        conn = db.conectar()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, custo, custolt, data, litrosa FROM abastecimentos WHERE id = %s", (id,))
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
    def atualizar(id, custo, custolt, data, litrosa):
        conn = db.conectar()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE abastecimentos SET custo = %s, custolt = %s, data = %s, litrosa = %s WHERE id = %s",
                (custo, custolt, data, litrosa, id)
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
    def deletar(id):
        conn = db.conectar()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM abastecimentos WHERE id = %s", (id,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao deletar abastecimento: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def obter_ultimo_custolt():
        conn = db.conectar()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT custolt FROM abastecimentos ORDER BY id DESC LIMIT 1")
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
