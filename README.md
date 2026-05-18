# AutoMotors

Plataforma de e-commerce para concessionária de veículos seminovos, desenvolvida com Django como projeto acadêmico (TPIII — SASI).

---

## Visão Geral

O sistema simula uma loja online de veículos seminovos com catálogo de carros, seção de acessórios automotivos e lista de interesse (carrinho). O projeto implementa **HTTPS seletivo**: páginas públicas rodam em HTTP (porta 8000) e páginas sensíveis (login, perfil, carrinho) são servidas via HTTPS com certificado próprio (porta 8443).

---

## Funcionalidades

| Módulo | Descrição |
|---|---|
| **Garagem** | Catálogo de veículos com filtro por categoria, galeria de fotos e página de detalhes |
| **Acessórios** | Listagem de produtos e serviços automotivos |
| **Lista de Interesse** | Carrinho persistente com envio direto via WhatsApp |
| **Histórico** | Registro permanente de veículos que o usuário demonstrou interesse |
| **Autenticação** | Cadastro, login e troca de senha em HTTPS; logout em mesmo esquema do navbar |
| **Perfil** | Dados pessoais do cliente (CPF, telefone, endereço) — HTTPS obrigatório |
| **HTTPS Seletivo** | Certificado digital próprio (OpenSSL CA + servidor) com redirecionamento automático |
| **Admin** | Painel Django com gestão de veículos, fotos, acessórios e usuários |

---

## Tecnologias

- **Back-end:** Python 3 · Django 5
- **Front-end:** HTML5 · CSS3 · JavaScript · Bootstrap 5
- **Banco de dados:** SQLite 3 (desenvolvimento)
- **Segurança:** OpenSSL (CA própria) · `django-sslserver`
- **Seed:** comando `python manage.py seed_garagem`

---

## Estrutura de Apps

```
automotors/   → configuração principal do Django (settings, urls, wsgi)
garagem/      → catálogo de veículos (modelo Veiculo + VeiculoFoto)
acessorios/   → produtos e serviços automotivos (modelo Acessorio)
cart/         → lista de interesse do usuário
home/         → landing page, perfil, histórico, avaliações, decorators HTTPS
```

---

## Execução Local

### Requisitos

- Python 3.10+
- Git
- OpenSSL (para HTTPS — veja `docs/tutorial-openssl.md`)

### Passo a passo

**1. Clone o repositório:**
```bash
git clone https://github.com/AndreLeite121/AutoMotors.git
cd TPIII-SASI
```

**2. Crie e ative um ambiente virtual:**
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

**3. Instale as dependências:**
```bash
pip install -r requeriments.txt
```

**4. Execute as migrações:**
```bash
python3 manage.py migrate
```

**5. Crie um superusuário para acessar `/admin/`:**
```bash
python3 manage.py createsuperuser
```

**6. (Opcional) Popule o banco com dados de exemplo:**
```bash
# 9 veículos + 3 acessórios (baixa fotos de capa do Unsplash)
python3 manage.py seed_garagem

# Galeria de fotos múltiplas (usa a pasta Carros/ versionada no repo)
python3 manage.py import_fotos
```

**7. Certificados SSL:**

Os certificados já estão versionados em `certs/` (CA AutoMotors + cert do
servidor) para facilitar a avaliação acadêmica e a auditoria do TPIV.
Você pode usá-los direto ou regenerar:

```bash
# Regenerar do zero (opcional)
cd certs/
bash gerar-certificados.sh   # macOS / Linux
cd ..
```
> Veja o passo a passo completo em [`docs/tutorial-openssl.md`](docs/tutorial-openssl.md).
> Para o navegador confiar no certificado sem aviso, instale o `certs/ca.crt`
> no Keychain — instruções em [`docs/passos-finais.md`](docs/passos-finais.md).

> ⚠️ **Em produção real**, chaves privadas (`ca.key`, `server.key`) **nunca**
> devem ir para o repositório. Aqui são cert acadêmicos de localhost,
> descartáveis após a entrega.

**8. Inicie os dois servidores em paralelo:**

```bash
# macOS / Linux
bash iniciar-automotors.sh

# Windows — abra dois terminais separados:
# Terminal 1:
python manage.py runserver 127.0.0.1:8000
# Terminal 2:
python manage.py runsslserver --certificate certs/server.crt --key certs/server.key 127.0.0.1:8443
```

| Endereço | Conteúdo |
|---|---|
| `http://127.0.0.1:8000` | Páginas públicas (garagem, acessórios, home) |
| `https://127.0.0.1:8443` | Páginas sensíveis (login, perfil, carrinho) |

---

## Documentação

- [`docs/como-rodar.md`](docs/como-rodar.md) — **passo a passo completo de instalação para Linux e Windows** (do `git clone` ao servidor rodando)
- [`docs/tutorial-openssl.md`](docs/tutorial-openssl.md) — geração e uso dos certificados com OpenSSL (entregue via Classroom)
- [`docs/ssl-automotors.md`](docs/ssl-automotors.md) — arquitetura SSL do projeto (decorators, settings, fluxo HTTP↔HTTPS)
- [`docs/atendimento-enunciado.md`](docs/atendimento-enunciado.md) — mapeamento ponto-a-ponto do enunciado para o código
- [`docs/passos-finais.md`](docs/passos-finais.md) — instalação da CA no Keychain do macOS
