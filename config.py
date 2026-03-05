"""
StockPro – Configuração local (config.json)
Guarda apenas as credenciais MySQL.
"""
import json, os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULTS = {
    "host":     "localhost",
    "port":     3306,
    "user":     "",
    "password": "",
    "database": "stockpro",
}

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
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def existe():
    return os.path.exists(CONFIG_FILE)

def valida(cfg: dict):
    return bool(cfg.get("host") and cfg.get("user"))
