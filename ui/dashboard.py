"""StockPro – Dashboard"""
import tkinter as tk
from ui.tema import C, Card, CardStat, Tabela, Btn
import db.database as db


class Dashboard(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg"]); hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="Dashboard", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        Btn(hdr, "Atualizar", cmd=self.refresh, estilo="ghost", icone="↻").pack(side="right")

        # Cards
        g = tk.Frame(self, bg=C["bg"]); g.pack(fill="x", pady=(0, 6))
        for i in range(4): g.columnconfigure(i, weight=1)
        self._c_total = CardStat(g, "Total Produtos", cor=C["accent"],   sub="produtos ativos")
        self._c_ok    = CardStat(g, "Stock Normal",   cor=C["green"],    sub="acima do mínimo")
        self._c_baixo = CardStat(g, "Stock Baixo",    cor=C["yellow"],   sub="abaixo do mínimo")
        self._c_zero  = CardStat(g, "Esgotados",      cor=C["red"],      sub="sem stock")
        self._c_total.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self._c_ok.grid(   row=0, column=1, padx=3,      sticky="ew")
        self._c_baixo.grid(row=0, column=2, padx=3,      sticky="ew")
        self._c_zero.grid( row=0, column=3, padx=(6, 0), sticky="ew")

        # Tabelas
        bottom = tk.Frame(self, bg=C["bg"]); bottom.pack(fill="both", expand=True)
        bottom.columnconfigure(0, weight=3); bottom.columnconfigure(1, weight=2)

        left = Card(bottom); left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        lh = tk.Frame(left, bg=C["bg2"]); lh.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(lh, text="⚠  Alertas de Stock Baixo", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self._badge_alerta = tk.Label(lh, text="0", bg=C["yellow_bg"], fg=C["yellow"],
                                      font=("Segoe UI", 9, "bold"), padx=8, pady=3)
        self._badge_alerta.pack(side="right")
        self._tbl_alertas = Tabela(left, altura=8, colunas=[
            {"id": "nome",   "label": "Produto",     "w": 200, "s": True},
            {"id": "atual",  "label": "Stock Atual", "w": 90,  "anc": "center"},
            {"id": "min",    "label": "Mínimo",      "w": 80,  "anc": "center"},
            {"id": "estado", "label": "Estado",      "w": 90,  "anc": "center"},
        ])
        self._tbl_alertas.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        right = Card(bottom); right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Últimos Movimentos", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
        self._tbl_mov = Tabela(right, altura=8, colunas=[
            {"id": "prod", "label": "Produto", "w": 160, "s": True},
            {"id": "tipo", "label": "Tipo",    "w": 75,  "anc": "center"},
            {"id": "qtd",  "label": "Qtd",     "w": 55,  "anc": "center"},
            {"id": "data", "label": "Data",    "w": 85,  "anc": "center"},
        ])
        self._tbl_mov.pack(fill="both", expand=True, padx=8, pady=(0, 6))

    def refresh(self, _=None):
        s = db.prod_stats()
        self._c_total.atualizar(s["total"])
        self._c_ok.atualizar(s["ok"])
        self._c_baixo.atualizar(s["baixo"])
        self._c_zero.atualizar(s["zero"])

        alertas = db.prod_listar(so_baixo=True)
        self._badge_alerta.config(text=f"  {len(alertas)}  ")
        self._tbl_alertas.limpar()
        for p in alertas:
            tag    = "zero" if p["stock_atual"] == 0 else "baixo"
            estado = "Esgotado" if p["stock_atual"] == 0 else "Baixo"
            self._tbl_alertas.linha((p["nome"],
                f"{p['stock_atual']} {p['unidade']}",
                f"{p['stock_minimo']} {p['unidade']}", estado), tag)
        self.app.set_badge(len(alertas))

        movs = db.mov_listar(limit=10)
        self._tbl_mov.limpar()
        for m in movs:
            tag  = "entrada" if m["tipo"] == "entrada" else "saida"
            tipo = "⬇ Entrada" if m["tipo"] == "entrada" else "⬆ Saída"
            sinal = ""
            self._tbl_mov.linha((m["prod_nome"], tipo,
                f"{m['quantidade']}", str(m["data_movimento"])), tag)
