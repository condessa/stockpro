"""
StockPro – Camada de base de dados MySQL
"""
import mysql.connector
from mysql.connector import Error
from datetime import date

# Preenchido em runtime pelo app.py a partir do config.json
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "",
    "password": "",
    "database": "stockpro",
    "charset":  "utf8mb4",
}

_TABLES = [
    """CREATE TABLE IF NOT EXISTS app_utilizadores (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        username     VARCHAR(60)  NOT NULL UNIQUE,
        nome         VARCHAR(120) NOT NULL,
        pass_hash    VARCHAR(64)  NOT NULL,
        role         ENUM('admin','operador') NOT NULL DEFAULT 'operador',
        ativo        TINYINT(1) DEFAULT 1,
        criado_em    DATETIME DEFAULT CURRENT_TIMESTAMP,
        ultimo_login DATETIME
    ) ENGINE=InnoDB""",

    """CREATE TABLE IF NOT EXISTS categorias (
        id        INT AUTO_INCREMENT PRIMARY KEY,
        nome      VARCHAR(100) NOT NULL UNIQUE,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB""",

    """CREATE TABLE IF NOT EXISTS departamentos (
        id        INT AUTO_INCREMENT PRIMARY KEY,
        nome      VARCHAR(100) NOT NULL UNIQUE,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB""",

    """CREATE TABLE IF NOT EXISTS produtos (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        codigo_barras VARCHAR(100) NOT NULL UNIQUE,
        nome          VARCHAR(200) NOT NULL,
        descricao     TEXT,
        categoria_id  INT,
        stock_atual   INT  NOT NULL DEFAULT 0,
        stock_minimo  INT  NOT NULL DEFAULT 5,
        unidade       VARCHAR(20)  DEFAULT 'un',
        localizacao   VARCHAR(100),
        ativo         TINYINT(1)   DEFAULT 1,
        criado_em     DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
    ) ENGINE=InnoDB""",

    """CREATE TABLE IF NOT EXISTS movimentos (
        id              INT AUTO_INCREMENT PRIMARY KEY,
        produto_id      INT  NOT NULL,
        tipo            ENUM('entrada','saida') NOT NULL,
        quantidade      INT  NOT NULL,
        stock_antes     INT  NOT NULL,
        stock_depois    INT  NOT NULL,
        departamento_id INT,
        levantado_por   VARCHAR(150),
        notas           TEXT,
        data_movimento  DATE NOT NULL,
        criado_em       DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (produto_id)      REFERENCES produtos(id)      ON DELETE CASCADE,
        FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE SET NULL
    ) ENGINE=InnoDB""",
]


# ─────────────────────────────────────────────────────────────────────────────
class Database:
    def __init__(self):
        self.conn   = None
        self.cursor = None

    def connect(self):
        try:
            # Criar BD se não existir
            tmp = mysql.connector.connect(
                host=DB_CONFIG["host"], port=int(DB_CONFIG["port"]),
                user=DB_CONFIG["user"], password=DB_CONFIG["password"],
                charset="utf8mb4",
            )
            cur = tmp.cursor()
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            tmp.commit(); cur.close(); tmp.close()

            self.conn   = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            for sql in _TABLES:
                self.cursor.execute(sql)
            self.conn.commit()
            return True, "OK"
        except Error as e:
            return False, str(e)

    def disconnect(self):
        try:
            if self.cursor: self.cursor.close()
            if self.conn and self.conn.is_connected(): self.conn.close()
        except Exception:
            pass

    def run(self, sql, params=()):
        if not self.cursor:
            raise RuntimeError("Base de dados não ligada")
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.lastrowid

    def one(self, sql, params=()):
        if not self.cursor:
            return None
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def all(self, sql, params=()):
        if not self.cursor:
            return []
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()


_db = Database()
def get_db(): return _db


# ── Utilizadores ──────────────────────────────────────────────────────────────
import hashlib

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def util_existe_algum():
    r = _db.one("SELECT COUNT(*) AS n FROM app_utilizadores")
    return (r["n"] if r else 0) > 0

def util_autenticar(username: str, password: str):
    u = _db.one(
        "SELECT * FROM app_utilizadores WHERE username=%s AND ativo=1",
        (username.strip().lower(),)
    )
    if u and u["pass_hash"] == _hash(password):
        _db.run("UPDATE app_utilizadores SET ultimo_login=NOW() WHERE id=%s", (u["id"],))
        return u
    return None

def util_listar():
    return _db.all(
        "SELECT id,username,nome,role,ativo,criado_em,ultimo_login "
        "FROM app_utilizadores ORDER BY nome"
    )

def util_criar(username: str, nome: str, password: str, role="operador"):
    return _db.run(
        "INSERT INTO app_utilizadores (username,nome,pass_hash,role) VALUES (%s,%s,%s,%s)",
        (username.strip().lower(), nome.strip(), _hash(password), role)
    )

def util_atualizar(uid: int, nome: str, role: str, ativo: int):
    _db.run(
        "UPDATE app_utilizadores SET nome=%s, role=%s, ativo=%s WHERE id=%s",
        (nome.strip(), role, int(ativo), uid)
    )

def util_alterar_password(uid: int, nova: str):
    _db.run(
        "UPDATE app_utilizadores SET pass_hash=%s WHERE id=%s",
        (_hash(nova), uid)
    )

def util_desativar(uid: int):
    _db.run("UPDATE app_utilizadores SET ativo=0 WHERE id=%s", (uid,))

def util_contar_admins():
    r = _db.one(
        "SELECT COUNT(*) AS n FROM app_utilizadores WHERE role='admin' AND ativo=1"
    )
    return r["n"] if r else 0


# ── Categorias ────────────────────────────────────────────────────────────────
def cat_listar():
    return _db.all("SELECT * FROM categorias ORDER BY nome")

def cat_criar(nome: str):
    return _db.run("INSERT INTO categorias (nome) VALUES (%s)", (nome.strip(),))

def cat_apagar(cid: int):
    _db.run("DELETE FROM categorias WHERE id=%s", (cid,))


# ── Departamentos ─────────────────────────────────────────────────────────────
def dep_listar():
    return _db.all("SELECT * FROM departamentos ORDER BY nome")

def dep_criar(nome: str):
    return _db.run("INSERT INTO departamentos (nome) VALUES (%s)", (nome.strip(),))

def dep_apagar(did: int):
    _db.run("DELETE FROM departamentos WHERE id=%s", (did,))


# ── Produtos ──────────────────────────────────────────────────────────────────
def prod_listar(pesquisa="", so_baixo=False):
    sql = """SELECT p.*, c.nome AS cat_nome
             FROM produtos p
             LEFT JOIN categorias c ON p.categoria_id = c.id
             WHERE p.ativo = 1"""
    params = []
    if pesquisa:
        sql += " AND (p.nome LIKE %s OR p.codigo_barras LIKE %s)"
        params += [f"%{pesquisa}%", f"%{pesquisa}%"]
    if so_baixo:
        sql += " AND p.stock_atual < p.stock_minimo"
    sql += " ORDER BY p.nome"
    return _db.all(sql, params)

def prod_por_codigo(codigo: str):
    return _db.one(
        "SELECT p.*, c.nome AS cat_nome FROM produtos p "
        "LEFT JOIN categorias c ON p.categoria_id=c.id "
        "WHERE p.codigo_barras=%s AND p.ativo=1", (codigo,)
    )

def prod_por_id(pid: int):
    return _db.one(
        "SELECT p.*, c.nome AS cat_nome FROM produtos p "
        "LEFT JOIN categorias c ON p.categoria_id=c.id "
        "WHERE p.id=%s", (pid,)
    )

def prod_criar(codigo, nome, descricao, cat_id, stock_ini, stock_min, unidade, local):
    pid = _db.run(
        "INSERT INTO produtos "
        "(codigo_barras,nome,descricao,categoria_id,stock_atual,stock_minimo,unidade,localizacao) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (codigo, nome, descricao or None, cat_id or None,
         stock_ini, stock_min, unidade, local or None)
    )
    if stock_ini > 0:
        _mov_registar(pid, "entrada", stock_ini, 0, None, None, "Stock inicial")
    return pid

def prod_atualizar(pid, nome, descricao, cat_id, stock_min, unidade, local):
    _db.run(
        "UPDATE produtos SET nome=%s,descricao=%s,categoria_id=%s,"
        "stock_minimo=%s,unidade=%s,localizacao=%s WHERE id=%s",
        (nome, descricao or None, cat_id or None, stock_min, unidade, local or None, pid)
    )

def prod_apagar(pid: int):
    """Desativa o produto (soft delete — mantém histórico)."""
    _db.run("UPDATE produtos SET ativo=0 WHERE id=%s", (pid,))

def prod_eliminar(pid: int):
    """Eliminação permanente — apaga produto e todos os movimentos associados."""
    _db.run("DELETE FROM produtos WHERE id=%s", (pid,))

def prod_stats():
    r = _db.one("""
        SELECT COUNT(*) AS total,
               SUM(stock_atual > 0 AND stock_atual < stock_minimo) AS baixo,
               SUM(stock_atual = 0)                                AS zero,
               SUM(stock_atual >= stock_minimo)                    AS ok
        FROM produtos WHERE ativo=1
    """)
    if not r:
        return {"total": 0, "baixo": 0, "zero": 0, "ok": 0}
    return {k: int(v or 0) for k, v in r.items()}

def prod_contar_alertas():
    r = _db.one(
        "SELECT COUNT(*) AS n FROM produtos WHERE ativo=1 AND stock_atual < stock_minimo"
    )
    return r["n"] if r else 0


# ── Movimentos ────────────────────────────────────────────────────────────────
def _mov_registar(prod_id, tipo, qtd, stock_antes,
                  dep_id, levantado_por, notas, data=None):
    stock_depois = stock_antes + qtd if tipo == "entrada" else stock_antes - qtd
    _db.run("UPDATE produtos SET stock_atual=%s WHERE id=%s", (stock_depois, prod_id))
    _db.run(
        "INSERT INTO movimentos "
        "(produto_id,tipo,quantidade,stock_antes,stock_depois,"
        "departamento_id,levantado_por,notas,data_movimento) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (prod_id, tipo, qtd, stock_antes, stock_depois,
         dep_id or None, levantado_por or None,
         notas or None, data or str(date.today()))
    )
    return stock_depois

def mov_entrada(prod_id: int, qtd: int, notas="", data=None):
    p = prod_por_id(prod_id)
    if not p:
        raise ValueError("Produto não encontrado")
    return _mov_registar(prod_id, "entrada", qtd, p["stock_atual"],
                         None, None, notas, data)

def mov_saida(prod_id: int, qtd: int, dep_id, levantado_por: str, data=None):
    p = prod_por_id(prod_id)
    if not p:
        raise ValueError("Produto não encontrado")
    if p["stock_atual"] < qtd:
        raise ValueError(f"Stock insuficiente. Disponível: {p['stock_atual']} {p['unidade']}")
    return _mov_registar(prod_id, "saida", qtd, p["stock_atual"],
                         dep_id, levantado_por, None, data)

def mov_listar(tipo="", pesquisa="", prod_id=None, limit=500, funcionario=""):
    sql = """
        SELECT m.*, p.nome AS prod_nome, p.codigo_barras, p.unidade,
               d.nome AS dep_nome
        FROM movimentos m
        JOIN  produtos     p ON m.produto_id      = p.id
        LEFT JOIN departamentos d ON m.departamento_id = d.id
        WHERE 1=1
    """
    params = []
    if tipo:
        sql += " AND m.tipo=%s";         params.append(tipo)
    if prod_id:
        sql += " AND m.produto_id=%s";   params.append(prod_id)
    if pesquisa:
        sql += (" AND (p.nome LIKE %s OR p.codigo_barras LIKE %s "
                "OR m.levantado_por LIKE %s)")
        params += [f"%{pesquisa}%"] * 3
    if funcionario:
        sql += " AND m.levantado_por LIKE %s"
        params.append(f"%{funcionario}%")
    sql += f" ORDER BY m.criado_em DESC LIMIT {int(limit)}"
    return _db.all(sql, params)


def mov_listar_funcionarios():
    """Devolve lista de nomes únicos de colaboradores com movimentos registados."""
    rows = _db.all(
        "SELECT DISTINCT levantado_por FROM movimentos "
        "WHERE levantado_por IS NOT NULL AND levantado_por != '' "
        "ORDER BY levantado_por"
    )
    return [r["levantado_por"] for r in rows]
