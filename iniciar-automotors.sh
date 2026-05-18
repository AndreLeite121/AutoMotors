#!/usr/bin/env bash
# AutoMotors — sobe os dois servidores em paralelo
#   HTTP   → 127.0.0.1:8000  (catálogo, home, política, ajuda)
#   HTTPS  → 127.0.0.1:8443  (login, cadastro, perfil, interesses)

set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f certs/server.crt ] || [ ! -f certs/server.key ]; then
    echo "❌ Certificados não encontrados em certs/."
    echo "   Rode primeiro:  bash certs/gerar-certificados.sh"
    exit 1
fi

cleanup() {
    echo ""
    echo "⏹  Encerrando servidores..."
    kill $HTTP_PID $HTTPS_PID 2>/dev/null || true
    wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "▶️  HTTP em  http://127.0.0.1:8000  (páginas públicas)"
python3 manage.py runserver 127.0.0.1:8000 --noreload &
HTTP_PID=$!

sleep 1

echo "🔒 HTTPS em https://127.0.0.1:8443 (páginas sensíveis)"
python3 manage.py runsslserver --certificate certs/server.crt \
                               --key         certs/server.key  \
                               127.0.0.1:8443 --noreload &
HTTPS_PID=$!

echo ""
echo "  Ctrl+C encerra os dois processos."
wait
