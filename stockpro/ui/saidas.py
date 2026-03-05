"""StockPro – Saídas de stock"""
import tkinter as tk
from datetime import date
from ui.tema import C, Card, Btn, FormLabel, Entrada, Combo, Tabela, BarraPesquisa, toast
import db.database as db


class Saidas(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app  = app
        self._mapa_prod = {}
        self._mapa_dep  = {}
        self._build()

    def _build(self):
        tk.Label(self, text="Saídas de Stock", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))
        pane = tk.Frame(self, bg=C["bg"]); pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=0); pane.columnconfigure(1, weight=1); pane.rowconfigure(0, weight=1)

        form = Card(pane); form.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        form.config(width=320); form.pack_propagate(False)
        inn = tk.Frame(form, bg=C["bg2"]); inn.pack(fill="both", expand=True, padx=16, pady=14)

        tk.Label(inn, text="Registar Saída", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

        FormLabel(inn, "Código de Barras").pack(anchor="w", pady=(0, 3))
        bc = tk.Frame(inn, bg=C["bg2"]); bc.pack(fill="x", pady=(0, 6))
        self._e_cod = Entrada(bc, placeholder="Scan ou código…", mono=True)
        self._e_cod.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 4))
        self._e_cod.bind("<Return>",   lambda _: self._lookup())
        self._e_cod.bind("<FocusOut>", lambda _: self._lookup())
        Btn(bc, "Procurar", cmd=self._lookup, estilo="ghost").pack(side="left")

        FormLabel(inn, "Produto").pack(anchor="w", pady=(0, 3))
        self._e_prod = Combo(inn, width=32)
        self._e_prod.pack(fill="x", pady=(0, 6))
        self._e_prod.bind("<<ComboboxSelected>>", self._ao_selecionar)

        FormLabel(inn, "Quantidade *").pack(anchor="w", pady=(0, 3))
        self._e_qtd = Entrada(inn, placeholder="1"); self._e_qtd.pack(fill="x", ipady=6, pady=(0, 6))

        FormLabel(inn, "Data").pack(anchor="w", pady=(0, 3))
        self._e_data = Entrada(inn); self._e_data.pack(fill="x", ipady=6, pady=(0, 6))
        self._e_data.set(str(date.today()))

        FormLabel(inn, "Secção / Departamento").pack(anchor="w", pady=(0, 3))
        self._e_dep = Combo(inn, width=32); self._e_dep.pack(fill="x", pady=(0, 6))

        FormLabel(inn, "Levantado por *").pack(anchor="w", pady=(0, 3))
        self._e_pessoa = Entrada(inn, placeholder="Nome do colaborador")
        self._e_pessoa.pack(fill="x", ipady=6, pady=(0, 6))

        self._info = tk.Label(inn, text="Nenhum produto selecionado",
                              bg=C["bg3"], fg=C["text3"], font=("Segoe UI", 9),
                              pady=8, padx=10, anchor="w",
                              highlightthickness=1, highlightbackground=C["border"])
        self._info.pack(fill="x", pady=(0, 8))
        Btn(inn, "Registar Saída", cmd=self._registar, estilo="danger", icone="⬆").pack(fill="x")

        dir = Card(pane); dir.grid(row=0, column=1, sticky="nsew")
        top = tk.Frame(dir, bg=C["bg2"]); top.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(top, text="Histórico de Saídas", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        self._pesq = BarraPesquisa(top, ao_mudar=lambda _: self.refresh())
        self._pesq.pack(side="right")
        self._tbl = Tabela(dir, altura=20, colunas=[
            {"id": "data",   "label": "Data",         "w": 90},
            {"id": "prod",   "label": "Produto",      "w": 180, "s": True},
            {"id": "qtd",    "label": "Qtd",          "w": 65,  "anc": "center"},
            {"id": "antes",  "label": "Antes",        "w": 55,  "anc": "center"},
            {"id": "depois", "label": "Depois",       "w": 55,  "anc": "center"},
            {"id": "dep",    "label": "Departamento", "w": 120},
            {"id": "pessoa", "label": "Colaborador",  "w": 130},
        ])
        self._tbl.pack(fill="both", expand=True, padx=8, pady=(0, 6))

    def _carregar_dados(self):
        self._mapa_prod = {}
        for p in db.prod_listar():
            lbl = f"{p['nome']}  [{p['codigo_barras']}]"
            self._mapa_prod[lbl] = p
        self._e_prod["values"] = list(self._mapa_prod.keys())
        self._mapa_dep = {}
        for d in db.dep_listar():
            self._mapa_dep[d["nome"]] = d["id"]
        self._e_dep["values"] = list(self._mapa_dep.keys())

    def _lookup(self):
        cod = self._e_cod.val().strip()
        if not cod: return
        if self._e_prod.get() and f"[{cod}]" in self._e_prod.get(): return
        p = db.prod_por_codigo(cod)
        if p: self._preencher(p); self._e_qtd.focus()
        else: toast(self, "Código não encontrado!", "error")

    def _preencher(self, p):
        lbl = f"{p['nome']}  [{p['codigo_barras']}]"
        self._mapa_prod[lbl] = p
        self._e_prod["values"] = list(self._mapa_prod.keys())
        self._e_prod.set(""); self._e_prod.set(lbl)
        self._atualizar_info(p)
        toast(self, f"Produto: {p['nome']}")

    def _ao_selecionar(self, _=None):
        p = self._mapa_prod.get(self._e_prod.get())
        if p:
            fresh = db.prod_por_id(p["id"]) or p
            self._e_cod.set(fresh["codigo_barras"])
            self._atualizar_info(fresh)

    def _atualizar_info(self, p):
        sa, sm = p["stock_atual"], p["stock_minimo"]
        if sa == 0:    txt, cor = "  ESGOTADO – sem stock disponível", C["red"]
        elif sa < sm:  txt, cor = f"  Stock: {sa} {p['unidade']}  (abaixo do mínimo: {sm})", C["yellow"]
        else:          txt, cor = f"  Stock: {sa} {p['unidade']}   |   Mínimo: {sm}", C["green"]
        self._info.config(text=txt, fg=cor)

    def _registar(self):
        p = self._mapa_prod.get(self._e_prod.get())
        if not p: toast(self, "Selecione um produto!", "error"); return
        qtd = self._e_qtd.val().strip()
        if not qtd.isdigit() or int(qtd) < 1: toast(self, "Quantidade inválida!", "error"); return
        dep    = self._e_dep.get()
        dep_id = self._mapa_dep.get(dep)  # None se não selecionado
        pessoa = self._e_pessoa.val().strip()
        if not pessoa: toast(self, "Indique quem levanta!", "error"); return
        try:
            novo = db.mov_saida(p["id"], int(qtd), dep_id, pessoa,
                                self._e_data.val() or str(date.today()))
            pf = db.prod_por_id(p["id"])
            if pf and novo < pf["stock_minimo"]:
                toast(self, f"⚠ Stock baixo! {p['nome']} ficou com {novo} unidades.", "warning")
            else:
                toast(self, f"-{qtd} {p['unidade']} de \"{p['nome']}\" registados!")
            self._e_cod.set(""); self._e_prod.set(""); self._e_qtd.set("")
            self._e_dep.set(""); self._e_pessoa.set("")
            self._info.config(text="Nenhum produto selecionado", fg=C["text3"])
            self.refresh(); self.app.pages["dashboard"].refresh()
        except ValueError as e: toast(self, str(e), "error")
        except Exception as e:  toast(self, f"Erro: {e}", "error")

    def refresh(self, _=None):
        self._carregar_dados()
        self._tbl.limpar()
        for i, m in enumerate(db.mov_listar("saida", self._pesq.val())):
            self._tbl.linha((str(m["data_movimento"]), m["prod_nome"],
                f"-{m['quantidade']} {m['unidade']}", m["stock_antes"], m["stock_depois"],
                m.get("dep_nome") or "-", m.get("levantado_por") or "-"),
                "even" if i%2==0 else "odd")
