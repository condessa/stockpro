"""StockPro – Gestão de Utilizadores (só admin)"""
import tkinter as tk
from ui.tema import C, Card, Btn, FormLabel, Entrada, Combo, Tabela, toast, DialogoConfirmar
import db.database as db


class Utilizadores(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app      = app
        self._edit_id = None
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg"]); hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="Utilizadores", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        Btn(hdr, "Novo Utilizador", cmd=self._novo, estilo="primary", icone="+").pack(side="right")

        pane = tk.Frame(self, bg=C["bg"]); pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=1); pane.columnconfigure(1, weight=0); pane.rowconfigure(0, weight=1)

        # Tabela
        esq = Card(pane); esq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._tbl = Tabela(esq, altura=16, colunas=[
            {"id": "nome",   "label": "Nome",         "w": 200, "s": True},
            {"id": "user",   "label": "Utilizador",   "w": 140},
            {"id": "role",   "label": "Perfil",       "w": 90,  "anc": "center"},
            {"id": "estado", "label": "Estado",       "w": 80,  "anc": "center"},
            {"id": "ultimo", "label": "Último Login", "w": 150},
            {"id": "criado", "label": "Criado em",    "w": 140},
        ])
        self._tbl.pack(fill="both", expand=True, padx=8, pady=(10, 6))
        self._tbl.duplo_clique(lambda _: self._editar())
        act = tk.Frame(esq, bg=C["bg2"]); act.pack(fill="x", padx=10, pady=(0, 6))
        Btn(act, "Editar",           cmd=self._editar,    estilo="ghost",   icone="✏").pack(side="left", padx=(0, 6))
        Btn(act, "Alterar Password", cmd=self._alt_pw,    estilo="neutral", icone="🔑").pack(side="left", padx=(0, 6))
        Btn(act, "Desativar",        cmd=self._desativar, estilo="danger",  icone="🚫").pack(side="left", padx=(0, 6))
        Btn(act, "Eliminar",         cmd=self._eliminar,  estilo="danger",  icone="🗑").pack(side="left")

        # Formulário
        self._frm = Card(pane); self._frm.grid(row=0, column=1, sticky="nsew")
        self._frm.config(width=300); self._frm.pack_propagate(False)
        inn = tk.Frame(self._frm, bg=C["bg2"]); inn.pack(fill="both", expand=True, padx=16, pady=14)

        self._titulo = tk.Label(inn, text="Novo Utilizador", bg=C["bg2"], fg=C["text"],
                                font=("Segoe UI", 13, "bold"))
        self._titulo.pack(anchor="w", pady=(0, 8))

        FormLabel(inn, "Nome completo *").pack(anchor="w", pady=(0, 3))
        self._e_nome = Entrada(inn, placeholder="Ex: João Silva")
        self._e_nome.pack(fill="x", ipady=6, pady=(0, 6))

        FormLabel(inn, "Utilizador *").pack(anchor="w", pady=(0, 3))
        self._e_user = Entrada(inn, placeholder="sem espaços")
        self._e_user.pack(fill="x", ipady=6, pady=(0, 6))

        self._frm_pw = tk.Frame(inn, bg=C["bg2"]); self._frm_pw.pack(fill="x", pady=(0, 6))
        FormLabel(self._frm_pw, "Password *").pack(anchor="w", pady=(0, 3))
        self._e_pw = Entrada(self._frm_pw, placeholder="mínimo 4 caracteres", password=True)
        self._e_pw.pack(fill="x", ipady=6, pady=(0, 6))
        FormLabel(self._frm_pw, "Confirmar *").pack(anchor="w", pady=(0, 3))
        self._e_pw2 = Entrada(self._frm_pw, placeholder="repetir", password=True)
        self._e_pw2.pack(fill="x", ipady=6)

        FormLabel(inn, "Perfil").pack(anchor="w", pady=(10, 3))
        self._e_role = Combo(inn, valores=["operador","admin"], width=18)
        self._e_role.set("operador"); self._e_role.pack(anchor="w", pady=(0, 6))

        self._var_ativo = tk.BooleanVar(value=True)
        tk.Checkbutton(inn, text="Conta ativa", variable=self._var_ativo,
                       bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                       activebackground=C["bg2"],
                       font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))

        btns = tk.Frame(inn, bg=C["bg2"]); btns.pack(fill="x")
        Btn(btns, "Cancelar", cmd=self._limpar, estilo="ghost").pack(side="left", padx=(0, 8))
        Btn(btns, "Guardar",  cmd=self._guardar, estilo="primary", icone="💾").pack(side="left")

    def _novo(self):
        self._limpar(); self._e_nome.focus()

    def _limpar(self):
        self._edit_id = None
        self._titulo.config(text="Novo Utilizador")
        self._e_user.config(state="normal")
        self._e_nome.set(""); self._e_user.set("")
        self._e_pw.delete(0,"end"); self._e_pw2.delete(0,"end")
        self._e_role.set("operador"); self._var_ativo.set(True)
        self._frm_pw.pack(fill="x", pady=(0, 6))

    def _guardar(self):
        nome  = self._e_nome.val().strip()
        uname = self._e_user.val().strip().lower().replace(" ","")
        role  = self._e_role.get()
        ativo = self._var_ativo.get()
        if not nome or not uname: toast(self, "Nome e utilizador obrigatórios!", "error"); return
        try:
            if self._edit_id:
                if not ativo or role != "admin":
                    u = db._db.one("SELECT role FROM app_utilizadores WHERE id=%s", (self._edit_id,))
                    if u and u["role"] == "admin" and db.util_contar_admins() <= 1:
                        toast(self, "Não pode remover o último administrador!", "error"); return
                db.util_atualizar(self._edit_id, nome, role, int(ativo))
                toast(self, f"'{uname}' atualizado!")
            else:
                pw  = self._e_pw.get()
                pw2 = self._e_pw2.get()
                if not pw: toast(self, "Password obrigatória!", "error"); return
                if pw != pw2: toast(self, "Passwords não coincidem!", "error"); return
                if len(pw) < 4: toast(self, "Password demasiado curta!", "error"); return
                db.util_criar(uname, nome, pw, role)
                toast(self, f"Utilizador '{uname}' criado!")
            self._limpar(); self.refresh()
        except Exception as e:
            toast(self, f"{'Utilizador já existe!' if 'Duplicate' in str(e) else e}", "error")

    def _editar(self):
        v = self._tbl.selecionado()
        if not v: toast(self, "Selecione um utilizador!", "warning"); return
        todos = db.util_listar()
        u = next((x for x in todos if x["username"] == v[1]), None)
        if not u: return
        self._edit_id = u["id"]
        self._titulo.config(text="Editar Utilizador")
        self._e_nome.set(u["nome"])
        self._e_user.config(state="normal"); self._e_user.set(u["username"]); self._e_user.config(state="disabled")
        self._e_role.set(u["role"]); self._var_ativo.set(bool(u["ativo"]))
        self._frm_pw.pack_forget()

    def _alt_pw(self):
        v = self._tbl.selecionado()
        if not v: toast(self, "Selecione um utilizador!", "warning"); return
        todos = db.util_listar()
        u = next((x for x in todos if x["username"] == v[1]), None)
        if u: _DialogoAltPW(self, u); self.refresh()

    def _desativar(self):
        v = self._tbl.selecionado()
        if not v: toast(self, "Selecione um utilizador!", "warning"); return
        todos = db.util_listar()
        u = next((x for x in todos if x["username"] == v[1]), None)
        if not u: return
        if u["role"] == "admin" and db.util_contar_admins() <= 1:
            toast(self, "Não pode desativar o último administrador!", "error"); return
        d = DialogoConfirmar(self, "Desativar", f"Desativar '{u['nome']}'?")
        if d.resultado:
            db.util_desativar(u["id"]); toast(self, "Desativado!", "warning"); self.refresh()


    def _eliminar(self):
        v = self._tbl.selecionado()
        if not v: toast(self, "Selecione um utilizador!", "warning"); return
        todos = db.util_listar()
        u = next((x for x in todos if x["username"] == v[1]), None)
        if not u: return
        if u["role"] == "admin" and db.util_contar_admins() <= 1:
            toast(self, "Não pode eliminar o último administrador!", "error"); return
        # Verificar se é o utilizador atual
        if self.app._utilizador and self.app._utilizador.get("id") == u["id"]:
            toast(self, "Não pode eliminar a sua própria conta!", "error"); return
        # Primeira confirmação
        d1 = DialogoConfirmar(self, "Eliminar Utilizador",
            f"Tem a certeza que quer eliminar permanentemente\n'{u['nome']} ({u['username']})'?\n\nEsta ação não pode ser desfeita.")
        if not d1.resultado: return
        # Segunda confirmação
        d2 = DialogoConfirmar(self, "Confirmar Eliminação",
            f"ATENÇÃO: O utilizador '{u['username']}'\nserá removido definitivamente.\n\nConfirma?")
        if not d2.resultado: return
        try:
            db.util_eliminar(u["id"])
            toast(self, f"Utilizador '{u['username']}' eliminado.", "warning")
            self._limpar(); self.refresh()
        except Exception as e:
            toast(self, f"Erro: {e}", "error")

    def refresh(self, _=None):
        self._tbl.limpar()
        for i, u in enumerate(db.util_listar()):
            tag    = "even" if i%2==0 else "odd"
            estado = "Ativo" if u["ativo"] else "Inativo"
            role   = "Admin" if u["role"]=="admin" else "Operador"
            ul     = str(u["ultimo_login"])[:16] if u["ultimo_login"] else "-"
            cr     = str(u["criado_em"])[:16]    if u["criado_em"]    else "-"
            self._tbl.linha((u["nome"],u["username"],role,estado,ul,cr), tag)


class _DialogoAltPW(tk.Toplevel):
    def __init__(self, parent, u):
        super().__init__(parent)
        self.title(f"Password – {u['username']}")
        self.resizable(False, False); self.config(bg=C["bg"])
        self.grab_set(); self._uid = u["id"]; self._parent = parent
        f = tk.Frame(self, bg=C["bg"], padx=30, pady=24); f.pack()
        tk.Label(f, text=f"Alterar password de '{u['username']}'",
                 bg=C["bg"], fg=C["text"], font=("Segoe UI", 11, "bold")).pack(pady=(0, 16))
        FormLabel(f, "Nova Password *", bg=C["bg"]).pack(anchor="w", pady=(0, 3))
        self._pw = Entrada(f, placeholder="mínimo 4 caracteres", password=True)
        self._pw.pack(fill="x", ipady=6, pady=(0, 6))
        FormLabel(f, "Confirmar *", bg=C["bg"]).pack(anchor="w", pady=(0, 3))
        self._pw2 = Entrada(f, placeholder="repetir", password=True)
        self._pw2.pack(fill="x", ipady=6, pady=(0, 6))
        self._pw2.bind("<Return>", lambda _: self._ok())
        self._erro = tk.Label(f, text="", bg=C["bg"], fg=C["red"], font=("Segoe UI", 9))
        self._erro.pack(pady=(0, 8))
        row = tk.Frame(f, bg=C["bg"]); row.pack(fill="x")
        Btn(row, "Cancelar", cmd=self.destroy, estilo="ghost").pack(side="left", padx=(0, 8))
        Btn(row, "Confirmar", cmd=self._ok, estilo="primary").pack(side="left")
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-self.winfo_width())//2}+{(sh-self.winfo_height())//2}")
        self.wait_window()

    def _ok(self):
        pw = self._pw.get(); pw2 = self._pw2.get()
        if not pw: self._erro.config(text="Password obrigatória."); return
        if pw != pw2: self._erro.config(text="Não coincidem."); return
        if len(pw) < 4: self._erro.config(text="Mínimo 4 caracteres."); return
        db.util_alterar_password(self._uid, pw)
        toast(self._parent, "Password alterada!")
        self.destroy()
