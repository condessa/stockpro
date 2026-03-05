"""StockPro – Página de Produtos"""
import tkinter as tk
from ui.tema import C, Card, Btn, FormLabel, Entrada, Combo, Tabela, BarraPesquisa, toast, DialogoConfirmar
import db.database as db


class Produtos(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app      = app
        self._edit_id = None
        self._cats    = []
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg"]); hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="Produtos", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        Btn(hdr, "Exportar CSV", cmd=self._exportar, estilo="ghost",   icone="↓").pack(side="right", padx=(0, 8))
        Btn(hdr, "Novo Produto", cmd=self._novo,     estilo="primary", icone="+").pack(side="right", padx=(0, 8))

        pane = tk.Frame(self, bg=C["bg"]); pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=1); pane.columnconfigure(1, weight=0); pane.rowconfigure(0, weight=1)

        # Tabela
        esq = Card(pane); esq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tb = tk.Frame(esq, bg=C["bg2"]); tb.pack(fill="x", padx=10, pady=(10, 6))
        self._pesq = BarraPesquisa(tb, ao_mudar=lambda _: self.refresh())
        self._pesq.pack(side="left", fill="x", expand=True)
        self._var_baixo = tk.BooleanVar(value=False)
        tk.Checkbutton(tb, text="Só stock baixo", variable=self._var_baixo,
                       command=self.refresh, bg=C["bg2"], fg=C["text2"],
                       selectcolor=C["bg3"], activebackground=C["bg2"],
                       font=("Segoe UI", 9)).pack(side="right", padx=(10, 0))

        self._tbl = Tabela(esq, altura=18, colunas=[
            {"id": "cod",   "label": "Código",      "w": 130},
            {"id": "nome",  "label": "Nome",        "w": 200, "s": True},
            {"id": "cat",   "label": "Categoria",   "w": 110},
            {"id": "stock", "label": "Stock",       "w": 65,  "anc": "center"},
            {"id": "min",   "label": "Mínimo",      "w": 65,  "anc": "center"},
            {"id": "un",    "label": "Un.",         "w": 45,  "anc": "center"},
            {"id": "local", "label": "Localização", "w": 110},
            {"id": "est",   "label": "Estado",      "w": 100, "anc": "center"},
        ])
        self._tbl.pack(fill="both", expand=True, padx=8, pady=(0, 6))
        self._tbl.duplo_clique(lambda _: self._editar())

        act = tk.Frame(esq, bg=C["bg2"]); act.pack(fill="x", padx=10, pady=(0, 6))
        Btn(act, "Editar",   cmd=self._editar,   estilo="ghost",  icone="✏").pack(side="left", padx=(0, 6))
        Btn(act, "Eliminar", cmd=self._eliminar, estilo="danger", icone="🗑").pack(side="left")

        # Formulário
        self._form = Card(pane); self._form.grid(row=0, column=1, sticky="nsew")
        self._form.config(width=310); self._form.pack_propagate(False)
        self._build_form()

    def _build_form(self):
        inner = tk.Frame(self._form, bg=C["bg2"])
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        self._form_titulo = tk.Label(inner, text="Novo Produto", bg=C["bg2"], fg=C["text"],
                                     font=("Segoe UI", 13, "bold"))
        self._form_titulo.pack(anchor="w", pady=(0, 8))

        FormLabel(inner, "Código de Barras *").pack(anchor="w", pady=(0, 3))
        bc = tk.Frame(inner, bg=C["bg2"]); bc.pack(fill="x", pady=(0, 6))
        self._e_cod = Entrada(bc, placeholder="Scan ou insira…", mono=True)
        self._e_cod.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 4))
        self._e_cod.bind("<Return>", lambda _: self._e_nome.focus())

        FormLabel(inner, "Nome *").pack(anchor="w", pady=(0, 3))
        self._e_nome = Entrada(inner, placeholder="Ex: Luvas proteção M")
        self._e_nome.pack(fill="x", ipady=6, pady=(0, 6))

        FormLabel(inner, "Descrição").pack(anchor="w", pady=(0, 3))
        self._e_desc = Entrada(inner, placeholder="Opcional")
        self._e_desc.pack(fill="x", ipady=6, pady=(0, 6))

        FormLabel(inner, "Categoria").pack(anchor="w", pady=(0, 3))
        self._e_cat = Combo(inner, width=28)
        self._e_cat.pack(fill="x", pady=(0, 6))

        r2 = tk.Frame(inner, bg=C["bg2"]); r2.pack(fill="x", pady=(0, 6))
        lf = tk.Frame(r2, bg=C["bg2"]); lf.pack(side="left", fill="x", expand=True, padx=(0, 4))
        rf = tk.Frame(r2, bg=C["bg2"]); rf.pack(side="left", fill="x", expand=True)
        FormLabel(lf, "Stock Inicial").pack(anchor="w", pady=(0, 3))
        self._e_stock = Entrada(lf, placeholder="0"); self._e_stock.pack(fill="x", ipady=6)
        FormLabel(rf, "Stock Mínimo *").pack(anchor="w", pady=(0, 3))
        self._e_min = Entrada(rf, placeholder="5"); self._e_min.pack(fill="x", ipady=6)

        r3 = tk.Frame(inner, bg=C["bg2"]); r3.pack(fill="x", pady=(0, 6))
        lf3 = tk.Frame(r3, bg=C["bg2"]); lf3.pack(side="left", padx=(0, 4))
        rf3 = tk.Frame(r3, bg=C["bg2"]); rf3.pack(side="left", fill="x", expand=True)
        FormLabel(lf3, "Unidade").pack(anchor="w", pady=(0, 3))
        self._e_un = Combo(lf3, valores=["un","kg","lt","m","cm","cx","par","rolo"], width=7)
        self._e_un.set("un"); self._e_un.pack()
        FormLabel(rf3, "Localização").pack(anchor="w", pady=(0, 3))
        self._e_local = Entrada(rf3, placeholder="Ex: A1-P2"); self._e_local.pack(fill="x", ipady=6)

        br = tk.Frame(inner, bg=C["bg2"]); br.pack(fill="x", pady=(8, 0))
        Btn(br, "Cancelar", cmd=self._limpar, estilo="ghost").pack(side="left", padx=(0, 8))
        Btn(br, "Guardar",  cmd=self._guardar, estilo="primary", icone="💾").pack(side="left")

    def _novo(self):
        self._limpar()
        self._e_cod.focus()

    def _limpar(self):
        self._edit_id = None
        self._form_titulo.config(text="Novo Produto")
        self._e_cod.config(state="normal")
        for e in [self._e_cod, self._e_nome, self._e_desc, self._e_stock, self._e_min, self._e_local]:
            e.set("")
        self._e_un.set("un")

    def _guardar(self):
        cod  = self._e_cod.val().strip()
        nome = self._e_nome.val().strip()
        minv = self._e_min.val().strip()
        if not cod:  toast(self, "Código obrigatório!",    "error"); return
        if not nome: toast(self, "Nome obrigatório!",      "error"); return
        if not minv.isdigit(): toast(self, "Mínimo inválido!", "error"); return
        cat_id = next((c["id"] for c in self._cats if c["nome"] == self._e_cat.get()), None)
        try:
            if self._edit_id:
                db.prod_atualizar(self._edit_id, nome, self._e_desc.val(),
                                  cat_id, int(minv), self._e_un.get(), self._e_local.val())
                toast(self, f'"{nome}" atualizado!')
            else:
                stock_ini = int(self._e_stock.val() or 0)
                db.prod_criar(cod, nome, self._e_desc.val(), cat_id,
                              stock_ini, int(minv), self._e_un.get(), self._e_local.val())
                toast(self, f'"{nome}" registado!')
            self._limpar(); self.refresh(); self.app.pages["dashboard"].refresh()
        except Exception as e:
            toast(self, f"Erro: {'Código já existe!' if 'Duplicate' in str(e) else e}", "error")

    def _editar(self):
        v = self._tbl.selecionado()
        if not v: toast(self, "Selecione um produto!", "warning"); return
        p = db.prod_por_codigo(v[0])
        if not p: return
        self._edit_id = p["id"]
        self._form_titulo.config(text="Editar Produto")
        self._e_cod.config(state="normal"); self._e_cod.set(p["codigo_barras"]); self._e_cod.config(state="disabled")
        self._e_nome.set(p["nome"]); self._e_desc.set(p.get("descricao") or "")
        self._e_stock.set(str(p["stock_atual"])); self._e_min.set(str(p["stock_minimo"]))
        self._e_local.set(p.get("localizacao") or ""); self._e_un.set(p.get("unidade","un"))
        if p.get("cat_nome"): self._e_cat.set(p["cat_nome"])

    def _eliminar(self):
        v = self._tbl.selecionado()
        if not v: toast(self, "Selecione um produto!", "warning"); return
        d = DialogoConfirmar(self, "Eliminar", f'Eliminar "{v[1]}"?')
        if d.resultado:
            p = db.prod_por_codigo(v[0])
            if p: db.prod_apagar(p["id"]); toast(self, "Eliminado!", "warning")
            self.refresh(); self.app.pages["dashboard"].refresh()

    def _exportar(self):
        import csv
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV","*.csv")], initialfile="produtos.csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Código","Nome","Categoria","Stock","Mínimo","Unidade","Localização","Estado"])
            for p in db.prod_listar():
                est = "Esgotado" if p["stock_atual"]==0 else ("Baixo" if p["stock_atual"]<p["stock_minimo"] else "OK")
                w.writerow([p["codigo_barras"],p["nome"],p.get("cat_nome",""),
                            p["stock_atual"],p["stock_minimo"],p["unidade"],p.get("localizacao",""),est])
        toast(self, "CSV exportado!")

    def refresh(self, _=None):
        self._cats = db.cat_listar()
        nomes = [c["nome"] for c in self._cats]
        self._e_cat["values"] = nomes
        if nomes and not self._e_cat.get(): self._e_cat.set(nomes[0])
        self._tbl.limpar()
        for p in db.prod_listar(self._pesq.val(), self._var_baixo.get()):
            sa, sm = p["stock_atual"], p["stock_minimo"]
            tag    = "zero" if sa==0 else ("baixo" if sa<sm else "even")
            estado = "Esgotado" if sa==0 else ("Baixo" if sa<sm else "OK")
            self._tbl.linha((p["codigo_barras"],p["nome"],p.get("cat_nome","-"),
                             sa,sm,p["unidade"],p.get("localizacao","-"),estado), tag)
