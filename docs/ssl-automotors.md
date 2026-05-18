# 🔒 SSL no Projeto AutoMotors

## Sumário

1. [O que é SSL/TLS?](#1-o-que-é-ssltls)
2. [A Analogia dos Correios Blindados](#2-a-analogia-dos-correios-blindados)
3. [Como o SSL pode ser aplicado](#3-como-o-ssl-pode-ser-aplicado)
4. [Por que foi aplicado dessa forma no AutoMotors](#4-por-que-foi-aplicado-dessa-forma-no-automotors)
5. [Como foi aplicado no código](#5-como-foi-aplicado-no-código)
6. [Como verificar o SSL em execução](#6-como-verificar-o-ssl-em-execução)

---

## 1. O que é SSL/TLS?

**SSL** (*Secure Sockets Layer*) é um protocolo criptográfico que protege a comunicação entre o navegador do usuário e o servidor web. Seu sucessor moderno e tecnicamente correto se chama **TLS** (*Transport Layer Security*), mas o nome "SSL" ainda é o mais usado no dia a dia.

Quando uma conexão SSL/TLS é estabelecida:

1. **Autenticação** — O servidor apresenta um **certificado digital** que prova sua identidade. O navegador verifica se esse certificado é confiável (emitido por uma CA reconhecida).
2. **Troca de chaves** — Servidor e cliente combinam uma **chave de sessão** de forma segura usando criptografia assimétrica (RSA/ECDSA).
3. **Criptografia** — Todo o tráfego a partir daí é cifrado com criptografia simétrica (AES), impedindo que terceiros leiam os dados em trânsito.
4. **Integridade** — Um código de autenticação de mensagem (MAC/HMAC) garante que nenhum dado foi alterado no caminho.

O resultado visível para o usuário é o cadeado 🔒 na barra de endereço e a URL iniciando com `https://`.

---

## 2. A Analogia dos Correios Blindados

> Imagine que você precisa enviar um documento sigiloso (sua senha, número do cartão) pelo correio.

**Sem SSL (HTTP puro):**
Você coloca o documento num envelope comum, transparente. Qualquer carteiro, vizinho ou pessoa no caminho consegue ler o conteúdo. Se alguém substituir o documento por outro, você nunca vai saber.

**Com SSL (HTTPS):**
Você contrata um **serviço de malote blindado** com as seguintes garantias:

| Etapa | Correios Blindados (Analogia) | SSL/TLS (Técnico) |
|---|---|---|
| **Identificação** | O entregador mostra um crachá certificado pela empresa | O servidor apresenta o **certificado digital** (`.crt`) |
| **Lacre único** | A mala é trancada com uma chave que só você e o destinatário têm | **Handshake TLS** troca a chave de sessão com criptografia assimétrica |
| **Conteúdo blindado** | Todo o interior é opaco, ninguém lê em trânsito | Dados cifrados com **AES** (criptografia simétrica) |
| **Selo de integridade** | Um lacre lacrado quebra se alguém abrir no caminho | **HMAC** detecta qualquer alteração nos dados |

A **Autoridade Certificadora (CA)** é a empresa de segurança que emitiu o crachá do entregador — ela é quem diz "esse entregador é legítimo". No AutoMotors, nós criamos nossa própria mini-empresa de certificação (CA AutoMotors) para desenvolvimento local.

---

## 3. Como o SSL pode ser aplicado

Existem diferentes estratégias de aplicação do SSL em uma aplicação web:

### 3.1 HTTPS Global (mais comum em produção)
Todo e qualquer acesso ao site passa por HTTPS. O servidor HTTP redireciona automaticamente para HTTPS.

```
Usuário → http://site.com → 301 Redirect → https://site.com → Resposta cifrada
```

### 3.2 HTTPS Seletivo (aplicado neste projeto)
Apenas as rotas que lidam com dados sensíveis exigem HTTPS. Páginas públicas (catálogo, home) permanecem em HTTP para economizar processamento.

```
Usuário → http://site.com/catalogo  → Resposta HTTP (OK, página pública)
Usuário → http://site.com/login     → 301 Redirect → https://site.com:8443/login
```

### 3.3 Tipos de certificados
| Tipo | Emitido por | Custo | Uso |
|---|---|---|---|
| **Autoassinado** | Você mesmo | Gratuito | Desenvolvimento local |
| **CA privada** | CA criada internamente | Gratuito | Redes corporativas / acadêmico |
| **Let's Encrypt** | CA pública gratuita | Gratuito | Produção (sites reais) |
| **CA comercial** | DigiCert, Sectigo, etc. | Pago | Produção empresarial |

---

## 4. Por que foi aplicado dessa forma no AutoMotors

O enunciado do TPIII-SASI impõe uma **restrição explícita**: o sistema **NÃO pode ter HTTPS global** — caso contrário, perde-se 60% da nota. A exigência é demonstrar **HTTPS seletivo**: somente rotas com dados sensíveis devem ser servidas por HTTPS.

Além disso, o ambiente é de desenvolvimento local (sem domínio público), portanto não é possível usar Let's Encrypt. A solução foi criar uma **CA (Autoridade Certificadora) própria** com OpenSSL e assinar o certificado do servidor com ela.

### Resumo da estratégia adotada

```
┌─────────────────────────────────────────────────────────────────┐
│                       AutoMotors (dev local)                    │
│                                                                 │
│   processo 1 → manage.py runserver    → http://127.0.0.1:8000  │
│   processo 2 → manage.py runsslserver → https://127.0.0.1:8443 │
│                                                                 │
│   Decorator @ssl_required → redireciona HTTP ➜ HTTPS           │
│   Decorator @http_only    → redireciona HTTPS ➜ HTTP           │
└─────────────────────────────────────────────────────────────────┘
```

**Rotas protegidas por HTTPS (`@ssl_required`):**
- Login, Troca de Senha, Reset de Senha
- Cadastro de novo usuário (`signup`)
- Página de perfil (CPF, endereço, telefone)
- Histórico de interesses do usuário
- Carrinho de compras (add, view, remove, update)
- Painel administrativo (`/admin/`)

**Rotas mantidas em HTTP (`@http_only`):**
- Home / Landing page
- Catálogo de veículos (público)

**Caso especial — Logout (`/accounts/logout/`):**
O logout **não usa `@ssl_required`**. A view só destrói a sessão do servidor (não transmite credenciais nem dados sensíveis), então não há ganho de segurança em forçar HTTPS. Manter o logout no mesmo esquema do navbar (HTTP) também resolve um problema prático: o Chrome envia `Origin: null` em POSTs cross-scheme (HTTP → HTTPS), o que faria o CSRF do Django falhar mesmo com o token correto. A solução é manter logout same-origin.

---

## 5. Como foi aplicado no código

A implementação SSL do AutoMotors está distribuída em **cinco camadas**:

---

### 5.1 — Geração dos Certificados (`certs/`)

O script `certs/gerar-certificados.sh` cria toda a infraestrutura de certificados com OpenSSL:

```bash
# certs/gerar-certificados.sh

# Passo 1: Cria a chave privada da CA AutoMotors (4096 bits)
openssl genrsa -out ca.key 4096

# Passo 2: Gera o certificado raiz autoassinado (válido por 10 anos)
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
    -subj "/C=BR/ST=Minas Gerais/L=Diamantina/O=AutoMotors LTDA/OU=Certificate Authority/CN=AutoMotors Root CA" \
    -out ca.crt

# Passo 3: Cria a chave privada do servidor (2048 bits)
openssl genrsa -out server.key 2048

# Passo 4: Gera o CSR (pedido de assinatura) com Subject Alternative Names
openssl req -new -key server.key -out server.csr -config openssl-server.cnf

# Passo 5: A CA AutoMotors assina o certificado do servidor (válido por 2 anos)
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 730 -sha256 \
    -extensions v3_req -extfile openssl-server.cnf
```

O arquivo `certs/openssl-server.cnf` define os **Subject Alternative Names (SAN)** — nomes e IPs que o certificado cobre:

```ini
[ alt_names ]
DNS.1 = localhost
DNS.2 = automotors.local
DNS.3 = www.automotors.local
IP.1  = 127.0.0.1
IP.2  = ::1
```

> **Por que SAN?** Navegadores modernos exigem que o certificado declare explicitamente os domínios/IPs que cobre. Sem SAN, o Chrome/Firefox rejeita o certificado mesmo que o CN seja correto.

**Arquivos gerados:**
| Arquivo | Descrição |
|---|---|
| `ca.key` | Chave privada da CA (nunca deve ser exposta) |
| `ca.crt` | Certificado raiz — deve ser instalado no navegador como CA confiável |
| `server.key` | Chave privada do servidor Django |
| `server.csr` | Certificate Signing Request (intermediário) |
| `server.crt` | Certificado final do servidor, assinado pela CA |

---

### 5.2 — Patch de Compatibilidade (`automotors/_ssl_compat.py`)

O `django-sslserver` (versão 0.22, sem manutenção desde 2018) usa `ssl.wrap_socket()`, uma API removida no **Python 3.12**. Para resolver isso sem trocar de biblioteca, foi criado um *shim* (substituto de compatibilidade):

```python
# automotors/_ssl_compat.py

import ssl

if not hasattr(ssl, "wrap_socket"):
    # Python 3.12+ removeu ssl.wrap_socket — criamos um substituto moderno.
    def _wrap_socket_compat(
        sock,
        keyfile=None,
        certfile=None,
        server_side=False,
        cert_reqs=ssl.CERT_NONE,
        ssl_version=None,
        ca_certs=None,
        do_handshake_on_connect=True,
        suppress_ragged_eofs=True,
        ciphers=None,
    ):
        """Substituto moderno de ssl.wrap_socket() usando SSLContext."""
        # Escolhe o protocolo correto (servidor ou cliente TLS)
        protocol = ssl.PROTOCOL_TLS_SERVER if server_side else ssl.PROTOCOL_TLS_CLIENT
        context = ssl.SSLContext(protocol)

        if certfile:
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        if ca_certs:
            context.load_verify_locations(cafile=ca_certs)
        if cert_reqs is not None:
            context.verify_mode = cert_reqs
        if ciphers:
            context.set_ciphers(ciphers)

        return context.wrap_socket(
            sock,
            server_side=server_side,
            do_handshake_on_connect=do_handshake_on_connect,
            suppress_ragged_eofs=suppress_ragged_eofs,
        )

    # "Remenda" o módulo ssl com o substituto antes de qualquer import do sslserver
    ssl.wrap_socket = _wrap_socket_compat
```

Este patch é carregado **antes de qualquer outro código Django**, via `automotors/__init__.py`:

```python
# automotors/__init__.py
from . import _ssl_compat  # noqa: F401
```

---

### 5.3 — Configurações Django (`automotors/settings.py`)

```python
# automotors/settings.py

# Hosts de cada protocolo
AUTOMOTORS_HTTP_HOST  = 'localhost:8000'
AUTOMOTORS_HTTPS_HOST = 'localhost:8443'

# CSRF aceita requisições dos dois protocolos
CSRF_TRUSTED_ORIGINS = [
    f'http://{AUTOMOTORS_HTTP_HOST}',
    f'https://{AUTOMOTORS_HTTPS_HOST}',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8443',
]

# Cookies de sessão precisam fluir entre HTTP e HTTPS
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE    = False

# NÃO forçar HTTPS global (requisito do enunciado)
SECURE_SSL_REDIRECT   = False
SECURE_HSTS_SECONDS   = 0

# Informa ao Django o protocolo real quando há proxy reverso
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    # ...
    'sslserver',  # habilita: python manage.py runsslserver
    # ...
]
```

> **`SESSION_COOKIE_SECURE = False`**: Em produção esse valor seria `True` (cookie só enviado em HTTPS). Aqui é `False` porque o usuário faz login em HTTPS (8443) mas depois navega em HTTP (8000) — o cookie de sessão precisa seguir junto.

---

### 5.4 — Decorators de Redirecionamento (`home/decorators.py`)

A lógica central do HTTPS seletivo está em dois decorators:

```python
# home/decorators.py

from functools import wraps
from django.conf import settings
from django.http import HttpResponseRedirect


def _redirect_to(host: str, request) -> HttpResponseRedirect:
    """Constrói o redirect preservando path + query string."""
    return HttpResponseRedirect(host + request.get_full_path())


def ssl_required(view_func):
    """
    Garante que a view só seja servida em HTTPS.
    Se o request chega por HTTP → redireciona para o host HTTPS.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        https_host = getattr(settings, 'AUTOMOTORS_HTTPS_HOST', '')
        if request.is_secure() or not https_host:
            return view_func(request, *args, **kwargs)      # já está em HTTPS
        return _redirect_to(f'https://{https_host}', request)  # redireciona

    return _wrapped


def http_only(view_func):
    """
    Devolve a navegação pública para HTTP.
    Se o request chega por HTTPS → redireciona para o host HTTP.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        http_host = getattr(settings, 'AUTOMOTORS_HTTP_HOST', '')
        if not request.is_secure() or not http_host:
            return view_func(request, *args, **kwargs)     # já está em HTTP
        return _redirect_to(f'http://{http_host}', request)   # redireciona

    return _wrapped
```

---

### 5.5 — Aplicação dos Decorators nas Views

#### `home/views.py` — Rotas da aplicação home

```python
from .decorators import ssl_required, http_only

@http_only          # Página pública → mantém em HTTP
def index(request):
    ...

@ssl_required       # Coleta email + senha → exige HTTPS
def signup_view(request):
    ...

@ssl_required       # CPF, endereço, telefone → exige HTTPS
@login_required
def perfil_view(request):
    ...

@ssl_required       # Lista privada do usuário → exige HTTPS
@login_required
def meu_historico_view(request):
    ...
```

#### `cart/views.py` — Carrinho de compras

```python
from home.decorators import ssl_required

@ssl_required       # Adicionar ao carrinho → exige HTTPS
@login_required
def add_to_cart(request, item_id): ...

@ssl_required       # Ver carrinho → exige HTTPS
@login_required
def view_cart(request): ...

@ssl_required       # Remover item → exige HTTPS
@login_required
def remove_from_cart(request, cart_item_id): ...

@ssl_required       # Atualizar quantidade → exige HTTPS
@login_required
def update_cart_item(request, cart_item_id): ...
```

#### `automotors/urls.py` — Views do Django Auth e Admin

Como as views de autenticação nativas do Django não são nossas views, não dá para usar o decorator diretamente na definição da função. A solução foi envolvê-las no momento do registro de URL:

```python
from home.decorators import ssl_required

auth_https_patterns = [
    path('login/',    ssl_required(auth_views.LoginView.as_view()),    name='login'),
    # Logout fica fora do ssl_required: ver "Caso especial — Logout" na seção 4.
    path('logout/',   auth_views.LogoutView.as_view(),                 name='logout'),
    path('password_change/', ssl_required(auth_views.PasswordChangeView.as_view()), ...),
    # ... demais rotas de senha
]

# Protege o login/logout do painel admin também
admin.site.login  = ssl_required(admin.site.login)
admin.site.logout = ssl_required(admin.site.logout)
```

#### `garagem/management/commands/seed_garagem.py` — Download de fotos com SSL

No comando de seed que popula o banco com dados de exemplo, o SSL é usado para fazer downloads seguros de imagens do Unsplash:

```python
import ssl
import urllib.request

# Cria um contexto SSL padrão (valida certificados do servidor remoto)
ctx = ssl.create_default_context()
req = urllib.request.Request(foto_url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
    content = resp.read()
```

> Aqui o SSL é usado no lado **cliente** — o Python valida o certificado do Unsplash antes de baixar a imagem, evitando ataques man-in-the-middle.

---

## 6. Como verificar o SSL em execução

### 6.1 Iniciar os servidores

```bash
# Opção 1: script automático (recomendado)
bash iniciar-automotors.sh

# Opção 2: manual em dois terminais
# Terminal 1 — HTTP
python3 manage.py runserver 127.0.0.1:8000

# Terminal 2 — HTTPS
python3 manage.py runsslserver \
    --certificate certs/server.crt \
    --key         certs/server.key \
    127.0.0.1:8443
```

### 6.2 Instalar o certificado CA no navegador

Para que o navegador confie no certificado local (sem mostrar aviso de segurança):

1. Abra as **Configurações** do navegador
2. Vá em **Segurança → Certificados → Autoridades**
3. Importe o arquivo `certs/ca.crt`
4. Marque como confiável para **identificar sites**

### 6.3 Testar o redirecionamento

| Ação | Esperado |
|---|---|
| Acessar `http://localhost:8000/` | Página inicial em HTTP ✅ |
| Acessar `http://localhost:8000/accounts/login/` | Redireciona para `https://localhost:8443/accounts/login/` 🔒 |
| Acessar `https://localhost:8443/` | Redireciona para `http://localhost:8000/` (http_only) ↩️ |
| Acessar `https://localhost:8443/accounts/login/` | Página de login em HTTPS ✅ |
| Cadeado no navegador em `/accounts/login/` | 🔒 Conexão segura |

### 6.4 Verificar o certificado via linha de comando

```bash
# Ver detalhes do certificado do servidor
openssl x509 -in certs/server.crt -text -noout

# Testar handshake TLS com o servidor local
openssl s_client -connect 127.0.0.1:8443 -CAfile certs/ca.crt
```

---

## Arquitetura Geral — Diagrama de Fluxo

```
Navegador
   │
   ├─── GET http://localhost:8000/              ──▶ runserver:8000
   │                                                   │ @http_only → OK
   │                                                   └▶ Renderiza index.html
   │
   ├─── GET http://localhost:8000/accounts/login/ ──▶ runserver:8000
   │                                                   │ @ssl_required → não é HTTPS
   │                                                   └▶ 301 Redirect
   │                                                          │
   │    ◀─────────────── 301 Location: https://localhost:8443/accounts/login/
   │
   └─── GET https://localhost:8443/accounts/login/ ──▶ runsslserver:8443
                                                          │ Handshake TLS (server.crt)
                                                          │ @ssl_required → é HTTPS → OK
                                                          └▶ Renderiza login.html 🔒
```

---

*Documento gerado para o TPIII-SASI — AutoMotors (2026/01)*
