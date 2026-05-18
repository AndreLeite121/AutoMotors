# Como rodar o AutoMotors — passo a passo

Guia completo para colocar o projeto rodando do zero, partindo apenas do
GitHub. Inclui instruções separadas para **Linux** e **Windows**.

> Tempo estimado: 10 a 15 minutos.

---

## Pré-requisitos

Antes de começar, garanta que você tem instalado:

| Ferramenta | Como verificar | Onde baixar |
|---|---|---|
| **Python 3.10+** | `python3 --version` (Linux) ou `python --version` (Windows) | [python.org/downloads](https://www.python.org/downloads/) |
| **Git** | `git --version` | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **OpenSSL** | `openssl version` | Linux: já vem; Windows: vem junto com o Git for Windows |

> **Windows:** ao instalar o Python, **marque a caixa "Add Python to PATH"**
> na primeira tela do instalador. Sem isso o comando `python` não funciona
> no terminal.

---

## 1. Clonar o repositório

Abra um terminal (Linux: Terminal; Windows: PowerShell ou Git Bash) e rode:

```bash
git clone https://github.com/AndreLeite121/AutoMotors.git
cd AutoMotors
```

> O nome da pasta clonada vai depender de como o repositório foi nomeado no
> GitHub. Se cair em `TPIII-SASI` ou outro nome, ajuste o `cd`.

---

## 2. Criar e ativar o ambiente virtual

O ambiente virtual (venv) isola as dependências do projeto. **Sempre ative
o venv antes de rodar qualquer comando `pip` ou `python manage.py`.**

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> Se o PowerShell reclamar com "execução de scripts foi desabilitada",
> rode uma única vez (como administrador):
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Verificação:** depois de ativar, o prompt do terminal deve aparecer com
`(venv)` no início. Se não aparecer, o venv não está ativo.

---

## 3. Instalar as dependências

```bash
pip install --upgrade pip
pip install -r requeriments.txt
```

> O nome do arquivo é `requeriments.txt` mesmo (com a grafia original do
> projeto), não `requirements.txt`.

Pacotes que serão instalados:

- `Django 5.2.1` — framework web
- `django-sslserver 0.22` — servidor HTTPS de desenvolvimento
- `Pillow 11.2.1` — manipulação de imagens
- `gunicorn 23.0.0` — servidor de produção (opcional)

---

## 4. Aplicar as migrations (criar o banco)

O arquivo `db.sqlite3` **não** vem no repositório (está no `.gitignore`).
Você precisa criar do zero:

```bash
python manage.py migrate
```

> Em Linux, dependendo da instalação, use `python3` em vez de `python`.

Saída esperada: várias linhas terminando em `OK`.

---

## 5. Criar um usuário administrador

Para acessar o painel `/admin/`:

```bash
python manage.py createsuperuser
```

O Django vai pedir, nessa ordem:

- **Username:** (exemplo) `admin`
- **Email:** (exemplo) `admin@automotors.local`
- **Password:** uma senha qualquer (ele avisa se for fraca, pode confirmar mesmo assim em dev)

---

## 6. Popular o banco com dados de exemplo (opcional, mas recomendado)

Sem isso o catálogo vai aparecer vazio.

**6.1 — Criar veículos e acessórios** (com 1 foto de capa cada, baixada do Unsplash):

```bash
python manage.py seed_garagem
```

Esse comando cria 9 veículos seminovos (Civic, Corolla, HB20, Golf GTI,
Compass, Hilux, BMW 320i, Kwid, Fiat Toro) e 3 acessórios (tapete,
higienização, película). Precisa de internet pra baixar as fotos de capa.

**6.2 — Importar a galeria de fotos múltiplas** (recomendado):

A pasta `Carros/` já vem no repositório com várias fotos por modelo
(2 a 5 fotos cada). Pra carregá-las na galeria de cada veículo:

```bash
python manage.py import_fotos
```

Sem internet, sem argumentos — ele pega de `Carros/` na raiz do projeto.
Sem esse passo, cada carro só vai ter a foto única baixada do Unsplash no
6.1.

---

## 7. Os certificados SSL

Os certificados já **vêm versionados** dentro de `certs/`:

- `ca.crt` / `ca.key` — Autoridade Certificadora AutoMotors
- `server.crt` / `server.key` — certificado do servidor para `localhost`
- `gerar-certificados.sh` — script para regenerar (opcional)

Você **não precisa regenerar** — só rode o servidor que ele já encontra
tudo. Se ainda assim quiser regenerar (Linux/macOS):

```bash
cd certs/
bash gerar-certificados.sh
cd ..
```

> No Windows isso só funciona dentro do **Git Bash** (não no CMD nem no
> PowerShell), porque o script usa sintaxe bash.

### 7.1 — (Opcional) Fazer o navegador confiar no certificado

Sem esse passo, o navegador vai mostrar um aviso de "conexão não privada"
ao acessar `https://localhost:8443` — é só clicar em "Avançado → Prosseguir"
toda vez. Para evitar o aviso:

**Linux (Chrome/Edge):**
1. Abra o Chrome → **Configurações → Privacidade e segurança → Segurança → Gerenciar certificados**
2. Aba **Autoridades** → **Importar**
3. Selecione `certs/ca.crt`
4. Marque "Confiar neste certificado para identificar sites"

**Linux (Firefox):**
1. Firefox → **Configurações → Privacidade e Segurança** → role até o fim → **Certificados → Ver Certificados**
2. Aba **Autoridades** → **Importar**
3. Selecione `certs/ca.crt`
4. Marque "Confiar nesta CA para identificar sites"

**Windows:**
1. Clique duplo em `certs/ca.crt` no Explorer
2. **Instalar Certificado** → **Computador Local** → **Avançar**
3. Selecione **Colocar todos os certificados no repositório a seguir** → **Procurar** → **Autoridades de Certificação Raiz Confiáveis**
4. **Avançar → Concluir → Sim**

> Reinicie o navegador depois de importar.

---

## 8. Iniciar os servidores

O AutoMotors roda **dois servidores em paralelo**: um HTTP (porta 8000) e
um HTTPS (porta 8443).

### Linux / macOS — script único

```bash
bash iniciar-automotors.sh
```

Esse script sobe os dois servidores ao mesmo tempo. Para encerrar, `Ctrl+C`
no terminal.

### Windows — dois terminais

Abra **dois PowerShell** (ou dois CMD). Em cada um, ative o venv primeiro
(`venv\Scripts\Activate.ps1`), depois rode:

**Terminal 1 (HTTP):**
```powershell
python manage.py runserver 127.0.0.1:8000
```

**Terminal 2 (HTTPS):**
```powershell
python manage.py runsslserver --certificate certs/server.crt --key certs/server.key 127.0.0.1:8443
```

> No Windows, dá pra usar `localhost` no lugar de `127.0.0.1` se preferir.

---

## 9. Acessar no navegador

| URL | O que tem |
|---|---|
| http://localhost:8000/ | Home pública (apresentação da empresa + política) |
| http://localhost:8000/garagem/ | Catálogo de veículos |
| http://localhost:8000/acessorios/ | Acessórios automotivos |
| https://localhost:8443/accounts/login/ | Login (HTTPS obrigatório) 🔒 |
| https://localhost:8443/signup/ | Cadastro 🔒 |
| https://localhost:8443/admin/ | Painel admin (use o superusuário do passo 5) 🔒 |

Quando você clicar em "Entrar" no navbar de qualquer página HTTP, o sistema
redireciona para `https://localhost:8443/...` automaticamente — isso é o
**HTTPS seletivo** funcionando.

---

## Problemas comuns

### "ModuleNotFoundError: No module named 'django'"

O venv não está ativo, ou as dependências não foram instaladas. Volte para
o **passo 2** e confirme que o prompt mostra `(venv)`. Depois rode
`pip install -r requeriments.txt` de novo.

### "Port 8000 (ou 8443) is already in use"

Algum outro processo já está usando a porta. No Linux:

```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:8443 | xargs kill -9
```

No Windows (PowerShell):

```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

### "bash: iniciar-automotors.sh: Permission denied" (Linux)

```bash
chmod +x iniciar-automotors.sh
bash iniciar-automotors.sh
```

### Aviso "Sua conexão não é particular" no Chrome ao abrir HTTPS

Esperado se você pulou o passo 7.1. Clique em **Avançado → Continuar para
localhost (não seguro)** — é só desenvolvimento local. Para sumir de vez,
faça o passo 7.1.

### "CSRF verification failed" no logout

Se acontecer, é provável que você tenha aberto a página em uma aba antiga
antes de logar — feche e reabra o navegador. O logout do AutoMotors
intencionalmente fica fora do `ssl_required` (explicação no
[`docs/ssl-automotors.md`](ssl-automotors.md), seção 4).

### Catálogo aparece vazio

Você pulou o **passo 6**. Rode `python manage.py seed_garagem`.

### Erro de SSL/Python 3.12 ao iniciar o `runsslserver`

O projeto já tem um patch (`automotors/_ssl_compat.py`) para Python 3.12+.
Se mesmo assim falhar, confira que está usando o Python do venv
(`which python` no Linux ou `where python` no Windows deve apontar para a
pasta `venv/`).

---

## Checklist final

- [ ] `git clone` feito
- [ ] venv criado e ativado (prompt mostra `(venv)`)
- [ ] `pip install -r requeriments.txt` rodou sem erro
- [ ] `python manage.py migrate` rodou sem erro
- [ ] superusuário criado
- [ ] (opcional) `seed_garagem` rodou e baixou as fotos
- [ ] dois servidores rodando (8000 + 8443)
- [ ] http://localhost:8000/ abre a home
- [ ] clicar "Entrar" leva para https://localhost:8443/accounts/login/

Se tudo acima estiver ok, está pronto para usar.

---

## Para saber mais

- [`tutorial-openssl.md`](tutorial-openssl.md) — como os certificados foram gerados
- [`ssl-automotors.md`](ssl-automotors.md) — arquitetura SSL do projeto
- [`atendimento-enunciado.md`](atendimento-enunciado.md) — mapeamento das exigências do TPIII para o código
- [`passos-finais.md`](passos-finais.md) — instalação da CA no Keychain (macOS)
