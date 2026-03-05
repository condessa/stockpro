# StockPro – Gestão de Stocks

**Versão:** 1.0.0  
**Desenvolvido por:** HCsoftware  
**Plataforma:** Linux (Debian/Ubuntu)

---

## Descrição

StockPro é uma aplicação desktop para gestão de stocks, desenvolvida em Python com interface gráfica tkinter e base de dados MySQL/MariaDB.

Funcionalidades principais:
- Gestão de produtos com categorias, códigos de barras e stock mínimo
- Registo de entradas e saídas com rastreio por colaborador e departamento
- Histórico completo de movimentos com filtros por produto e funcionário
- Alertas automáticos de stock baixo
- Sistema de utilizadores com perfis Admin e Operador
- Bloqueio automático por inatividade (1 minuto)
- Backup da base de dados em CSV
- Verificação automática de atualizações

---

## Requisitos

| Componente | Versão mínima |
|---|---|
| Python | 3.10+ |
| python3-tk | qualquer |
| mysql-connector-python | qualquer |
| MySQL ou MariaDB | 5.7+ / 10.3+ |

---

## Instalação (pacote .deb)

```bash
sudo apt install ./stockpro_1.0.0_amd64.deb
```

O instalador trata automaticamente de:
1. Instalar `mysql-connector-python` via pip
2. Iniciar o serviço MySQL/MariaDB
3. Criar a base de dados `stockpro` com utilizador dedicado
4. Criar todas as tabelas necessárias

Na primeira execução é pedida a configuração da ligação à base de dados. As credenciais ficam guardadas em `~/.config/stockpro/config.json`.

---

## Instalação manual (sem .deb)

```bash
# 1. Instalar dependências
sudo apt install python3 python3-tk mysql-server
pip3 install mysql-connector-python --break-system-packages

# 2. Criar base de dados
sudo mysql << 'SQL'
CREATE DATABASE stockpro DEFAULT CHARACTER SET utf8mb4;
CREATE USER 'stockpro_app'@'localhost' IDENTIFIED BY 'password_aqui';
GRANT ALL PRIVILEGES ON stockpro.* TO 'stockpro_app'@'localhost';
FLUSH PRIVILEGES;
SQL

# 3. Correr o programa
cd /caminho/para/stockpro
python3 main.py
```

---

## Estrutura do projeto

```
stockpro/
├── main.py              # Ponto de entrada
├── app.py               # Janela principal, sidebar, navegação
├── config.py            # Configuração MySQL (~/.config/stockpro/)
├── version.py           # Versão da aplicação
├── db/
│   └── database.py      # Todas as operações na base de dados
└── ui/
    ├── tema.py           # Cores, widgets reutilizáveis, tooltips
    ├── login.py          # Ecrã de login / registo
    ├── setup.py          # Assistente de configuração inicial
    ├── bloqueio.py       # Ecrã de bloqueio por inatividade
    ├── dashboard.py      # Página inicial com estatísticas
    ├── produtos.py       # Gestão de produtos
    ├── entradas.py       # Registo de entradas de stock
    ├── saidas.py         # Registo de saídas de stock
    ├── historico.py      # Histórico de movimentos e alertas
    ├── utilizadores.py   # Gestão de utilizadores (só admin)
    └── definicoes.py     # Categorias, departamentos e sobre
```

---

## Gerar novo pacote .deb

Após fazer alterações ao código:

```bash
# Na raiz do projeto
bash build_deb.sh 1.0.1
```

O pacote é gerado em `dist/stockpro_1.0.1_all.deb`.

Para instalar a nova versão:
```bash
sudo apt install ./dist/stockpro_1.0.1_all.deb
```

---

## Atualizar manualmente (sem .deb)

Substitui os ficheiros `.py` na pasta de instalação:

```bash
sudo cp -r ui/ db/ *.py /usr/share/stockpro/
```

---

## Primeiro acesso

1. Abre o programa: `stockpro` (ou pelo menu de aplicações)
2. Configura a ligação à base de dados
3. Cria o primeiro utilizador **Administrador**
4. O programa entra automaticamente após o registo

---

## Utilizadores e perfis

| Perfil | Permissões |
|---|---|
| **Admin** | Acesso total, incluindo gestão de utilizadores e definições |
| **Operador** | Produtos, entradas, saídas e histórico |

---

## Segurança

- Passwords guardadas com hash SHA-256
- Bloqueio automático após **1 minuto** de inatividade
- Configuração da base de dados guardada em `~/.config/stockpro/config.json` (permissões 600)
- Proteção contra eliminação do último administrador

---

## Resolução de problemas

**Programa não abre após instalação**
```bash
# Verificar se MySQL está ativo
sudo systemctl status mysql
# Verificar configuração
cat ~/.config/stockpro/config.json
```

**Erro "Access denied" no MySQL**
```bash
# No Debian/Ubuntu usar sudo em vez de -u root -p
sudo mysql stockpro
```

**Reinstalar do zero (apagar todos os dados)**
```bash
sudo mysql -e "DROP DATABASE stockpro;"
rm ~/.config/stockpro/config.json
sudo apt install ./stockpro_1.0.0_amd64.deb
```

---

## Licença

Uso privado — HCsoftware © 2026
