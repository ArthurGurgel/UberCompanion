#!/usr/bin/env python3
"""Migração: adiciona coluna user_id em ganhos e abastecimentos se faltar.
Uso:
  python scripts/migrate_add_userid.py [--assign-user USER_ID]

Se --assign-user não informado, o script só adiciona a coluna (como NULLABLE) e imprime quantas linhas ficaram sem user_id.
"""
import argparse
from app.database import db

parser = argparse.ArgumentParser()
parser.add_argument('--assign-user', type=int, help='ID do usuário para atribuir às linhas existentes sem user_id')
args = parser.parse_args()

conn = db.conectar()
if not conn:
    print('Erro: não foi possível conectar ao banco')
    raise SystemExit(1)

cursor = conn.cursor()

for table in ('ganhos', 'abastecimentos'):
    cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s", (db.database, table, 'user_id'))
    exists = cursor.fetchone()[0]
    if exists:
        print(f"Tabela {table}: coluna user_id já existe")
    else:
        print(f"Tabela {table}: adicionando coluna user_id (NULLABLE)")
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INT DEFAULT NULL")
            cursor.execute(f"CREATE INDEX idx_{table}_user ON {table} (user_id)")
            conn.commit()
            print(f"  coluna user_id adicionada com sucesso em {table}")
        except Exception as e:
            print(f"  ERRO ao adicionar coluna em {table}: {e}")

    # contar linhas sem user_id
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id IS NULL")
        nulls = cursor.fetchone()[0]
        print(f"  Linhas com user_id NULL em {table}: {nulls}")
        if args.assign_user and nulls > 0:
            cursor.execute(f"UPDATE {table} SET user_id = %s WHERE user_id IS NULL", (args.assign_user,))
            conn.commit()
            print(f"  Atribuído user_id={args.assign_user} em {nulls} linhas de {table}")
    except Exception as e:
        print(f"  Não foi possível contar/atualizar linhas em {table}: {e}")

# tentar adicionar FK (não obrigatório)
try:
    cursor.execute("ALTER TABLE ganhos ADD CONSTRAINT fk_ganhos_user FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE")
except Exception:
    pass
try:
    cursor.execute("ALTER TABLE abastecimentos ADD CONSTRAINT fk_abast_user FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE")
except Exception:
    pass

cursor.close()
conn.close()
print('Migração finalizada')
