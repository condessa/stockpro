"""StockPro – Histórico e Alertas"""
import tkinter as tk
from ui.tema import C, Card, Btn, FormLabel, Combo, Tabela, BarraPesquisa, toast
import db.database as db


class Historico(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._mapa_prod = {"Todos": None}
        self._build()

    def _build(self):
        tk.Label(self, text="Histórico de Movimentos", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 6))

        # Linha 1 — filtros principais
        flt1 = tk.Frame(self, bg=C["bg"]); flt1.pack(fill="x", pady=(0, 6))
        FormLabel(flt1, "Tipo:", bg=C["bg"]).pack(side="left", padx=(0, 4))
        self._f_tipo = Combo(flt1, valores=["Todos","Entradas","Saídas"], width=10)
        self._f_tipo.set("Todos"); self._f_tipo.pack(side="left", padx=(0, 14))
        self._f_tipo.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        FormLabel(flt1, "Produto:", bg=C["bg"]).pack(side="left", padx=(0, 4))
        self._f_prod = Combo(flt1, valores=["Todos"], width=26)
        self._f_prod.set("Todos"); self._f_prod.pack(side="left", padx=(0, 14))
        self._f_prod.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        self._pesq = BarraPesquisa(flt1, ao_mudar=lambda _: self.refresh())
        self._pesq.pack(side="left", fill="x", expand=True, padx=(0, 10))
        Btn(flt1, "Exportar CSV", cmd=self._exportar, estilo="ghost", icone="↓").pack(side="right")

        # Linha 2 — pesquisa por funcionário
        flt2 = tk.Frame(self, bg=C["bg"]); flt2.pack(fill="x", pady=(0, 6))
        tk.Label(flt2, text="👤", bg=C["bg"], fg=C["text2"],
                 font=("Segoe UI", 12)).pack(side="left", padx=(0, 4))
        FormLabel(flt2, "Funcionário:", bg=C["bg"]).pack(side="left", padx=(0, 4))
        self._f_func = Combo(flt2, valores=["Todos"], width=28)
        self._f_func.set("Todos"); self._f_func.pack(side="left", padx=(0, 8))
        self._f_func.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        # Pesquisa manual (para nomes não listados ainda)
        self._pesq_func = BarraPesquisa(flt2, ph="🔍  Nome do funcionário…",
                                        ao_mudar=self._ao_pesq_func)
        self._pesq_func.pack(side="left", padx=(0, 10))
        Btn(flt2, "Limpar filtros", cmd=self._limpar_filtros,
            estilo="ghost", icone="✕").pack(side="right")

        card = Card(self); card.pack(fill="both", expand=True)
        self._tbl = Tabela(card, altura=22, colunas=[
            {"id": "dt",     "label": "Data/Hora",     "w": 140},
            {"id": "tipo",   "label": "Tipo",          "w": 80,  "anc": "center"},
            {"id": "prod",   "label": "Produto",       "w": 190, "s": True},
            {"id": "cod",    "label": "Código",        "w": 120},
            {"id": "qtd",    "label": "Qtd",           "w": 65,  "anc": "center"},
            {"id": "antes",  "label": "Antes",         "w": 70,  "anc": "center"},
            {"id": "depois", "label": "Depois",        "w": 70,  "anc": "center"},
            {"id": "dep",    "label": "Departamento",  "w": 120},
            {"id": "pessoa", "label": "Colaborador",   "w": 130},
            {"id": "notas",  "label": "Notas",         "w": 130},
        ])
        self._tbl.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self._lbl_n = tk.Label(card, text="", bg=C["bg2"], fg=C["text3"], font=("Segoe UI", 9))
        self._lbl_n.pack(anchor="e", padx=14, pady=(0, 8))

    def _ao_pesq_func(self, _=None):
        """Quando o utilizador escreve manualmente, limpa o combo."""
        if self._pesq_func.val():
            self._f_func.set("Todos")
        self.refresh()

    def _limpar_filtros(self):
        self._f_tipo.set("Todos")
        self._f_prod.set("Todos")
        self._f_func.set("Todos")
        self._pesq.set("")
        self._pesq_func.set("")
        self.refresh()

    def _exportar(self):
        import csv
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV","*.csv")], initialfile="historico.csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Data","Tipo","Produto","Código","Qtd","Antes","Depois","Dep.","Colaborador","Notas"])
            for m in db.mov_listar(limit=10000):
                w.writerow([str(m["criado_em"]),m["tipo"],m["prod_nome"],m["codigo_barras"],
                            m["quantidade"],m["stock_antes"],m["stock_depois"],
                            m.get("dep_nome",""),m.get("levantado_por",""),m.get("notas","")])
        toast(self, "CSV exportado!")

    def refresh(self, _=None):
        # Atualizar lista de produtos
        prods = db.prod_listar()
        self._mapa_prod = {"Todos": None}
        for p in prods: self._mapa_prod[p["nome"]] = p["id"]
        self._f_prod["values"] = list(self._mapa_prod.keys())

        # Atualizar lista de funcionários a partir dos movimentos existentes
        funcs = db.mov_listar_funcionarios()
        self._f_func["values"] = ["Todos"] + funcs

        tipo_map = {"Entradas": "entrada", "Saídas": "saida"}
        tipo  = tipo_map.get(self._f_tipo.get(), "")
        pid   = self._mapa_prod.get(self._f_prod.get())

        # Funcionário: combo tem prioridade, depois pesquisa manual
        func_combo = self._f_func.get()
        func_pesq  = self._pesq_func.val().strip()
        funcionario = func_combo if func_combo and func_combo != "Todos" else func_pesq

        movs = db.mov_listar(tipo, self._pesq.val(), pid, funcionario=funcionario)
        self._tbl.limpar()
        for m in movs:
            if m["tipo"] == "entrada": tag, txt, s = "entrada", "⬇ Entrada", "+"
            else:                      tag, txt, s = "saida",   "⬆ Saída",   "-"
            self._tbl.linha((str(m["criado_em"]), txt, m["prod_nome"], m["codigo_barras"],
                f"{s}{m['quantidade']} {m['unidade']}", m["stock_antes"], m["stock_depois"],
                m.get("dep_nome") or "-", m.get("levantado_por") or "-",
                m.get("notas") or "-"), tag)

        # Indicador de filtro ativo
        filtros = []
        if tipo:       filtros.append(self._f_tipo.get())
        if pid:        filtros.append(self._f_prod.get())
        if funcionario: filtros.append(f"👤 {funcionario}")
        info = f"{len(movs)} registos"
        if filtros: info += f"  •  filtros: {', '.join(filtros)}"
        self._lbl_n.config(text=info)


class Alertas(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg"]); hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="Alertas de Stock Baixo", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        Btn(hdr, "Atualizar", cmd=self.refresh, estilo="ghost", icone="↻").pack(side="right")
        self._aviso = tk.Label(self, text="", bg=C["green_bg"], fg=C["green"],
                               font=("Segoe UI", 10, "bold"), pady=10, anchor="w", padx=16)
        self._aviso.pack(fill="x", pady=(0, 8))
        card = Card(self); card.pack(fill="both", expand=True)
        tk.Label(card, text="Produtos com Stock Abaixo do Mínimo", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
        self._tbl = Tabela(card, altura=20, colunas=[
            {"id": "nome",   "label": "Produto",      "w": 220, "s": True},
            {"id": "cod",    "label": "Código",       "w": 140},
            {"id": "cat",    "label": "Categoria",    "w": 110},
            {"id": "atual",  "label": "Stock Atual",  "w": 90,  "anc": "center"},
            {"id": "min",    "label": "Mínimo",       "w": 80,  "anc": "center"},
            {"id": "falta",  "label": "Em Falta",     "w": 80,  "anc": "center"},
            {"id": "un",     "label": "Un.",          "w": 50,  "anc": "center"},
            {"id": "local",  "label": "Localização",  "w": 110},
            {"id": "estado", "label": "Estado",       "w": 90,  "anc": "center"},
        ])
        self._tbl.pack(fill="both", expand=True, padx=8, pady=(0, 6))

    def refresh(self, _=None):
        alertas = db.prod_listar(so_baixo=True)
        n = len(alertas)
        if n == 0:
            self._aviso.config(text="  ✔  Todos os produtos estão acima do mínimo!",
                               bg=C["green_bg"], fg=C["green"])
        else:
            self._aviso.config(text=f"  ⚠  {n} produto{'s' if n>1 else ''} com stock baixo!",
                               bg=C["yellow_bg"], fg=C["yellow"])
        self._tbl.limpar()
        for p in alertas:
            sa, sm = p["stock_atual"], p["stock_minimo"]
            tag    = "zero" if sa == 0 else "baixo"
            estado = "Esgotado" if sa == 0 else "Baixo"
            self._tbl.linha((p["nome"], p["codigo_barras"], p.get("cat_nome","-"),
                sa, sm, f"-{sm-sa}", p["unidade"], p.get("localizacao","-"), estado), tag)
        self.app.set_badge(n)
