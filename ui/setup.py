"""
StockPro – Assistente de configuração MySQL (primeira execução)
"""
import tkinter as tk
import threading
from ui.tema import C, Btn, FormLabel, Entrada


class SetupWizard(tk.Toplevel):
    def __init__(self, parent, cfg: dict, ao_guardar):
        super().__init__(parent)
        self.title("StockPro – Configuração da Base de Dados")
        self.resizable(False, False)
        self.config(bg=C["bg"])
        self.attributes("-topmost", True)
        self._cfg       = cfg
        self._ao_guardar = ao_guardar
        self._build()
        self._centrar()
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.after(50, self._safe_grab)

    def _safe_grab(self):
        try: self.grab_set()
        except Exception: self.after(100, self._safe_grab)

    def _centrar(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h   = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        f = tk.Frame(self, bg=C["bg"], padx=40, pady=30)
        f.pack()

        tk.Label(f, text="StockPro", bg=C["bg"], fg=C["accent"],
                 font=("Consolas", 22, "bold")).pack()
        tk.Label(f, text="CONFIGURAÇÃO INICIAL", bg=C["bg"], fg=C["text3"],
                 font=("Segoe UI", 8, "bold")).pack(pady=(0, 24))
        tk.Label(f, text="Ligação ao servidor MySQL",
                 bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(f,
                 text="Introduza as credenciais do seu servidor MySQL.\n"
                      "Serão guardadas em ~/.config/stockpro/config.json",
                 bg=C["bg"], fg=C["text2"],
                 font=("Segoe UI", 9), justify="left").pack(anchor="w", pady=(4, 18))

        # Host + Porta
        row = tk.Frame(f, bg=C["bg"]); row.pack(fill="x", pady=(0, 10))
        lf  = tk.Frame(row, bg=C["bg"]); lf.pack(side="left", fill="x", expand=True, padx=(0, 8))
        rf  = tk.Frame(row, bg=C["bg"]); rf.pack(side="left", fill="x", expand=True)

        FormLabel(lf, "Host", bg=C["bg"]).pack(anchor="w", pady=(0, 3))
        self._host = Entrada(lf, placeholder="localhost")
        self._host.pack(fill="x", ipady=6)
        self._host.set(self._cfg.get("host", "localhost"))

        FormLabel(rf, "Porta", bg=C["bg"]).pack(anchor="w", pady=(0, 3))
        self._port = Entrada(rf, placeholder="3306")
        self._port.pack(fill="x", ipady=6)
        self._port.set(str(self._cfg.get("port", 3306)))

        FormLabel(f, "Utilizador MySQL", bg=C["bg"]).pack(anchor="w", pady=(0, 3))
        self._user = Entrada(f, placeholder="Ex: root")
        self._user.pack(fill="x", ipady=6, pady=(0, 10))
        self._user.set(self._cfg.get("user", ""))

        FormLabel(f, "Password MySQL", bg=C["bg"]).pack(anchor="w", pady=(0, 3))
        self._pw = Entrada(f, placeholder="Password do utilizador MySQL", password=True)
        self._pw.pack(fill="x", ipady=6, pady=(0, 10))

        FormLabel(f, "Nome da Base de Dados", bg=C["bg"]).pack(anchor="w", pady=(0, 3))
        self._db = Entrada(f, placeholder="stockpro")
        self._db.pack(fill="x", ipady=6, pady=(0, 20))
        self._db.set(self._cfg.get("database", "stockpro"))

        self._status = tk.Label(f, text="", bg=C["bg"], fg=C["text2"],
                                font=("Segoe UI", 9))
        self._status.pack(pady=(0, 12))

        row2 = tk.Frame(f, bg=C["bg"]); row2.pack(fill="x")
        Btn(row2, "Testar Ligação", cmd=self._testar, estilo="ghost").pack(side="left", padx=(0, 10))
        self._btn_ok = Btn(row2, "Guardar e Continuar", cmd=self._guardar, estilo="primary")
        self._btn_ok.pack(side="left")
        self._btn_ok.config(state="disabled")

    def _testar(self):
        self._status.config(text="A testar…", fg=C["text2"])
        self.update()
        cfg = self._ler()
        threading.Thread(target=self._testar_async, args=(cfg,), daemon=True).start()

    def _testar_async(self, cfg):
        try:
            import mysql.connector
            c = mysql.connector.connect(
                host=cfg["host"], port=cfg["port"],
                user=cfg["user"], password=cfg["password"])
            c.close()
            self.after(0, lambda: self._resultado(True, "Ligação estabelecida com sucesso!"))
        except Exception as e:
            msg = str(e)
            self.after(0, lambda m=msg: self._resultado(False, m))

    def _resultado(self, ok, msg):
        self._status.config(
            text=f"{'✔' if ok else '✖'}  {msg}",
            fg=C["green"] if ok else C["red"])
        self._btn_ok.config(state="normal" if ok else "disabled")

    def _ler(self):
        return {
            "host":     self._host.val().strip() or "localhost",
            "port":     int(self._port.val().strip() or 3306),
            "user":     self._user.val().strip(),
            "password": self._pw.val().strip(),
            "database": self._db.val().strip() or "stockpro",
            "charset":  "utf8mb4",
        }

    def _guardar(self):
        import config
        cfg = self._ler()
        config.guardar(cfg)
        self.grab_release()
        self.destroy()
        self._ao_guardar(cfg)  # chamar APÓS destroy para não bloquear
