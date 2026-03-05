"""
StockPro – Ecrã de bloqueio por inatividade
"""
import tkinter as tk
from ui.tema import C, Btn, FormLabel, Entrada
import db.database as db

TIMEOUT_SEGUNDOS = 60  # 1 minuto


class EcraBloqueio(tk.Toplevel):
    def __init__(self, parent, utilizador, ao_desbloquear):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg=C["bg"])
        self._parent         = parent
        self._utilizador     = utilizador
        self._ao_desbloquear = ao_desbloquear
        self._build()
        self._cobrir()
        self.after(50, self._safe_grab)
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
        fundo = tk.Frame(self, bg=C["bg"]); fundo.pack(fill="both", expand=True)

        topbar = tk.Frame(fundo, bg=C["bg2"], height=52,
                          highlightthickness=1, highlightbackground=C["border"])
        topbar.pack(fill="x"); topbar.pack_propagate(False)
        tk.Label(topbar, text="StockPro", bg=C["bg2"], fg=C["accent"],
                 font=("Consolas", 15, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(topbar, text="by HCsoftware", bg=C["bg2"], fg=C["text3"],
                 font=("Segoe UI", 8)).pack(side="left")

        centro = tk.Frame(fundo, bg=C["bg"])
        centro.place(relx=.5, rely=.5, anchor="center")

        tk.Label(centro, text="🔒", bg=C["bg"], font=("Segoe UI", 48)).pack(pady=(0, 8))
        tk.Label(centro, text="Sessão Bloqueada", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 20, "bold")).pack()
        tk.Label(centro,
                 text=f"Utilizador:  {self._utilizador.get('nome', '')}\n"
                      "Introduza a password para continuar.",
                 bg=C["bg"], fg=C["text2"],
                 font=("Segoe UI", 10), justify="center").pack(pady=(6, 22))

        card = tk.Frame(centro, bg=C["bg2"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(ipadx=30, ipady=20)

        FormLabel(card, "Password", bg=C["bg2"]).pack(anchor="w", padx=20, pady=(0, 4))
        self._e_pw = Entrada(card, password=True)
        self._e_pw.pack(fill="x", padx=20, ipady=7, pady=(0, 4))
        self._e_pw.bind("<Return>", lambda _: self._tentar())
        self._e_pw.focus_set()

        self._erro = tk.Label(card, text="", bg=C["bg2"], fg=C["red"], font=("Segoe UI", 9))
        self._erro.pack(pady=(0, 4))
        Btn(card, "Desbloquear", cmd=self._tentar,
            estilo="primary", icone="🔓").pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(centro, text="Não é você?", bg=C["bg"], fg=C["text3"],
                 font=("Segoe UI", 8)).pack(pady=(14, 2))
        lnk = tk.Label(centro,
                       text="Terminar sessão e iniciar com outro utilizador",
                       bg=C["bg"], fg=C["accent"],
                       font=("Segoe UI", 8), cursor="hand2")
        lnk.pack()
        lnk.bind("<Button-1>", lambda _: self._terminar_sessao())

    def _tentar(self):
        pw = self._e_pw.get().strip()
        if not pw:
            self._erro.config(text="Introduza a password."); return
        u = db.util_autenticar(self._utilizador.get("username", ""), pw)
        if u:
            self.grab_release()
            self._ao_desbloquear()
            try:
                self.destroy()
            except Exception:
                pass
        else:
            self._erro.config(text="Password incorreta. Tente novamente.")
            self._e_pw.delete(0, "end")

    def _terminar_sessao(self):
        self.grab_release()
        self._ao_desbloquear(logout=True)
        try:
            self.destroy()
        except Exception:
            pass
