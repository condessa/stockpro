"""StockPro – Definições: Categorias e Departamentos"""
import tkinter as tk
from ui.tema import C, Card, Btn, FormLabel, Entrada, Tabela, toast, DialogoConfirmar
import db.database as db


class _ListaSimples(tk.Frame):
    """Componente reutilizável para gerir uma lista simples (categorias / departamentos)."""
    def __init__(self, parent, titulo, fn_listar, fn_criar, fn_apagar):
        super().__init__(parent, bg=C["bg2"])
        self._listar  = fn_listar
        self._criar   = fn_criar
        self._apagar  = fn_apagar
        self._build(titulo)

    def _build(self, titulo):
        tk.Label(self, text=titulo, bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        row = tk.Frame(self, bg=C["bg2"]); row.pack(fill="x", padx=14, pady=(0, 8))
        self._entrada = Entrada(row, placeholder="Nome…")
        self._entrada.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self._entrada.bind("<Return>", lambda _: self._adicionar())
        Btn(row, "Adicionar", cmd=self._adicionar, estilo="primary", icone="+").pack(side="left")

        self._tbl = Tabela(self, altura=12, colunas=[
            {"id": "nome", "label": "Nome", "w": 200, "s": True},
            {"id": "data", "label": "Criado em", "w": 140},
        ])
        self._tbl.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        act = tk.Frame(self, bg=C["bg2"]); act.pack(fill="x", padx=10, pady=(0, 6))
        Btn(act, "Apagar", cmd=self._apagar_sel, estilo="danger", icone="🗑").pack(side="left")

    def _adicionar(self):
        nome = self._entrada.val().strip()
        if not nome: toast(self, "Nome obrigatório!", "error"); return
        try:
            self._criar(nome); toast(self, f'"{nome}" adicionado!'); self._entrada.set(""); self.refresh()
        except Exception as e:
            toast(self, f"{'Já existe!' if 'Duplicate' in str(e) else e}", "error")

    def _apagar_sel(self):
        v = self._tbl.selecionado()
        if not v: toast(self, "Selecione um item!", "warning"); return
        d = DialogoConfirmar(self, "Apagar", f'Apagar "{v[0]}"?\n(Produtos/movimentos associados não são afetados)')
        if d.resultado:
            try:
                # Obter id pelo nome
                items = self._listar()
                item = next((x for x in items if x["nome"] == v[0]), None)
                if item: self._apagar(item["id"]); toast(self, "Apagado!", "warning"); self.refresh()
            except Exception as e:
                toast(self, f"Erro: {e}", "error")

    def refresh(self):
        self._tbl.limpar()
        for i, item in enumerate(self._listar()):
            self._tbl.linha((item["nome"], str(item["criado_em"])[:16]), "even" if i%2==0 else "odd")


class Definicoes(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Definições", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))

        pane = tk.Frame(self, bg=C["bg"]); pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=1); pane.columnconfigure(1, weight=1)

        card_cat = Card(pane); card_cat.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self._cats = _ListaSimples(card_cat, "Categorias",
                                   db.cat_listar, db.cat_criar, db.cat_apagar)
        self._cats.pack(fill="both", expand=True)

        card_dep = Card(pane); card_dep.grid(row=0, column=1, sticky="nsew")
        self._deps = _ListaSimples(card_dep, "Departamentos",
                                   db.dep_listar, db.dep_criar, db.dep_apagar)
        self._deps.pack(fill="both", expand=True)

    def refresh(self, _=None):
        self._cats.refresh()
        self._deps.refresh()
