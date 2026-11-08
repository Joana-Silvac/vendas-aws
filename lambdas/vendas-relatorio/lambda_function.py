import os, json, csv, io
from collections import defaultdict
import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]

def resp(status, body):
    return {"statusCode": status,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body, ensure_ascii=False)}

def lambda_handler(event, context):
    chave = (event.get("queryStringParameters") or {}).get("arquivo", "")
    if not chave.startswith("vendas-csv/") or ".." in chave:
        return resp(400, {"erro": "Parâmetro 'arquivo' inválido"})
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=chave)
    except s3.exceptions.NoSuchKey:
        return resp(404, {"erro": "Arquivo não encontrado"})

    texto = obj["Body"].read().decode("utf-8")
    total = 0.0
    por_produto = defaultdict(lambda: {"quantidade": 0.0, "receita": 0.0})
    try:
        for l in csv.DictReader(io.StringIO(texto)):
            q, p = float(l["quantidade"]), float(l["preco_unitario"])
            total += q * p
            por_produto[l["produto"]]["quantidade"] += q
            por_produto[l["produto"]]["receita"] += q * p
    except (ValueError, TypeError, KeyError):
        return resp(422, {"erro": "Arquivo com dados inválidos"})

    ranking = sorted(({"produto": k, "quantidade": v["quantidade"], "receita": round(v["receita"], 2)}
                      for k, v in por_produto.items()),
                     key=lambda x: x["quantidade"], reverse=True)
    relatorio = {"arquivo": chave, "total_vendas": round(total, 2),
                 "produtos_mais_vendidos": ranking[:5]}

    saida = chave.replace("vendas-csv/", "relatorios/").replace(".csv", ".json")
    s3.put_object(Bucket=BUCKET, Key=saida,
                  Body=json.dumps(relatorio, ensure_ascii=False).encode("utf-8"),
                  ContentType="application/json")
    return resp(200, relatorio)
