#Ubercompanion

## Observações antes de publicar

- Este projeto utiliza credenciais de banco de dados em `app/database.py` por padrão. **Recomendo fortemente** colocar suas credenciais em variáveis de ambiente (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT) antes de publicar.
- Adicione um arquivo `.env` ao `.gitignore` e carregue variáveis com `python-dotenv` ou exporte no ambiente do servidor. Evite commitar segredos.

## Como publicar no GitHub

1. Crie um repositório no GitHub (via site ou `gh repo create`).
2. Adicione o remote e faça push:

```bash
git remote add origin git@github.com:SEU_USUARIO/NOME_REPO.git
git branch -M main
git push -u origin main
```

Se preferir, posso criar o repositório por você (preciso que você forneça um token do GitHub com permissões para criar repositórios, ou tenha o `gh` CLI autenticado). 

## Multi-tenant / dados por usuário

Implementei um modelo simples e seguro para que cada usuário tenha seus próprios registros (ganhos, abastecimentos, relatórios): agora as tabelas `ganhos` e `abastecimentos` possuem a coluna `user_id` e todas as operações (listar, criar, atualizar, deletar) são filtradas pelo usuário autenticado (session `user_id`).

Como funciona:
- Ao fazer login, o `user_id` é salvo na sessão (`session['user_id']`).
- Endpoints das APIs (`/api/ganhos`, `/api/abastecimentos`) só retornam ou permitem operações sobre os dados do usuário logado (retornam 401 se não autenticado).

Migração de dados existentes:
- Se você já tem dados nas tabelas, será necessário atribuir `user_id` às linhas existentes. Exemplo (substitua 1 pelo id do usuário que deve ficar como dono):

```sql
UPDATE ganhos SET user_id = 1 WHERE user_id IS NULL;
UPDATE abastecimentos SET user_id = 1 WHERE user_id IS NULL;
```

O método `db.criar_tabelas()` tenta adicionar as colunas `user_id` e as chaves estrangeiras automaticamente na inicialização (usa `information_schema` para detectar se a coluna já existe). Ainda assim, revise no banco e faça backup antes de executar em produção.

Rotas úteis:
- GET /profile — exibe formulário de edição de perfil
- POST /profile — atualiza `usuario`, `email`, `telefone`
- POST /profile/password — altera a senha (é necessário enviar senha atual)

