# Atendimento ao Enunciado — TPIII-SASI / AutoMotors

Este documento mapeia **cada exigência do enunciado** para o local exato do
código onde foi implementada, com a justificativa da decisão. A intenção é
servir tanto de roteiro de apresentação quanto de checklist para a auditoria
do TPIV-SASI.

---

## 1. Definir o sistema web

> "Definir o sistema web: comércio eletrônico, banco, instituições federais,
> receita federal, etc., de acordo com a empresa criada no primeiro trabalho
> (TPI_SASI)."

**O quê.** O sistema é a **AutoMotors**, e-commerce de veículos seminovos
(automotivo). É a continuidade da empresa modelada no TPI_SASI.

**Onde.**

| Camada | Arquivo / pasta |
|---|---|
| Projeto Django | `automotors/` (settings, urls, wsgi, asgi) |
| Catálogo de veículos | `garagem/` (model `Veiculo`, `VeiculoFoto`) |
| Acessórios automotivos | `acessorios/` (model `Acessorio`) |
| Carrinho de interesse | `cart/` (`Cart`, `CartItem`) |
| Home / perfil / histórico | `home/` (`UserProfile`, `HistoricoInteresse`, `Review`) |

**Por quê.** O domínio "venda de veículos seminovos" tem todos os elementos
exigidos pelo enunciado: catálogo público (não-sensível), cadastro com
dados pessoais (CPF, endereço — sensíveis), histórico do usuário e fluxo de
"interesse" (carrinho). Permite demonstrar **HTTPS seletivo** com clareza.

---

## 2. Gerar certificados digitais e chaves com OpenSSL

> "Gerar os certificados digitais e chaves públicas e privadas utilizando openssl."

**O quê.** Criamos uma **CA própria (AutoMotors Root CA)** que assina o
certificado do servidor — duas etapas de PKI completa, em vez de um
autoassinado raso.

**Onde.**

- `certs/gerar-certificados.sh` — script único que gera todos os artefatos.
- `certs/openssl-server.cnf` — configuração com **SAN** (Subject Alternative
  Names: `localhost`, `automotors.local`, `127.0.0.1`, `::1`).
- `certs/` — saída: `ca.key`, `ca.crt`, `server.key`, `server.csr`,
  `server.crt`.

**Como.** Resumo do `gerar-certificados.sh`:

```bash
openssl genrsa -out ca.key 4096                       # chave privada da CA
openssl req -x509 -new -nodes -key ca.key ... -out ca.crt   # cert raiz autoassinado (10 anos)
openssl genrsa -out server.key 2048                   # chave privada do servidor
openssl req -new -key server.key -out server.csr -config openssl-server.cnf   # CSR
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key ... -out server.crt # CA assina o cert
```

**Por quê.**
- **CA própria, não autoassinado direto:** ensina o fluxo real
  (root → intermediate-like → server) e demonstra a cadeia de confiança que
  navegadores exigem.
- **4096 bits na CA, 2048 no servidor:** CA é raiz de confiança e raramente
  rotaciona — quanto mais forte, melhor. Servidor rotaciona mais e 2048 já é
  considerado seguro até 2030+ pelo NIST.
- **SAN obrigatório:** desde 2017 (Chrome 58) o `CN` é ignorado; sem SAN o
  navegador rejeita o certificado com `NET::ERR_CERT_COMMON_NAME_INVALID`.

> O tutorial completo, passo a passo, está em [`tutorial-openssl.md`](tutorial-openssl.md).

---

## 3. Proteger login/senha e dados sensíveis (cartão, CPF, etc.)

> "Implementar o uso de certificação digital no seu site para proteger o
> envio do login e senha e para proteger as informações importantes
> (cartão de crédito, cpf, etc)."

**O quê.** Rotas que recebem ou exibem dados sensíveis ficam **somente em
HTTPS** (`runsslserver` na porta 8443). Rotas públicas seguem em HTTP puro
(porta 8000). Dois decorators garantem a porta correta — invertendo o
redirect quando o usuário tenta o esquema errado.

**Onde.**

| Rota | Sensibilidade | Decorator | Arquivo |
|---|---|---|---|
| `/accounts/login/` | senha | `ssl_required` (no registro da URL) | `automotors/urls.py:16` |
| `/accounts/password_change/`, `password_reset/...` | senha | `ssl_required` | `automotors/urls.py:25-40` |
| `/signup/` | senha + e-mail | `@ssl_required` | `home/views.py:36` |
| `/perfil/` | CPF, CEP, endereço, telefone | `@ssl_required` | `home/views.py:51` |
| `/meu-historico/` | histórico privado | `@ssl_required` | `home/views.py:77` |
| `/interesse/...` (carrinho add/view/remove/update) | escolhas privadas + intent de compra | `@ssl_required` | `cart/views.py:11,72,80,88` |
| `/admin/` | credenciais administrativas | `ssl_required(admin.site.login/logout)` | `automotors/urls.py:46-47` |

**Como** o redirect funciona — núcleo em `home/decorators.py`:

```python
def ssl_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        https_host = settings.AUTOMOTORS_HTTPS_HOST     # 'localhost:8443'
        if request.is_secure() or not https_host:
            return view_func(request, *args, **kwargs)  # já está em HTTPS, segue
        return HttpResponseRedirect(f'https://{https_host}{request.get_full_path()}')
    return _wrapped
```

O decorator irmão `http_only` faz o caminho inverso (HTTPS → HTTP) para
páginas públicas, evitando que o usuário fique "preso" no HTTPS depois de
sair do login.

**Por quê.**
- **Cartão de crédito não foi implementado** porque o fluxo de negócio
  modelado é "manifestação de interesse" (típico de seminovos — concessionária
  fecha a venda offline). Os dados realmente sensíveis que entram no sistema
  são **senha, CPF, CEP, endereço e telefone**. Todos protegidos.
- **Decorator, e não middleware global,** porque o enunciado proíbe HTTPS
  global ("se o certificado for implementado com atuação global, em todo
  sistema será descontado 60% da nota"). Decorator por view dá granularidade.
- **`is_secure()`** consulta `request.scheme == 'https'` levando em conta o
  `SECURE_PROXY_SSL_HEADER` — funciona tanto no dev local quanto atrás de
  um Nginx.

**Caso especial — logout (`/accounts/logout/`).** *Não* usa `ssl_required`.
Justificativas no doc [`ssl-automotors.md` §4](ssl-automotors.md): (a) logout
só destrói sessão, não trafega credenciais; (b) Chrome envia `Origin: null`
em POST cross-scheme, quebrando o CSRF — manter o logout same-origin (HTTP→HTTP
ou HTTPS→HTTPS conforme o navbar) resolve sem afrouxar segurança real.

---

## 4. Funcionalidades básicas do negócio

> "O sistema deverá ter funcionalidades básicas de acordo com o negócio
> escolhido."

**O quê.** Catálogo, detalhes, carrinho de interesse, gestão de perfil e
seções institucionais.

**Onde.**

| Funcionalidade | URL | View |
|---|---|---|
| Home / landing institucional | `/` | `home/views.py:index` |
| Garagem (catálogo) | `/garagem/` | `garagem/views.py` |
| Detalhe do veículo | `/garagem/<id>/` | `garagem/views.py` |
| Loja de acessórios | `/acessorios/` | `acessorios/views.py` |
| Carrinho de interesse | `/interesse/` | `cart/views.py` |
| Cadastro de usuário | `/signup/` | `home/views.py:signup_view` |
| Perfil (CPF/endereço) | `/perfil/` | `home/views.py:perfil_view` |
| Meu histórico | `/meu-historico/` | `home/views.py:meu_historico_view` |
| Admin Django | `/admin/` | wrap em `ssl_required` |

**Por quê.** A combinação de áreas públicas (catálogo) com áreas
autenticadas (perfil, carrinho) é o que torna o exercício de HTTPS seletivo
visível: o usuário transita pelos dois esquemas dentro do mesmo site.

---

## 5. Política de segurança apresentada no site

> "...deverá conter a política de segurança da empresa apresentada no site."

**O quê.** Página pública dedicada à Política de Segurança da Informação,
referenciada da home.

**Onde.**

- Template: `home/templates/home/politica_de_privacidade.html`
- URL: `/politica-de-privacidade/` em `home/urls.py:23`
- Decorator: `@http_only` (rota pública, sem dados sensíveis)
- CTA na home: `home/templates/index.html` — botão "Política de segurança" no hero

**Conteúdo coberto.** Princípios (CIA), dados coletados e finalidade, base
legal (LGPD — Lei 13.709/2018), retenção, direitos do titular, contato do
DPO.

**Por quê.** O enunciado exige a política "apresentada no site", e o ponto
8 reforça que a página social inicial deve apresentar empresa **e** política
de segurança. Por isso o link aparece em destaque no hero da home, além de
estar no footer.

---

## 6. Tutorial OpenSSL para entrega

> "Deverá ser redigido um tutorial de como se implementar os certificados e
> chaves usando o openssl."

**O quê.** Tutorial passo-a-passo, autossuficiente, em
[`docs/tutorial-openssl.md`](tutorial-openssl.md). Cobre:

1. Conceitos (CA, chave privada/pública, CSR, certificado, SAN).
2. Geração da CA AutoMotors.
3. Geração da chave + CSR do servidor com SAN.
4. Assinatura do certificado pela CA.
5. Configuração no `runsslserver` (Django).
6. Instalação da CA no Keychain (macOS) — também em [`passos-finais.md`](passos-finais.md).
7. Verificação via `openssl x509 -text -noout` e `openssl s_client`.

**Por quê.** É exigência explícita de entrega via Classroom. Foi escrito
em português, com comandos prontos para copiar, para servir tanto à banca
quanto ao grupo que for nos auditar no TPIV.

---

## 7. HTTPS seletivo (NÃO global) — penalidade de 60%

> "Se o certificado for implementado com atuação global, em todo sistema
> será descontado 60% da nota."

**O quê.** Garantimos por **três mecanismos independentes** que o HTTPS
permanece seletivo:

1. **Dois servidores distintos** em portas distintas:
   - `runserver  127.0.0.1:8000` (HTTP)
   - `runsslserver 127.0.0.1:8443 --certificate certs/server.crt --key certs/server.key` (HTTPS)
   - Subidos juntos por `iniciar-automotors.sh`.

2. **Settings explícitos contra HTTPS global** em `automotors/settings.py`:
   ```python
   SECURE_SSL_REDIRECT = False    # Django NÃO redireciona HTTP→HTTPS automaticamente
   SECURE_HSTS_SECONDS = 0        # navegador NÃO é instruído a fixar HTTPS
   SESSION_COOKIE_SECURE = False  # cookie de sessão pode trafegar em HTTP
   CSRF_COOKIE_SECURE = False
   ```

3. **Decorators por view** (`ssl_required` / `http_only`) — só rotas
   explicitamente decoradas mudam de esquema.

**Por quê.** Cada um sozinho não bastaria: sem (2), bastaria ativar HSTS
acidentalmente e o navegador fixaria HTTPS para sempre — equivalente a
global. Sem (3), seria fácil esquecer uma rota e expor dados. Sem (1), não
haveria como demonstrar a coexistência dos dois esquemas.

**Resultado verificável (smoke test):**

```
GET http://localhost:8000/                         → 200  (HTTP puro, OK)
GET http://localhost:8000/accounts/login/          → 302  Location: https://localhost:8443/...
GET https://localhost:8443/                        → 302  Location: http://localhost:8000/...
GET https://localhost:8443/accounts/login/         → 200  🔒
```

---

## 8. Página social inicial direcionando para login HTTPS

> "Caso o sistema tenha característica de login inicial, deverá ser criada
> uma página social (http padrão) apresentando a empresa e a política de
> segurança, sendo que essa página direciona para a página de login
> (nesse caso https)."

**O quê.** A home (`/`) é a página social pública em HTTP, com:

- **Apresentação da empresa** — hero com proposta de valor, número de
  veículos vistoriados, garantia.
- **CTA para Política de segurança** — botão direto no hero (`index.html:25`).
- **CTA para Login** — botão "Entrar" no navbar, apontando para
  `{{ HTTPS_BASE }}{% url 'login' %}`, que resolve para
  `https://localhost:8443/accounts/login/`.
- **CTA para Cadastro** — botão "Cadastrar", mesma lógica, vai para
  `/signup/` em HTTPS.

**Como o link decide o esquema.** O context processor
`home/context_processors.py` injeta `HTTPS_BASE` em todos os templates, com o
valor `https://localhost:8443`. Templates concatenam esse prefixo nos links
que **devem** sair em HTTPS, sem depender de o redirect rodar.

**Por quê.** Anexar o esquema-alvo na origem do link em vez de confiar só
no redirect tem três vantagens:
1. **UX** — usuário não vê o flash do 302.
2. **Performance** — evita um roundtrip extra.
3. **Segurança** — fecha uma janela teórica de downgrade: o redirect HTTP→HTTPS
   ainda parte de uma página HTTP, ou seja, um MITM ativo poderia interceptar
   o redirect e levar o usuário para um clone. Pré-resolver o link em HTTPS
   reduz a superfície (o redirect continua existindo como defesa em
   profundidade caso alguém digite à mão).

---

## Resumo da auditoria

| Exigência do enunciado | Atende? | Referência principal |
|---|---|---|
| 1. Sistema definido (TPI_SASI) | ✅ | `automotors/`, `garagem/`, `acessorios/`, `cart/`, `home/` |
| 2. Certificados via OpenSSL | ✅ | `certs/gerar-certificados.sh` + `openssl-server.cnf` |
| 3. HTTPS protege credenciais e dados sensíveis | ✅ | `home/decorators.py` + `@ssl_required` nas views |
| 4. Funcionalidades do negócio | ✅ | URLs em `automotors/urls.py` |
| 5. Política de segurança no site | ✅ | `home/templates/home/politica_de_privacidade.html` |
| 6. Tutorial OpenSSL | ✅ | `docs/tutorial-openssl.md` |
| 7. HTTPS NÃO global (proibido pelo enunciado) | ✅ | dois servidores + settings + decorators |
| 8. Página social HTTP → login HTTPS | ✅ | `home/templates/index.html` + `HTTPS_BASE` context processor |

**Cobertura: 100%.**
