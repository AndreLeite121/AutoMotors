#!/usr/bin/env bash
# AutoMotors — Geração de certificados digitais com OpenSSL
# Uso: bash certs/gerar-certificados.sh
#
# Produz:
#   ca.key           Chave privada da Autoridade Certificadora AutoMotors
#   ca.crt           Certificado raiz autoassinado (instalar no navegador como CA confiável)
#   server.key       Chave privada do servidor
#   server.csr       Certificate Signing Request do servidor
#   server.crt       Certificado do servidor assinado pela CA AutoMotors

set -euo pipefail
cd "$(dirname "$0")"

# ----------------------------------------------------------------------
# 1) Autoridade Certificadora (CA AutoMotors) — raiz autoassinada
# ----------------------------------------------------------------------
echo "==> 1/5 Gerando chave privada da CA (4096 bits)..."
openssl genrsa -out ca.key 4096

echo "==> 2/5 Gerando certificado raiz autoassinado (validade 10 anos)..."
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
    -subj "/C=BR/ST=Minas Gerais/L=Diamantina/O=AutoMotors LTDA/OU=Certificate Authority/CN=AutoMotors Root CA" \
    -out ca.crt

# ----------------------------------------------------------------------
# 2) Chave privada do servidor + CSR
# ----------------------------------------------------------------------
echo "==> 3/5 Gerando chave privada do servidor (2048 bits)..."
openssl genrsa -out server.key 2048

echo "==> 4/5 Gerando Certificate Signing Request (CSR) com SAN..."
openssl req -new -key server.key -out server.csr -config openssl-server.cnf

# ----------------------------------------------------------------------
# 3) Assinar o cert do servidor com a CA AutoMotors
# ----------------------------------------------------------------------
echo "==> 5/5 Assinando certificado do servidor com a CA (validade 2 anos)..."
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 730 -sha256 \
    -extensions v3_req -extfile openssl-server.cnf

# ----------------------------------------------------------------------
# 4) Resumo
# ----------------------------------------------------------------------
echo ""
echo "✅ Certificados gerados em $(pwd):"
ls -lh ca.key ca.crt server.key server.csr server.crt 2>/dev/null

echo ""
echo "📌 Próximos passos:"
echo "   1. Instale ca.crt no navegador como Autoridade Certificadora confiável."
echo "   2. Inicie o servidor HTTPS:"
echo "        python3 manage.py runsslserver --certificate certs/server.crt \\"
echo "                                       --key         certs/server.key  \\"
echo "                                       127.0.0.1:8443"
echo "   3. Em outro terminal, inicie o HTTP:"
echo "        python3 manage.py runserver 127.0.0.1:8000"
