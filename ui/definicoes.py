"""StockPro – Definições: Categorias, Departamentos e Sobre"""
import tkinter as tk
import threading
import urllib.request
from ui.tema import C, Card, Btn, FormLabel, Entrada, Tabela, toast, DialogoConfirmar
import db.database as db
from version import VERSION, RELEASE_DATE, AUTHOR, UPDATE_CHECK_URL


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
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))
        row = tk.Frame(self, bg=C["bg2"]); row.pack(fill="x", padx=14, pady=(0, 8))
        self._entrada = Entrada(row, placeholder="Nome…")
        self._entrada.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self._entrada.bind("<Return>", lambda _: self._adicionar())
        Btn(row, "Adicionar", cmd=self._adicionar, estilo="primary", icone="+").pack(side="left")
        self._tbl = Tabela(self, altura=12, colunas=[
            {"id": "nome", "label": "Nome",       "w": 200, "s": True},
            {"id": "data", "label": "Criado em",  "w": 140},
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
                item = next((x for x in self._listar() if x["nome"] == v[0]), None)
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

        # Tabs
        tab_bar = tk.Frame(self, bg=C["bg"]); tab_bar.pack(fill="x", pady=(0, 10))
        self._tabs  = {}
        self._frame_atual = None
        for chave, label in [("listas", "📋  Categorias & Departamentos"),
                              ("sobre",  "ℹ️  Sobre & Atualizações")]:
            b = tk.Label(tab_bar, text=label, bg=C["bg3"], fg=C["text2"],
                         font=("Segoe UI", 9, "bold"), padx=14, pady=6, cursor="hand2")
            b.pack(side="left", padx=(0, 2))
            b.bind("<Button-1>", lambda _, k=chave: self._mostrar_tab(k))
            self._tabs[chave] = b

        # Frame Listas
        self._frm_listas = tk.Frame(self, bg=C["bg"]); 
        pane = tk.Frame(self._frm_listas, bg=C["bg"]); pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=1); pane.columnconfigure(1, weight=1)
        card_cat = Card(pane); card_cat.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self._cats = _ListaSimples(card_cat, "Categorias", db.cat_listar, db.cat_criar, db.cat_apagar)
        self._cats.pack(fill="both", expand=True)
        card_dep = Card(pane); card_dep.grid(row=0, column=1, sticky="nsew")
        self._deps = _ListaSimples(card_dep, "Departamentos", db.dep_listar, db.dep_criar, db.dep_apagar)
        self._deps.pack(fill="both", expand=True)

        # Frame Sobre
        self._frm_sobre = tk.Frame(self, bg=C["bg"])
        self._build_sobre()

        self._mostrar_tab("listas")

    def _build_sobre(self):
        f = self._frm_sobre
        card = Card(f); card.pack(fill="x", pady=(0, 12))
        inn  = tk.Frame(card, bg=C["bg2"]); inn.pack(fill="x", padx=20, pady=16)

        # Logo + versão
        tk.Label(inn, text="StockPro", bg=C["bg2"], fg=C["accent"],
                 font=("Consolas", 22, "bold")).pack(anchor="w")
        tk.Label(inn, text="GESTÃO DE STOCKS", bg=C["bg2"], fg=C["text3"],
                 font=("Segoe UI", 7, "bold")).pack(anchor="w")
        tk.Frame(inn, bg=C["border"], height=1).pack(fill="x", pady=10)

        grid = tk.Frame(inn, bg=C["bg2"]); grid.pack(fill="x")
        for i, (label, valor) in enumerate([
            ("Versão",         VERSION),
            ("Data de lançamento", RELEASE_DATE),
            ("Desenvolvido por",   AUTHOR),
            ("Licença",            "Uso privado"),
        ]):
            tk.Label(grid, text=label, bg=C["bg2"], fg=C["text3"],
                     font=("Segoe UI", 8, "bold"), width=22, anchor="w").grid(row=i, column=0, pady=3, sticky="w")
            tk.Label(grid, text=valor, bg=C["bg2"], fg=C["text"],
                     font=("Segoe UI", 9), anchor="w").grid(row=i, column=1, pady=3, sticky="w")

        # Atualização
        card2 = Card(f); card2.pack(fill="x")
        inn2  = tk.Frame(card2, bg=C["bg2"]); inn2.pack(fill="x", padx=20, pady=16)
        tk.Label(inn2, text="Atualizações", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        row = tk.Frame(inn2, bg=C["bg2"]); row.pack(fill="x")
        tk.Label(row, text=f"Versão instalada:  {VERSION}", bg=C["bg2"], fg=C["text2"],
                 font=("Segoe UI", 9)).pack(side="left")
        Btn(row, "Verificar atualização", cmd=self._verificar_update,
            estilo="ghost", icone="↻").pack(side="right")

        self._lbl_update = tk.Label(inn2, text="", bg=C["bg2"],
                                    font=("Segoe UI", 9), anchor="w")
        self._lbl_update.pack(anchor="w", pady=(8, 0))

    def _mostrar_tab(self, chave):
        # Estilo tabs
        for k, b in self._tabs.items():
            b.config(bg=C["accent"] if k==chave else C["bg3"],
                     fg=C["white"]  if k==chave else C["text2"])
        # Trocar frame
        if self._frame_atual: self._frame_atual.pack_forget()
        frame = self._frm_listas if chave == "listas" else self._frm_sobre
        frame.pack(fill="both", expand=True)
        self._frame_atual = frame
        if chave == "listas":
            self._cats.refresh(); self._deps.refresh()

    def _verificar_update(self):
        self._lbl_update.config(text="A verificar…", fg=C["text2"])
        threading.Thread(target=self._check_update_async, daemon=True).start()

    def _check_update_async(self):
        try:
            req = urllib.request.Request(UPDATE_CHECK_URL,
                headers={"User-Agent": f"StockPro/{VERSION}"})
            with urllib.request.urlopen(req, timeout=5) as r:
                latest = r.read().decode().strip()
            def _mostrar():
                v_cur = tuple(int(x) for x in VERSION.split("."))
                v_new = tuple(int(x) for x in latest.split("."))
                if v_new > v_cur:
                    self._lbl_update.config(
                        text=f"⬆  Nova versão disponível: {latest}  —  Descarrega o novo .deb em github.com/hcsoftware/stockpro",
                        fg=C["yellow"])
                else:
                    self._lbl_update.config(
                        text=f"✔  Tens a versão mais recente ({VERSION})",
                        fg=C["green"])
            self.after(0, _mostrar)
        except Exception:
            self.after(0, lambda: self._lbl_update.config(
                text="⚠  Não foi possível verificar (sem ligação à internet?)",
                fg=C["text3"]))

    def refresh(self, _=None):
        self._cats.refresh()
        self._deps.refresh()
