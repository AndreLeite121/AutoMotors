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
| **Autenticação** | Cadastro, login, logout e troca de senha — todos em HTTPS |
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
cd automotors
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

**5. (Opcional) Popule o banco com dados de exemplo:**
```bash
python3 manage.py seed_garagem
```

**6. Gere os certificados SSL** (necessário para HTTPS):
```bash
cd certs/
bash gerar-certificados.sh   # macOS / Linux
cd ..
```
> Veja o passo a passo completo em [`docs/tutorial-openssl.md`](docs/tutorial-openssl.md).

**7. Inicie os dois servidores em paralelo:**

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

- [`docs/tutorial-openssl.md`](docs/tutorial-openssl.md) — geração e instalação dos certificados digitais
