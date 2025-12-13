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
