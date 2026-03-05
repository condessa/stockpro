"""StockPro – Janela principal"""
import tkinter as tk
from datetime import datetime
import threading

from ui.tema import C, aplicar_estilo, Btn, toast
from ui.dashboard    import Dashboard
from ui.produtos     import Produtos
from ui.entradas     import Entradas
from ui.saidas       import Saidas
from ui.historico    import Historico, Alertas
from ui.utilizadores import Utilizadores
from ui.definicoes   import Definicoes
from ui.bloqueio     import EcraBloqueio, TIMEOUT_SEGUNDOS
import db.database as db

SB_FECHADA = 52
SB_ABERTA  = 210


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StockPro – Gestão de Stocks  by HCsoftware")
        self.geometry("1280x780")
        self.minsize(1000, 640)
        self.config(bg=C["bg"])
        aplicar_estilo()

        self._pagina_atual  = None
        self._nav_btns      = {}
        self._nav_items     = []
        self._secao_labels  = []
        self._utilizador    = None
        self.pages          = {}
        self._sb_fixada     = False
        self._sb_aberta     = False
        self._anim_id       = None
        self._inatividade   = 0
        self._bloqueado     = False
        self._a_monitorizar = False

        # Janela principal abre imediatamente com ecrã de boas-vindas
        self._mostrar_boas_vindas()
        # Ligação à BD em background
        self.after(200, self._iniciar)

    # ── Ecrã de boas-vindas (fundo permanente) ────────────────────────────────
    def _mostrar_boas_vindas(self):
        for w in self.winfo_children(): w.destroy()
        f = tk.Frame(self, bg=C["bg"]); f.pack(fill="both", expand=True)

        topbar = tk.Frame(f, bg=C["bg2"], height=40,
                          highlightthickness=1, highlightbackground=C["border"])
        topbar.pack(fill="x"); topbar.pack_propagate(False)
        tk.Label(topbar, text="StockPro", bg=C["bg2"], fg=C["accent"],
                 font=("Consolas", 12, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(topbar, text="by HCsoftware", bg=C["bg2"], fg=C["text3"],
                 font=("Segoe UI", 7)).pack(side="left")

        centro = tk.Frame(f, bg=C["bg"])
        centro.place(relx=.5, rely=.5, anchor="center")
        tk.Label(centro, text="🏭", bg=C["bg"], font=("Segoe UI", 52)).pack()
        tk.Label(centro, text="StockPro", bg=C["bg"], fg=C["accent"],
                 font=("Consolas", 30, "bold")).pack()
        tk.Label(centro, text="GESTÃO DE STOCKS", bg=C["bg"], fg=C["text3"],
                 font=("Segoe UI", 10, "bold")).pack(pady=(0, 6))
        self._lbl_estado = tk.Label(centro, text="A ligar à base de dados…",
                                    bg=C["bg"], fg=C["text2"],
                                    font=("Segoe UI", 10))
        self._lbl_estado.pack()

    # ── Arranque / ligação ────────────────────────────────────────────────────
    def _iniciar(self):
        import config
        cfg = config.carregar()
        if not config.existe() or not config.valida(cfg):
            from ui.setup import SetupWizard
            SetupWizard(self, cfg, ao_guardar=self._ligar)
        else:
            self._ligar(cfg)

    def _ligar(self, cfg):
        import config
        db.DB_CONFIG.update({
            "host": cfg["host"], "port": int(cfg["port"]),
            "user": cfg["user"], "password": cfg["password"],
            "database": cfg["database"], "charset": "utf8mb4",
        })
        config.guardar(cfg)
        threading.Thread(target=self._ligar_async, daemon=True).start()

    def _ligar_async(self):
        ok, msg = db.get_db().connect()
        self.after(0, lambda: self._apos_ligacao(ok, msg))

    def _apos_ligacao(self, ok, msg):
        if not ok:
            from tkinter import messagebox
            import os, config
            messagebox.showerror("Erro de Ligação",
                f"Não foi possível ligar ao MySQL:\n\n{msg}")
            if os.path.exists(config.CONFIG_FILE):
                os.remove(config.CONFIG_FILE)
            self.destroy(); return
        try:
            self._lbl_estado.config(text="✔  Ligado!", fg=C["green"])
        except Exception: pass
        self.after(400, self._mostrar_login)

    # ── Login (por cima da janela principal) ──────────────────────────────────
    def _mostrar_login(self):
        from ui.login import LoginWindow
        LoginWindow(self, ao_login=self._apos_login)

    def _apos_login(self, utilizador):
        self._utilizador = utilizador
        self._construir_ui()
        self._iniciar_monitor_inatividade()

    # ── Inatividade ───────────────────────────────────────────────────────────
    def _iniciar_monitor_inatividade(self):
        self._inatividade   = 0
        self._bloqueado     = False
        self._a_monitorizar = True
        for ev in ("<Motion>", "<KeyPress>", "<ButtonPress>", "<MouseWheel>"):
            self.bind_all(ev, self._reset_inatividade)
        self._verificar_inatividade()

    def _reset_inatividade(self, _=None):
        self._inatividade = 0

    def _verificar_inatividade(self):
        if not self._a_monitorizar: return
        if not self._bloqueado:
            self._inatividade += 1
            if self._inatividade >= TIMEOUT_SEGUNDOS:
                self._bloquear()
        self.after(1000, self._verificar_inatividade)

    def _bloquear(self):
        if self._bloqueado or not self._utilizador: return
        self._bloqueado = True
        EcraBloqueio(self, self._utilizador, self._ao_desbloquear)

    def _ao_desbloquear(self, logout=False):
        self._bloqueado   = False
        self._inatividade = 0
        if logout:
            self._a_monitorizar = False
            self._logout()

    # ── UI principal ──────────────────────────────────────────────────────────
    def _construir_ui(self):
        for w in self.winfo_children(): w.destroy()
        self._nav_btns     = {}
        self._nav_items    = []
        self._secao_labels = []
        self.pages         = {}
        self._sb_fixada    = False
        self._sb_aberta    = False

        root = tk.Frame(self, bg=C["bg"]); root.pack(fill="both", expand=True)

        # Sidebar
        self._sidebar = tk.Frame(root, bg=C["bg2"], width=SB_FECHADA,
                                 highlightthickness=1, highlightbackground=C["border"])
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._sidebar.bind("<Enter>", self._sb_hover_in)
        self._sidebar.bind("<Leave>", self._sb_hover_out)

        topo = tk.Frame(self._sidebar, bg=C["bg2"]); topo.pack(fill="x")
        self._btn_toggle = tk.Label(topo, text="☰", bg=C["bg2"], fg=C["text2"],
                                    font=("Segoe UI", 12), padx=10, pady=8, cursor="hand2")
        self._btn_toggle.pack(side="left")
        self._btn_toggle.bind("<Button-1>", self._toggle_fixar)

        self._logo_frame = tk.Frame(topo, bg=C["bg2"]); self._logo_frame.pack(side="left")
        tk.Label(self._logo_frame, text="StockPro", bg=C["bg2"], fg=C["accent"],
                 font=("Consolas", 11, "bold")).pack(anchor="w")
        tk.Label(self._logo_frame, text="GESTÃO DE STOCKS", bg=C["bg2"], fg=C["text3"],
                 font=("Segoe UI", 6, "bold")).pack(anchor="w")
        tk.Frame(self._sidebar, bg=C["border"], height=1).pack(fill="x")

        self._add_secao("PRINCIPAL")
        self._add_nav("Dashboard",    "dashboard",    "📊")
        self._add_nav("Produtos",     "produtos",     "📦")
        self._add_secao("MOVIMENTOS")
        self._add_nav("Entradas",     "entradas",     "⬇")
        self._add_nav("Saídas",       "saidas",       "⬆")
        self._add_secao("RELATÓRIOS")
        self._add_nav("Histórico",    "historico",    "📋")
        self._add_nav("Alertas",      "alertas",      "🔔")
        self._add_secao("CONFIG.")
        self._add_nav("Definições",   "definicoes",   "⚙")
        if self._utilizador and self._utilizador.get("role") == "admin":
            self._add_nav("Utilizadores", "utilizadores", "👥")

        self._badge = tk.Label(self._sidebar, text="", bg=C["yellow_bg"], fg=C["yellow"],
                               font=("Segoe UI", 7, "bold"), cursor="hand2", pady=2)
        self._badge.bind("<Button-1>", lambda _: self.ir("alertas"))

        # Rodapé sidebar
        self._rod = tk.Frame(self._sidebar, bg=C["bg2"])
        self._rod.pack(side="bottom", fill="x", padx=8, pady=8)
        tk.Frame(self._rod, bg=C["border"], height=1).pack(fill="x", pady=(0, 6))
        rod_top = tk.Frame(self._rod, bg=C["bg2"]); rod_top.pack(fill="x")
        tk.Label(rod_top, text="👤", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 13)).pack(side="left", padx=(4, 0))
        self._rod_info = tk.Frame(rod_top, bg=C["bg2"]); self._rod_info.pack(side="left", padx=6)
        nome = self._utilizador.get("nome", "") if self._utilizador else ""
        role = self._utilizador.get("role", "") if self._utilizador else ""
        tk.Label(self._rod_info, text=nome, bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(self._rod_info, text=role.capitalize(), bg=C["bg2"], fg=C["accent"],
                 font=("Segoe UI", 7)).pack(anchor="w")
        self._rod_extra = tk.Frame(self._rod, bg=C["bg2"]); self._rod_extra.pack(fill="x", pady=(6, 0))
        self._lbl_bd   = tk.Label(self._rod_extra, text="● Ligado", bg=C["bg2"], fg=C["green"],
                                  font=("Segoe UI", 8)); self._lbl_bd.pack(anchor="w")
        self._lbl_hora = tk.Label(self._rod_extra, text="", bg=C["bg2"], fg=C["text3"],
                                  font=("Consolas", 7)); self._lbl_hora.pack(anchor="w")
        tk.Frame(self._rod, bg=C["border"], height=1).pack(fill="x", pady=(6, 4))
        rod_btns = tk.Frame(self._rod, bg=C["bg2"]); rod_btns.pack(fill="x")
        Btn(rod_btns, "Backup", cmd=self._backup, estilo="neutral", icone="💾").pack(side="left", fill="x", expand=True, padx=(0, 2))
        Btn(rod_btns, "Sair",   cmd=self._logout, estilo="ghost",   icone="⏻").pack(side="left", fill="x", expand=True)

        self._aplicar_estado(aberta=False)

        # Área conteúdo
        cont = tk.Frame(root, bg=C["bg"]); cont.pack(side="left", fill="both", expand=True)
        topbar = tk.Frame(cont, bg=C["bg2"], height=40,
                          highlightthickness=1, highlightbackground=C["border"])
        topbar.pack(fill="x"); topbar.pack_propagate(False)
        self._lbl_titulo = tk.Label(topbar, text="Dashboard", bg=C["bg2"], fg=C["text"],
                                    font=("Segoe UI", 11, "bold"))
        self._lbl_titulo.pack(side="left", padx=14, pady=8)
        self._lbl_inativ = tk.Label(topbar, text="", bg=C["bg2"], fg=C["text3"],
                                    font=("Consolas", 8))
        self._lbl_inativ.pack(side="left", padx=(0, 10))
        bf = tk.Frame(topbar, bg=C["bg2"]); bf.pack(side="right", padx=10, pady=5)
        Btn(bf, "Nova Entrada", cmd=lambda: self.ir("entradas"), estilo="success", icone="⬇").pack(side="left", padx=(0, 8))
        Btn(bf, "Nova Saída",   cmd=lambda: self.ir("saidas"),   estilo="danger",  icone="⬆").pack(side="left")

        self._area = tk.Frame(cont, bg=C["bg"])
        self._area.pack(fill="both", expand=True, padx=14, pady=10)

        self.pages = {
            "dashboard":    Dashboard(self._area, self),
            "produtos":     Produtos(self._area, self),
            "entradas":     Entradas(self._area, self),
            "saidas":       Saidas(self._area, self),
            "historico":    Historico(self._area, self),
            "alertas":      Alertas(self._area, self),
            "definicoes":   Definicoes(self._area, self),
            "utilizadores": Utilizadores(self._area, self),
        }
        self._ir_inicial("dashboard")
        self.pages["dashboard"].refresh()
        self.set_badge(db.prod_contar_alertas())
        self._tick()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _add_secao(self, txt):
        lbl = tk.Label(self._sidebar, text=txt, bg=C["bg2"], fg=C["text3"],
                       font=("Segoe UI", 6, "bold"), anchor="w")
        lbl.pack(fill="x", padx=14, pady=(8, 1))
        self._secao_labels.append(lbl)

    def _add_nav(self, label, chave, icone="•"):
        f = tk.Frame(self._sidebar, bg=C["bg2"], cursor="hand2"); f.pack(fill="x", padx=4, pady=1)
        li = tk.Label(f, text=icone, bg=C["bg2"], fg=C["text2"],
                      font=("Segoe UI", 11), width=3, anchor="center")
        li.pack(side="left", ipady=7)
        lt = tk.Label(f, text=label, bg=C["bg2"], fg=C["text2"],
                      font=("Segoe UI", 9), anchor="w")
        lt.pack(side="left", fill="x", expand=True)
        for w in (f, li, lt):
            w.bind("<Button-1>", lambda _, c=chave: self.ir(c))
            w.bind("<Enter>",    lambda e, c=chave: (self._nav_hover(c, True),  self._sb_hover_in(e)),  add="+")
            w.bind("<Leave>",    lambda e, c=chave: (self._nav_hover(c, False), self._sb_hover_out(e)), add="+")
        self._nav_btns[chave] = (f, li, lt)
        self._nav_items.append((chave, icone, label))

    def _nav_hover(self, chave, on):
        if chave not in self._nav_btns or chave == self._pagina_atual: return
        f, li, lt = self._nav_btns[chave]
        bg = C["hover"] if on else C["bg2"]
        for w in (f, li, lt): w.config(bg=bg)

    def _nav_selecionar(self, chave):
        for c, (f, li, lt) in self._nav_btns.items():
            sel = (c == chave)
            bg  = C["accent"] if sel else C["bg2"]
            fg  = C["white"]  if sel else C["text2"]
            for w in (f, li, lt): w.config(bg=bg)
            li.config(fg=fg); lt.config(fg=fg)

    def _sb_hover_in(self, _=None):
        if not self._sb_fixada:
            self._sb_aberta = True; self._animar(SB_ABERTA)

    def _sb_hover_out(self, event=None):
        if self._sb_fixada: return
        try:
            x, y = self._sidebar.winfo_pointerxy()
            sx, sy = self._sidebar.winfo_rootx(), self._sidebar.winfo_rooty()
            if sx <= x <= sx + self._sidebar.winfo_width() and \
               sy <= y <= sy + self._sidebar.winfo_height(): return
        except Exception: pass
        self._sb_aberta = False; self._animar(SB_FECHADA)

    def _toggle_fixar(self, _=None):
        self._sb_fixada = not self._sb_fixada
        self._btn_toggle.config(fg=C["accent"] if self._sb_fixada else C["text2"])
        self._animar(SB_ABERTA if self._sb_fixada else SB_FECHADA)

    def _animar(self, alvo):
        if self._anim_id:
            try: self.after_cancel(self._anim_id)
            except Exception: pass
        self._anim_passo(alvo)

    def _anim_passo(self, alvo):
        try: atual = self._sidebar.winfo_width()
        except Exception: return
        diff = alvo - atual
        if abs(diff) < 3:
            self._sidebar.config(width=alvo)
            self._aplicar_estado(alvo >= SB_ABERTA - 10); return
        self._sidebar.config(width=atual + (1 if diff > 0 else -1) * max(8, abs(diff) // 3))
        self._anim_id = self.after(12, lambda: self._anim_passo(alvo))

    def _aplicar_estado(self, aberta):
        if aberta: self._logo_frame.pack(side="left")
        else:      self._logo_frame.pack_forget()
        for lbl in self._secao_labels:
            if aberta: lbl.pack(fill="x", padx=18, pady=(7, 1))
            else:      lbl.pack_forget()
        for _, (f, li, lt) in self._nav_btns.items():
            if aberta: lt.pack(side="left", fill="x", expand=True)
            else:      lt.pack_forget()
        if aberta:
            self._rod_info.pack(side="left", padx=6)
            self._rod_extra.pack(fill="x", pady=(6, 0))
        else:
            self._rod_info.pack_forget()
            self._rod_extra.pack_forget()
        txt = self._badge.cget("text")
        if aberta and txt: self._badge.pack(fill="x", padx=6, pady=(4, 0))
        elif not aberta:   self._badge.pack_forget()

    # ── Navegação ─────────────────────────────────────────────────────────────
    def _ir_inicial(self, chave):
        self._pagina_atual = chave
        self.pages[chave].pack(fill="both", expand=True)
        self._nav_selecionar(chave)
        self._lbl_titulo.config(text=self._titulo(chave))

    def ir(self, chave):
        if chave not in self.pages: return
        if self._pagina_atual: self.pages[self._pagina_atual].pack_forget()
        self._pagina_atual = chave
        self.pages[chave].pack(fill="both", expand=True)
        self._nav_selecionar(chave)
        self._lbl_titulo.config(text=self._titulo(chave))
        if hasattr(self.pages[chave], "refresh"): self.pages[chave].refresh()
        if not self._sb_fixada: self._animar(SB_FECHADA)

    def _titulo(self, chave):
        return {"dashboard":"Dashboard","produtos":"Produtos","entradas":"Entradas",
                "saidas":"Saídas","historico":"Histórico","alertas":"Alertas",
                "definicoes":"Definições","utilizadores":"Utilizadores"}.get(chave, chave)

    # ── Badge ─────────────────────────────────────────────────────────────────
    def set_badge(self, n):
        if n > 0:
            self._badge.config(text=f" ⚠ {n} alerta{'s' if n>1 else ''} ")
            if self._sb_aberta or self._sb_fixada:
                self._badge.pack(fill="x", padx=6, pady=(4, 0))
        else:
            self._badge.pack_forget()

    # ── Logout ────────────────────────────────────────────────────────────────
    def _logout(self):
        self._a_monitorizar = False
        self._utilizador    = None
        self._pagina_atual  = None
        # Mostrar boas-vindas por baixo e login por cima — sem fechar a janela
        self._mostrar_boas_vindas()
        self._mostrar_login()

    # ── Backup ────────────────────────────────────────────────────────────────
    def _backup(self):
        from tkinter import filedialog
        d = db.get_db()
        if not d.conn or not d.conn.is_connected():
            toast(self, "BD não ligada!", "error"); return
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".sql", filetypes=[("SQL","*.sql"),("Todos","*.*")],
            initialfile=f"stockpro_backup_{ts}.sql")
        if not path: return
        try:
            linhas = [f"-- StockPro Backup {datetime.now():%d/%m/%Y %H:%M:%S}",
                      f"-- BD: {db.DB_CONFIG['database']}", "",
                      "SET FOREIGN_KEY_CHECKS=0;", ""]
            for tab in ["categorias","departamentos","produtos","movimentos","app_utilizadores"]:
                rows = d.all(f"SELECT * FROM {tab}")
                linhas += [f"-- {tab} ({len(rows)} registos)", f"DELETE FROM `{tab}`;"]
                for row in rows:
                    cols = ", ".join(f"`{c}`" for c in row.keys())
                    vals = []
                    for v in row.values():
                        if v is None: vals.append("NULL")
                        elif isinstance(v, (int, float)): vals.append(str(v))
                        else: vals.append(f"'{str(v).replace(chr(39), chr(39)*2)}'")
                    linhas.append(f"INSERT INTO `{tab}` ({cols}) VALUES ({', '.join(vals)});")
                linhas.append("")
            linhas += ["SET FOREIGN_KEY_CHECKS=1;", "-- Fim"]
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(linhas))
            toast(self, "Backup guardado!")
        except Exception as e:
            toast(self, f"Erro: {e}", "error")

    # ── Relógio + aviso inatividade ───────────────────────────────────────────
    def _tick(self):
        try:
            if self._lbl_hora.winfo_exists():
                self._lbl_hora.config(text=datetime.now().strftime("%d/%m  %H:%M:%S"))
            if self._lbl_inativ.winfo_exists() and self._a_monitorizar and not self._bloqueado:
                restam = max(0, TIMEOUT_SEGUNDOS - self._inatividade)
                if restam <= 15:
                    self._lbl_inativ.config(
                        text=f"🔒 Bloqueia em {restam}s",
                        fg=C["yellow"] if restam > 5 else C["red"])
                else:
                    self._lbl_inativ.config(text="")
        except Exception: pass
        self.after(1000, self._tick)

    def on_close(self):
        db.get_db().disconnect()
        self.destroy()
