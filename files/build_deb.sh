#!/bin/bash
# ============================================================
#  StockPro – Builder de pacote .deb
#  Uso: bash build_deb.sh [versao]
#  Exemplo: bash build_deb.sh 1.0.1
# ============================================================

set -e

# ── Configuração ─────────────────────────────────────────────
NOME="stockpro"
VERSAO="${1:-1.0.0}"
ARCH="all"
MAINTAINER="HCsoftware <hcsoftware@local>"
DESCRICAO="StockPro - Sistema de Gestão de Stocks"

# Diretório onde está o código fonte (pasta onde corre o script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR"     # Assume que o build.sh está na raiz do projeto

# Diretório de output do .deb
OUTPUT_DIR="$SCRIPT_DIR/dist"

# ── Verificações ──────────────────────────────────────────────
if ! command -v dpkg-deb &>/dev/null; then
    echo "ERRO: dpkg-deb não encontrado. Instala com: sudo apt install dpkg"
    exit 1
fi

if [ ! -f "$SOURCE_DIR/main.py" ]; then
    echo "ERRO: main.py não encontrado em $SOURCE_DIR"
    echo "Certifica-te que o build_deb.sh está na raiz do projeto StockPro"
    exit 1
fi

echo "============================================"
echo "  StockPro .deb Builder"
echo "  Versão: $VERSAO"
echo "  Fonte:  $SOURCE_DIR"
echo "============================================"

# ── Estrutura do pacote ───────────────────────────────────────
PKG_DIR="$(mktemp -d)/stockpro_${VERSAO}"
echo ""
echo "[1/4] A criar estrutura do pacote..."

mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/stockpro"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$PKG_DIR/etc/stockpro"

# ── Copiar código fonte ───────────────────────────────────────
echo "[2/4] A copiar ficheiros..."
cp -r "$SOURCE_DIR/." "$PKG_DIR/usr/share/stockpro/"

# Limpar ficheiros desnecessários
find "$PKG_DIR/usr/share/stockpro/" -name "*.pyc"        -delete
find "$PKG_DIR/usr/share/stockpro/" -name "__pycache__"  -exec rm -rf {} + 2>/dev/null || true
find "$PKG_DIR/usr/share/stockpro/" -name "config.json"  -delete 2>/dev/null || true
find "$PKG_DIR/usr/share/stockpro/" -name "build_deb.sh" -delete 2>/dev/null || true
find "$PKG_DIR/usr/share/stockpro/" -name "dist"         -exec rm -rf {} + 2>/dev/null || true

# ── Launcher ─────────────────────────────────────────────────
cat > "$PKG_DIR/usr/bin/stockpro" << 'EOF'
#!/bin/bash
exec python3 /usr/share/stockpro/main.py "$@"
EOF
chmod 755 "$PKG_DIR/usr/bin/stockpro"

# ── Ícone SVG ─────────────────────────────────────────────────
cat > "$PKG_DIR/usr/share/icons/hicolor/128x128/apps/stockpro.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <rect width="128" height="128" rx="16" fill="#0f1117"/>
  <rect x="16" y="48" width="96" height="64" rx="4" fill="#161b27" stroke="#2e3450" stroke-width="2"/>
  <polygon points="8,52 64,16 120,52" fill="#4f7ef7"/>
  <rect x="44" y="72" width="40" height="40" rx="3" fill="#1e2235" stroke="#4f7ef7" stroke-width="1.5"/>
  <rect x="54" y="80" width="8" height="8" rx="1" fill="#22c55e"/>
  <rect x="66" y="80" width="8" height="8" rx="1" fill="#ef4444"/>
  <rect x="54" y="92" width="20" height="3" rx="1" fill="#4f7ef7"/>
  <rect x="54" y="99" width="14" height="3" rx="1" fill="#4a5578"/>
</svg>
EOF

# ── .desktop ──────────────────────────────────────────────────
cat > "$PKG_DIR/usr/share/applications/stockpro.desktop" << EOF
[Desktop Entry]
Version=$VERSAO
Type=Application
Name=StockPro
GenericName=Gestão de Stocks
Comment=Sistema de gestão de stocks by HCsoftware
Exec=stockpro
Icon=stockpro
Terminal=false
Categories=Office;Finance;
Keywords=stock;gestão;armazém;inventário;
StartupNotify=true
EOF

# ── DEBIAN/control ────────────────────────────────────────────
INSTALLED_SIZE=$(du -sk "$PKG_DIR/usr/" | cut -f1)
cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: $NOME
Version: $VERSAO
Section: utils
Priority: optional
Architecture: $ARCH
Installed-Size: $INSTALLED_SIZE
Depends: python3 (>= 3.10), python3-tk, python3-pip, mysql-server | mariadb-server
Recommends: python3-mysqlconnector
Maintainer: $MAINTAINER
Description: $DESCRICAO
 Aplicação desktop para gestão de stocks com suporte a múltiplos
 utilizadores, entradas e saídas de produtos, histórico de movimentos,
 alertas de stock mínimo e backup de base de dados.
 .
 Requer MySQL/MariaDB (instalado automaticamente se não presente).
EOF

# ── DEBIAN/postinst ───────────────────────────────────────────
cat > "$PKG_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
echo "============================================"
echo "  StockPro – Configuração pós-instalação"
echo "============================================"

echo "[1/4] A instalar mysql-connector-python..."
pip3 install mysql-connector-python --break-system-packages -q 2>/dev/null || \
pip3 install mysql-connector-python -q 2>/dev/null || \
echo "  AVISO: instala manualmente: pip3 install mysql-connector-python"

echo "[2/4] A verificar MySQL/MariaDB..."
systemctl start mysql 2>/dev/null || systemctl start mariadb 2>/dev/null || \
service mysql start 2>/dev/null || service mariadb start 2>/dev/null || true

echo "[3/4] A preparar base de dados..."
MYSQL_CMD=""
command -v mysql   &>/dev/null && MYSQL_CMD="mysql"
command -v mariadb &>/dev/null && MYSQL_CMD="${MYSQL_CMD:-mariadb}"

if [ -n "$MYSQL_CMD" ]; then
    DB_PASS=$(python3 -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(16)))")
    $MYSQL_CMD -u root 2>/dev/null << SQLEOF || $MYSQL_CMD -u root --skip-password 2>/dev/null << SQLEOF || true
CREATE DATABASE IF NOT EXISTS stockpro DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'stockpro_app'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON stockpro.* TO 'stockpro_app'@'localhost';
FLUSH PRIVILEGES;
SQLEOF
    mkdir -p /etc/stockpro
    printf "DB_HOST=localhost\nDB_PORT=3306\nDB_NAME=stockpro\nDB_USER=stockpro_app\nDB_PASS=%s\n" "$DB_PASS" > /etc/stockpro/db_setup.conf
    chmod 640 /etc/stockpro/db_setup.conf
fi

echo "[4/4] A criar esquema..."
if [ -n "$MYSQL_CMD" ] && [ -f /etc/stockpro/db_setup.conf ]; then
    source /etc/stockpro/db_setup.conf
    $MYSQL_CMD -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" 2>/dev/null << 'SQLEOF' || true
SET FOREIGN_KEY_CHECKS=0;
CREATE TABLE IF NOT EXISTS categorias (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(100) NOT NULL UNIQUE, descricao TEXT, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS departamentos (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(100) NOT NULL UNIQUE, descricao TEXT, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS produtos (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(200) NOT NULL, codigo_barras VARCHAR(100) UNIQUE, categoria_id INT, descricao TEXT, unidade VARCHAR(20) DEFAULT 'un', stock_atual INT DEFAULT 0, stock_minimo INT DEFAULT 0, localizacao VARCHAR(100), ativo TINYINT(1) DEFAULT 1, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP, atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS movimentos (id INT AUTO_INCREMENT PRIMARY KEY, produto_id INT NOT NULL, tipo ENUM('entrada','saida') NOT NULL, quantidade INT NOT NULL, stock_antes INT NOT NULL, stock_depois INT NOT NULL, departamento_id INT, levantado_por VARCHAR(150), notas TEXT, data_movimento DATE, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE, FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE SET NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS app_utilizadores (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(80) NOT NULL UNIQUE, nome VARCHAR(150) NOT NULL, password_hash VARCHAR(256) NOT NULL, role ENUM('admin','operador') DEFAULT 'operador', ativo TINYINT(1) DEFAULT 1, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
SET FOREIGN_KEY_CHECKS=1;
SQLEOF
fi

echo ""
echo "✔ Instalação concluída! Inicia com: stockpro"
echo "============================================"
exit 0
EOF
chmod 755 "$PKG_DIR/DEBIAN/postinst"

# ── DEBIAN/prerm e postrm ─────────────────────────────────────
echo '#!/bin/bash
exit 0' > "$PKG_DIR/DEBIAN/prerm"
chmod 755 "$PKG_DIR/DEBIAN/prerm"

cat > "$PKG_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
if [ "$1" = "purge" ]; then
    rm -rf /etc/stockpro
    rm -f /usr/share/applications/stockpro.desktop
fi
exit 0
EOF
chmod 755 "$PKG_DIR/DEBIAN/postrm"

# ── Construir .deb ────────────────────────────────────────────
echo "[3/4] A construir pacote .deb..."
mkdir -p "$OUTPUT_DIR"
DEB_FILE="$OUTPUT_DIR/${NOME}_${VERSAO}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "$PKG_DIR" "$DEB_FILE"

# Limpeza
rm -rf "$(dirname $PKG_DIR)"

echo ""
echo "============================================"
echo "  ✔ Pacote criado com sucesso!"
echo "  Ficheiro: $DEB_FILE"
echo "  Tamanho:  $(du -sh "$DEB_FILE" | cut -f1)"
echo ""
echo "  Para instalar:"
echo "  sudo apt install $DEB_FILE"
echo "============================================"
