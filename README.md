# Análise de vendas na nuvem (AWS)

Projeto Final de Cloud Computing (UNIMA). O usuário envia um CSV de vendas, o S3 guarda o arquivo e a Lambda calcula o total e os produtos mais vendidos.

## Arquitetura
Navegador → site estático (S3) → Lambda `vendas-upload` / `vendas-relatorio` (Function URL) → S3 (`vendas-csv/` e `relatorios/`)

## Estrutura
- `docs/index.html`: interface web (edite as duas URLs no topo do script)
- `lambdas/vendas-upload/lambda_function.py`: valida e grava o CSV no S3
- `lambdas/vendas-relatorio/lambda_function.py`: lê o CSV, calcula e grava o relatório
- `exemplos/`: CSV válido e dois inválidos para testes

## Como executar
1. Criar dois buckets S3: um privado (dados) e um com hospedagem de site estático.
2. Criar a IAM Role `role-lambda-vendas` com acesso só ao bucket de dados.
3. Criar as duas Lambdas (Python 3.12), colar o código e definir a variável de ambiente `BUCKET_NAME`.
4. Criar a Function URL de cada Lambda (auth NONE, CORS com a URL do site).
5. Colar as URLs em `docs/index.html` e enviar o arquivo para o bucket do site.

Nenhuma credencial fica no código: as Lambdas usam a IAM Role.

## Resultado esperado com `exemplos/vendas_exemplo.csv`
- Total de vendas: R$ 1236.70
- Ranking por quantidade: Garrafa (10), Camiseta (9), Caneca (8), Boné (5), Mochila (1)
