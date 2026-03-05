"""
StockPro – Configuração local (config.json)
Guarda as credenciais MySQL em ~/.config/stockpro/config.json
"""
import json, os

# Pasta de configuração no home do utilizador (com permissões de escrita)
_CONFIG_DIR  = os.path.join(os.path.expanduser("~"), ".config", "stockpro")
CONFIG_FILE  = os.path.join(_CONFIG_DIR, "config.json")

DEFAULTS = {
    "host":     "localhost",
    "port":     3306,
    "user":     "",
    "password": "",
    "database": "stockpro",
}

def _garantir_dir():
    os.makedirs(_CONFIG_DIR, mode=0o700, exist_ok=True)

def carregar():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            cfg = DEFAULTS.copy()
            cfg.update(d)
            return cfg
        except Exception:
            pass
    return DEFAULTS.copy()

def guardar(cfg: dict):
    _garantir_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.chmod(CONFIG_FILE, 0o600)  # só o dono pode ler

def existe():
    return os.path.exists(CONFIG_FILE)

def valida(cfg: dict):
    return bool(cfg.get("host") and cfg.get("user"))
