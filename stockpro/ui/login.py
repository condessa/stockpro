"""
StockPro – Ecrã de Login (overlay sobre a janela principal)
"""
import tkinter as tk
from tkinter import messagebox
from ui.tema import C, Btn, FormLabel, Entrada, Combo
import db.database as db


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, ao_login):
        super().__init__(parent)
        self.overrideredirect(True)          # sem barra de título — overlay puro
        self.attributes("-topmost", True)
        self.config(bg=C["bg"])
        self._parent    = parent
        self._ao_login  = ao_login
        self._primeiro  = not db.util_existe_algum()
        self._build()
        self._cobrir()
        self.after(50, self._safe_grab)
        # Reposicionar se a janela pai se mover
        parent.bind("<Configure>", self._cobrir, add="+")

    def _cobrir(self, _=None):
        self.update_idletasks()
        self.geometry(
            f"{self._parent.winfo_width()}x{self._parent.winfo_height()}"
            f"+{self._parent.winfo_rootx()}+{self._parent.winfo_rooty()}"
        )

    def _safe_grab(self):
        try: self.grab_set()
        except Exception: self.after(100, self._safe_grab)

    def _build(self):
        # Fundo semitransparente com o logo em cima
        fundo = tk.Frame(self, bg=C["bg"]); fundo.pack(fill="both", expand=True)

        # Topo decorativo igual à janela principal
        topbar = tk.Frame(fundo, bg=C["bg2"], height=52,
                          highlightthickness=1, highlightbackground=C["border"])
        topbar.pack(fill="x"); topbar.pack_propagate(False)
        tk.Label(topbar, text="StockPro", bg=C["bg2"], fg=C["accent"],
                 font=("Consolas", 15, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(topbar, text="by HCsoftware", bg=C["bg2"], fg=C["text3"],
                 font=("Segoe UI", 8)).pack(side="left")

        # Card central de login
        centro = tk.Frame(fundo, bg=C["bg"])
        centro.place(relx=.5, rely=.5, anchor="center")

        card = tk.Frame(centro, bg=C["bg2"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(ipadx=40, ipady=30)

        tk.Label(card, text="🏭", bg=C["bg2"], font=("Segoe UI", 32)).pack(pady=(20, 0))
        tk.Label(card, text="StockPro", bg=C["bg2"], fg=C["accent"],
                 font=("Consolas", 20, "bold")).pack()
        tk.Label(card, text="GESTÃO DE STOCKS", bg=C["bg2"], fg=C["text3"],
                 font=("Segoe UI", 8, "bold")).pack(pady=(0, 20))

        # Tabs
        tabs = tk.Frame(card, bg=C["bg2"]); tabs.pack(fill="x", padx=30, pady=(0, 16))
        self._tab_login = tk.Label(tabs, text="Entrar",
            bg=C["accent"], fg=C["white"],
            font=("Segoe UI", 10, "bold"), padx=20, pady=7, cursor="hand2")
        self._tab_login.pack(side="left")
        self._tab_login.bind("<Button-1>", lambda _: self._aba("login"))
        self._tab_reg = tk.Label(tabs, text="Novo Utilizador",
            bg=C["bg3"], fg=C["text2"],
            font=("Segoe UI", 10), padx=20, pady=7, cursor="hand2")
        self._tab_reg.pack(side="left", padx=(2, 0))
        self._tab_reg.bind("<Button-1>", lambda _: self._aba("reg"))

        if self._primeiro:
            tk.Label(card,
                text="  Primeiro acesso — crie o administrador.",
                bg=C["yellow_bg"], fg=C["yellow"],
                font=("Segoe UI", 9), pady=8, justify="left").pack(fill="x", padx=30, pady=(0, 10))

        # Painéis
        self._pnl_login = tk.Frame(card, bg=C["bg2"])
        self._build_login(self._pnl_login)
        self._pnl_reg = tk.Frame(card, bg=C["bg2"])
        self._build_reg(self._pnl_reg)

        self._aba("reg" if self._primeiro else "login")

    def _build_login(self, p):
        p.config(padx=30)
        FormLabel(p, "Utilizador", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._l_user = Entrada(p, placeholder="nome de utilizador")
        self._l_user.pack(fill="x", ipady=7, pady=(0, 10))
        self._l_user.bind("<Return>", lambda _: self._l_pw.focus())

        FormLabel(p, "Password", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._l_pw = Entrada(p, placeholder="password", password=True)
        self._l_pw.pack(fill="x", ipady=7, pady=(0, 14))
        self._l_pw.bind("<Return>", lambda _: self._login())

        self._l_erro = tk.Label(p, text="", bg=C["bg2"], fg=C["red"], font=("Segoe UI", 9))
        self._l_erro.pack(pady=(0, 8))
        Btn(p, "Entrar", cmd=self._login, estilo="primary", icone="→").pack(fill="x", pady=(0, 20))

    def _build_reg(self, p):
        p.config(padx=30)
        FormLabel(p, "Nome completo", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._r_nome = Entrada(p, placeholder="Ex: João Silva")
        self._r_nome.pack(fill="x", ipady=7, pady=(0, 8))

        FormLabel(p, "Utilizador (login)", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._r_user = Entrada(p, placeholder="sem espaços, ex: joao.silva")
        self._r_user.pack(fill="x", ipady=7, pady=(0, 8))

        FormLabel(p, "Password", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._r_pw = Entrada(p, placeholder="mínimo 4 caracteres", password=True)
        self._r_pw.pack(fill="x", ipady=7, pady=(0, 8))

        FormLabel(p, "Confirmar Password", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._r_pw2 = Entrada(p, placeholder="repetir password", password=True)
        self._r_pw2.pack(fill="x", ipady=7, pady=(0, 8))

        FormLabel(p, "Perfil", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._r_role = Combo(p, valores=["operador", "admin"], width=18)
        self._r_role.set("admin" if self._primeiro else "operador")
        self._r_role.pack(anchor="w", pady=(0, 4))
        if self._primeiro:
            self._r_role.config(state="disabled")

        self._r_erro = tk.Label(p, text="", bg=C["bg2"], fg=C["red"],
                                font=("Segoe UI", 9), wraplength=300)
        self._r_erro.pack(pady=(8, 4))
        Btn(p, "Criar Utilizador", cmd=self._registar,
            estilo="success", icone="+").pack(fill="x", pady=(0, 20))

    def _aba(self, aba):
        self._pnl_login.pack_forget()
        self._pnl_reg.pack_forget()
        if aba == "login":
            self._tab_login.config(bg=C["accent"], fg=C["white"], font=("Segoe UI", 10, "bold"))
            self._tab_reg.config(  bg=C["bg3"],    fg=C["text2"], font=("Segoe UI", 10))
            self._pnl_login.pack(fill="x")
        else:
            self._tab_reg.config(  bg=C["accent"], fg=C["white"], font=("Segoe UI", 10, "bold"))
            self._tab_login.config(bg=C["bg3"],    fg=C["text2"], font=("Segoe UI", 10))
            self._pnl_reg.pack(fill="x")
        self.update_idletasks()

    def _login(self):
        u = db.util_autenticar(self._l_user.val(), self._l_pw.val())
        if u:
            self.grab_release()
            self._parent.unbind("<Configure>")
            # Chamar ao_login ANTES de destroy para a janela principal
            # reconstruir a UI sem perda de foco
            self._ao_login(u)
            try:
                self.destroy()
            except Exception:
                pass
        else:
            self._l_erro.config(text="Utilizador ou password incorretos.")
            self._l_pw.delete(0, "end")

    def _registar(self):
        nome  = self._r_nome.val().strip()
        uname = self._r_user.val().strip().lower().replace(" ", "")
        pw    = self._r_pw.val().strip()
        pw2   = self._r_pw2.val().strip()
        role  = "admin" if self._primeiro else self._r_role.get()

        if not nome or not uname or not pw:
            self._r_erro.config(text="Preencha todos os campos."); return
        if pw != pw2:
            self._r_erro.config(text="As passwords não coincidem."); return
        if len(pw) < 4:
            self._r_erro.config(text="Password demasiado curta (mín. 4)."); return

        if not self._primeiro:
            # Mostrar diálogo de autorização com callback — sem wait_window
            _DialogoAdminAuth(self,
                ao_autorizar=lambda: self._criar_utilizador(uname, nome, pw, role),
                ao_cancelar=lambda: self._r_erro.config(text="Autorização cancelada."))
            return

        self._criar_utilizador(uname, nome, pw, role)

    def _criar_utilizador(self, uname, nome, pw, role):
        try:
            db.util_criar(uname, nome, pw, role)
            if self._primeiro:
                # Primeiro utilizador — login automático
                u = db.util_autenticar(uname, pw)
                if u:
                    self.grab_release()
                    self._parent.unbind("<Configure>")
                    self.destroy()
                    self._ao_login(u)
                    return
            else:
                messagebox.showinfo("Conta criada", f"Utilizador '{uname}' criado com sucesso!")
                self._aba("login")
                self._l_user.set(uname)
        except Exception as e:
            self._r_erro.config(text=f"Utilizador '{uname}' já existe!" if "Duplicate" in str(e) else str(e))


class _DialogoAdminAuth(tk.Toplevel):
    def __init__(self, parent, ao_autorizar, ao_cancelar=None):
        super().__init__(parent)
        self.resizable(False, False)
        self.config(bg=C["bg2"],
                    highlightthickness=1,
                    highlightbackground=C["accent"])
        self.attributes("-topmost", True)
        self._ao_autorizar = ao_autorizar
        self._ao_cancelar  = ao_cancelar
        self._build()
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-self.winfo_width())//2}+{(sh-self.winfo_height())//2}")
        self.protocol("WM_DELETE_WINDOW", self._cancelar)

    def _build(self):
        f = tk.Frame(self, bg=C["bg2"], padx=30, pady=24); f.pack()
        tk.Label(f, text="🔐  Autorização necessária", bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(pady=(0, 8))
        tk.Label(f, text="Para criar um utilizador é necessária\na confirmação de um Administrador.",
                 bg=C["bg2"], fg=C["text2"], font=("Segoe UI", 9), justify="center").pack(pady=(0, 16))
        FormLabel(f, "Admin – Utilizador", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._user = Entrada(f, placeholder="username do admin")
        self._user.pack(fill="x", ipady=6, pady=(0, 10))
        self._user.focus_set()
        FormLabel(f, "Admin – Password", bg=C["bg2"]).pack(anchor="w", pady=(0, 3))
        self._pw = Entrada(f, placeholder="password do admin", password=True)
        self._pw.pack(fill="x", ipady=6, pady=(0, 10))
        self._pw.bind("<Return>", lambda _: self._confirmar())
        self._erro = tk.Label(f, text="", bg=C["bg2"], fg=C["red"], font=("Segoe UI", 9))
        self._erro.pack(pady=(0, 8))
        row = tk.Frame(f, bg=C["bg2"]); row.pack(fill="x")
        Btn(row, "Cancelar",  cmd=self._cancelar,  estilo="ghost").pack(side="left", padx=(0, 8))
        Btn(row, "Autorizar", cmd=self._confirmar, estilo="primary").pack(side="left")

    def _cancelar(self):
        self.destroy()
        if self._ao_cancelar: self._ao_cancelar()

    def _confirmar(self):
        u = db.util_autenticar(self._user.val(), self._pw.val())
        if u and u["role"] == "admin":
            self.destroy()
            self._ao_autorizar()
        else:
            self._erro.config(text="Credenciais inválidas ou sem perfil admin.")
