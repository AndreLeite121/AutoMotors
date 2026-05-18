# Tutorial — Certificação Digital com OpenSSL
**AutoMotors**

Este tutorial mostra como gerar e usar certificados digitais próprios (CA + servidor) com OpenSSL para proteger o tráfego de páginas sensíveis do sistema AutoMotors.

---

## 1. Conceitos rápidos

| Termo | O que é |
|---|---|
| **CA (Certificate Authority)** | Entidade que emite e assina certificados. Aqui criamos a nossa própria, **AutoMotors Root CA**. |
| **Chave privada** (`.key`) | Segredo do dono. Nunca sai do servidor (ou da CA). Fica protegida em disco. |
| **Chave pública** | Vai dentro do certificado, é distribuída pra qualquer um. |
| **CSR (Certificate Signing Request)** | Pedido formal de "emite um certificado pra essa chave pública", contendo dados do requisitante (CN, O, OU…). |
| **Certificado (`.crt`)** | Documento assinado pela CA que liga uma chave pública a uma identidade (ex: `CN=localhost`). |
| **SAN (Subject Alternative Name)** | Lista de hosts/IPs adicionais que o certificado cobre. Hoje é obrigatório — navegadores ignoram o CN. |

**Cadeia de confiança:** o navegador confia no servidor porque o certificado dele foi assinado pela CA, e o navegador tem a CA marcada como confiável.

---

## 2. Pré-requisitos

```bash
# macOS (via Homebrew)
brew install openssl

# Ubuntu / Debian
sudo apt update && sudo apt install -y openssl

# Verificar versão (>= 1.1 ou >= 3.x)
openssl version
```

Saída esperada: `OpenSSL 3.5.0 8 Apr 2025` (ou similar 1.1+).

---

## 3. Geração dos certificados — passo a passo

Toda a operação acontece dentro de `certs/` no projeto AutoMotors. O script `gerar-certificados.sh` automatiza tudo, mas vamos fazer manualmente uma vez para entender cada passo.

### 3.1 Chave privada da CA AutoMotors

```bash
cd certs/
openssl genrsa -out ca.key 4096
```

- `genrsa` gera chave RSA
- `4096` bits — robusto para CA (resistente a ataques modernos)
- saída: `ca.key` (mantém em sigilo absoluto, modo 600)

### 3.2 Certificado raiz autoassinado da CA

```bash
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
    -subj "/C=BR/ST=Minas Gerais/L=Diamantina/O=AutoMotors LTDA/OU=Certificate Authority/CN=AutoMotors Root CA" \
    -out ca.crt
```

- `-x509` cria certificado autoassinado (raiz da cadeia)
- `-nodes` não criptografa a chave com senha (para automação acadêmica)
- `-days 3650` validade de 10 anos
- `-subj` evita prompt interativo
- saída: `ca.crt` (pode ser distribuído publicamente)

### 3.3 Chave privada do servidor

```bash
openssl genrsa -out server.key 2048
```

2048 bits é o padrão atual recomendado para servidores web.

### 3.4 CSR do servidor

Primeiro, o arquivo de configuração `openssl-server.cnf` com SAN:

```ini
[ req ]
default_bits        = 2048
default_md          = sha256
prompt              = no
distinguished_name  = req_dn
req_extensions      = v3_req

[ req_dn ]
C  = BR
ST = Minas Gerais
L  = Diamantina
O  = AutoMotors LTDA
OU = E-commerce
CN = localhost

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage         = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName   = @alt_names

[ alt_names ]
DNS.1 = localhost
DNS.2 = automotors.local
DNS.3 = www.automotors.local
IP.1  = 127.0.0.1
IP.2  = ::1
```

Gerando o CSR:

```bash
openssl req -new -key server.key -out server.csr -config openssl-server.cnf
```

- `-new` novo CSR
- `-config` lê a configuração com SAN
- saída: `server.csr` (envia pra CA)

### 3.5 CA assina o certificado do servidor

```bash
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 730 -sha256 \
    -extensions v3_req -extfile openssl-server.cnf
```

- `-in server.csr` o pedido
- `-CA ca.crt` certificado da CA (identidade)
- `-CAkey ca.key` chave privada da CA (para assinar)
- `-CAcreateserial` cria/atualiza `ca.srl` (número de série dos certs emitidos)
- `-extensions v3_req -extfile ...` reaplica o SAN no certificado final
- saída: `server.crt` (instala no servidor web)

### 3.6 Validação da cadeia

```bash
# Verifica que o cert do servidor foi assinado pela nossa CA
openssl verify -CAfile ca.crt server.crt
# server.crt: OK

# Inspeciona o certificado
openssl x509 -in server.crt -noout -subject -issuer -dates
openssl x509 -in server.crt -noout -ext subjectAltName
```

Saída esperada:
```
subject=C=BR, ST=Minas Gerais, ..., CN=localhost
issuer=C=BR, ..., CN=AutoMotors Root CA
notBefore=May 15 13:11:15 2026 GMT
notAfter=May 14 13:11:15 2028 GMT

X509v3 Subject Alternative Name:
    DNS:localhost, DNS:automotors.local, DNS:www.automotors.local,
    IP Address:127.0.0.1, IP Address:0:0:0:0:0:0:0:1
```

---

## 4. Instalar a CA AutoMotors no navegador

Sem instalar a CA como "confiável" no navegador, o `ca.crt` é desconhecido e qualquer página em HTTPS vai disparar o alerta vermelho de "Sua conexão não é privada".

### Firefox

1. `about:preferences#privacy` → seção **Certificados** → **Ver certificados**
2. Aba **Autoridades** → **Importar**
3. Selecione `certs/ca.crt`
4. Marque ✔ **Confiar nesta CA para identificar sites**
5. OK

### Chrome / Edge / Brave (macOS)

1. Abra o **Keychain Access** (Acesso às Chaves)
2. Arraste `certs/ca.crt` para **System** ou **login**
3. Duplo clique no cert importado → **Trust** → **When using this certificate: Always Trust**
4. Reinicie o navegador

### Chrome / Edge (Linux)

```bash
# Importa para o repositório de CAs do sistema
sudo cp certs/ca.crt /usr/local/share/ca-certificates/automotors-ca.crt
sudo update-ca-certificates
```

### Safari (macOS)

Mesmo procedimento do Chrome — Safari usa o Keychain do sistema.

---

## 5. Configurar o Django com os certificados

A AutoMotors usa **dois processos Django em paralelo**:

| Processo | Porta | Comando | Serve |
|---|---|---|---|
| HTTP | 8000 | `python manage.py runserver 127.0.0.1:8000` | Páginas públicas |
| HTTPS | 8443 | `python manage.py runsslserver --certificate certs/server.crt --key certs/server.key 127.0.0.1:8443` | Páginas sensíveis |

Para conveniência, o projeto tem `iniciar-automotors.sh` que sobe os dois ao mesmo tempo:

```bash
bash iniciar-automotors.sh
```

### Como o Django sabe quando redirecionar?

Os decorators em `home/decorators.py`:

- `@ssl_required` — força HTTPS. Se a view receber HTTP, devolve 302 para `https://localhost:8443/...`
- `@http_only` — devolve HTTPS público para HTTP (cumpre exigência do TPIII de NÃO ter HTTPS global)

Exemplo de uso:

```python
from home.decorators import ssl_required, http_only

@ssl_required
@login_required
def perfil_view(request):
    """Edita CPF, telefone e endereço — sempre HTTPS."""
    ...

@http_only
def index(request):
    """Landing pública — sempre HTTP por economia."""
    ...
```

---

## 6. Mapeamento de rotas AutoMotors

| Rota | Protocolo | Justificativa |
|---|---|---|
| `/` | HTTP | Página social pública — sem dado sensível |
| `/garagem/` | HTTP | Catálogo público |
| `/garagem/detalhes/<id>` | HTTP | Detalhe de carro — público |
| `/acessorios/` | HTTP | Catálogo de acessórios — público |
| `/politica-de-privacidade/` | HTTP | Documento público |
| `/termos-e-condicoes/` | HTTP | Documento público |
| `/central-de-ajuda/` | HTTP | Documento público |
| `/accounts/login/` | **HTTPS** | Recebe senha |
| `/accounts/logout/` | **HTTPS** | Encerra sessão |
| `/accounts/password_reset/` | **HTTPS** | Recebe email + token |
| `/signup/` | **HTTPS** | Recebe senha |
| `/perfil/` | **HTTPS** | Lê e escreve CPF, telefone, endereço |
| `/meu-historico/` | **HTTPS** | Lista privada do usuário |
| `/interesse/` | **HTTPS** | Lista privada do usuário |
| `/admin/` | **HTTPS** | Credenciais administrativas |

---

## 7. Teste de aceitação

Após instalar a CA no navegador e iniciar `iniciar-automotors.sh`:

1. Abra `http://localhost:8000/` → carrega normalmente em HTTP (sem cadeado)
2. Clique em **Entrar** no canto superior direito → URL muda para `https://localhost:8443/accounts/login/` com **cadeado verde** ao lado do endereço
3. Faça login → redireciona para `/` em HTTP novamente
4. Clique em **Meu perfil** no dropdown → URL muda para `https://localhost:8443/perfil/` com cadeado verde
5. Clique no nome **AutoMotors** → URL volta para `http://localhost:8000/`

Esse vai-e-vem entre os protocolos comprova o HTTPS seletivo e cumpre a exigência do enunciado.

---

## 8. Estrutura de arquivos gerados

```
certs/
├── openssl-server.cnf      # Configuração com SAN
├── gerar-certificados.sh   # Script que automatiza o pipeline
├── ca.key                  # 🔒 Chave privada da CA — NUNCA versionar
├── ca.crt                  # Certificado raiz da CA — distribui
├── ca.srl                  # Contador de série dos certs emitidos
├── server.key              # 🔒 Chave privada do servidor — NUNCA versionar
├── server.csr              # CSR enviado para a CA (descartável)
└── server.crt              # Certificado do servidor assinado pela CA
```

> ⚠️ Em produção, `ca.key` e `server.key` ficam fora do repositório git
> (`.gitignore` de `*.key`).

---

## 9. Glossário rápido

- **TLS** (antigamente SSL) — protocolo de transporte criptografado. HTTPS = HTTP sobre TLS.
- **PKI** (Public Key Infrastructure) — infraestrutura de chaves públicas: CAs, certs, listas de revogação.
- **X.509** — padrão de formato dos certificados que usamos.
- **PEM** — encoding base64 dos arquivos `.key`/`.crt` (o cabeçalho `-----BEGIN CERTIFICATE-----`).

---

**Entrega:** este arquivo (`tutorial-openssl.md`) + o diretório `certs/` zipado + screenshots do navegador mostrando o cadeado verde nas rotas HTTPS.
