import os, json, csv, io, base64, uuid, datetime
import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
COLUNAS = {"data", "produto", "quantidade", "preco_unitario"}
MAX_BYTES = 1_000_000

def resp(status, body):
    return {"statusCode": status,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body, ensure_ascii=False)}

def lambda_handler(event, context):
    corpo = event.get("body") or ""
    if event.get("isBase64Encoded"):
        corpo = base64.b64decode(corpo).decode("utf-8", errors="replace")
    if not corpo or len(corpo.encode()) > MAX_BYTES:
        return resp(400, {"erro": "Arquivo vazio ou maior que 1 MB"})

    leitor = csv.DictReader(io.StringIO(corpo))
    if not leitor.fieldnames or not COLUNAS.issubset(set(leitor.fieldnames)):
        return resp(400, {"erro": "CSV inválido. Colunas esperadas: " + ", ".join(sorted(COLUNAS))})

    linhas = 0
    for linha in leitor:
        try:
            float(linha["quantidade"]); float(linha["preco_unitario"])
        except (ValueError, TypeError):
            return resp(400, {"erro": f"Valor numérico inválido na linha {linhas + 2}"})
        linhas += 1

    agora = datetime.datetime.now(datetime.timezone.utc)
    chave = f"vendas-csv/{agora:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}.csv"
    s3.put_object(Bucket=BUCKET, Key=chave, Body=corpo.encode("utf-8"), ContentType="text/csv")
    return resp(200, {"mensagem": "Arquivo salvo", "arquivo": chave, "linhas": linhas})
