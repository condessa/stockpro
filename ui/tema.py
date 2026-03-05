"""
StockPro – Tema, cores e widgets reutilizáveis
"""
import tkinter as tk
from tkinter import ttk

C = {
    "bg":        "#0f1117",
    "bg2":       "#161b27",
    "bg3":       "#1e2235",
    "bg4":       "#252a3d",
    "border":    "#2e3450",
    "accent":    "#4f7ef7",
    "accent_h":  "#3d6af5",
    "green":     "#22c55e",
    "green_bg":  "#0d2e1a",
    "yellow":    "#f59e0b",
    "yellow_bg": "#2d2005",
    "red":       "#ef4444",
    "red_bg":    "#2d0f0f",
    "text":      "#e2e8f0",
    "text2":     "#8892b0",
    "text3":     "#4a5578",
    "white":     "#ffffff",
    "row_even":  "#161b27",
    "row_odd":   "#131720",
    "row_sel":   "#1e2d50",
    "hover":     "#1e2235",
    "entrada_bg":"#0d2e1a",
    "saida_bg":  "#2d0f0f",
}


def aplicar_estilo():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("T.Treeview",
        background=C["bg2"], foreground=C["text"],
        fieldbackground=C["bg2"], borderwidth=0,
        rowheight=22, font=("Segoe UI", 9))
    s.configure("T.Treeview.Heading",
        background=C["bg3"], foreground=C["text2"],
        relief="flat", font=("Segoe UI", 8, "bold"), borderwidth=0)
    s.map("T.Treeview",
        background=[("selected", C["row_sel"])],
        foreground=[("selected", C["white"])])
    s.map("T.Treeview.Heading",
        background=[("active", C["bg4"])])
    try:
        s.configure("Vertical.TScrollbar",
            background=C["bg3"], troughcolor=C["bg2"],
            arrowcolor=C["text3"], borderwidth=0)
    except Exception:
        pass
    s.configure("D.TCombobox",
        fieldbackground=C["bg3"], background=C["bg3"],
        foreground=C["text"], arrowcolor=C["text2"],
        bordercolor=C["border"], relief="flat",
        selectbackground=C["bg4"], selectforeground=C["text"])
    s.map("D.TCombobox",
        fieldbackground=[("readonly", C["bg3"])],
        selectbackground=[("readonly", C["bg3"])],
        selectforeground=[("readonly", C["text"])])


# ── Widgets base ──────────────────────────────────────────────────────────────

class Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["bg2"],
                         highlightthickness=1,
                         highlightbackground=C["border"], **kw)


class Label(tk.Label):
    def __init__(self, parent, text, size=9, bold=False, color=None, bg=None, **kw):
        font = ("Segoe UI", size, "bold" if bold else "normal")
        super().__init__(parent, text=text,
                         bg=bg or C["bg2"],
                         fg=color or C["text"],
                         font=font, **kw)


class FormLabel(tk.Label):
    def __init__(self, parent, text, bg=None, **kw):
        super().__init__(parent, text=text,
                         bg=bg or C["bg2"], fg=C["text2"],
                         font=("Segoe UI", 8, "bold"), **kw)


class Entrada(tk.Entry):
    """Entry com placeholder."""
    def __init__(self, parent, placeholder="", password=False, mono=False, **kw):
        self._ph    = placeholder
        self._ph_on = False
        self._is_pw = password
        font = ("Consolas", 9) if mono else ("Segoe UI", 9)
        super().__init__(parent,
            bg=C["bg3"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=0, font=font,
            highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["accent"], **kw)
        if password:
            self.config(show="•")
        if placeholder:
            self._set_ph()
            self.bind("<FocusIn>",  self._in)
            self.bind("<FocusOut>", self._out)

    def _set_ph(self):
        self.delete(0, "end")
        self.config(show="", fg=C["text3"])
        self.insert(0, self._ph)
        self._ph_on = True

    def _in(self, _=None):
        if self._ph_on:
            self.delete(0, "end")
            if self._is_pw:
                self.config(show="•")
            self.config(fg=C["text"])
            self._ph_on = False

    def _out(self, _=None):
        if not tk.Entry.get(self) and self._ph:
            self._set_ph()

    def val(self):
        return "" if self._ph_on else tk.Entry.get(self)

    def set(self, v):
        self.delete(0, "end")
        self._ph_on = False
        if v:
            self.config(fg=C["text"])
            self.insert(0, str(v))
        elif self._ph:
            self._set_ph()


class Combo(ttk.Combobox):
    def __init__(self, parent, valores=(), **kw):
        super().__init__(parent, values=list(valores),
                         style="D.TCombobox",
                         font=("Segoe UI", 9),
                         state="readonly", **kw)
        self.option_add("*TCombobox*Listbox.background",       C["bg3"])
        self.option_add("*TCombobox*Listbox.foreground",       C["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", C["accent"])
        self.option_add("*TCombobox*Listbox.font",             ("Segoe UI", 9))


class Btn(tk.Button):
    _ESTILOS = {
        "primary": ("#4f7ef7", "#3d6af5", "#fff"),
        "success": ("#166534", "#14532d", "#22c55e"),
        "danger":  ("#7f1d1d", "#6b1b1b", "#ef4444"),
        "warning": ("#78350f", "#6b2d0a", "#f59e0b"),
        "ghost":   (C["bg3"],  C["bg4"],  C["text2"]),
        "neutral": (C["bg4"],  C["border"], C["text"]),
    }
    def __init__(self, parent, texto, cmd=None, estilo="primary", icone="", **kw):
        bg, abg, fg = self._ESTILOS.get(estilo, self._ESTILOS["primary"])
        label = f"{icone}  {texto}" if icone else texto
        super().__init__(parent, text=label, command=cmd,
            bg=bg, fg=fg, activebackground=abg, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=10, pady=4, **kw)
        self.bind("<Enter>", lambda _: self.config(bg=abg))
        self.bind("<Leave>", lambda _: self.config(bg=bg))


class CardStat(tk.Frame):
    def __init__(self, parent, titulo, valor="0", sub="", cor=None, **kw):
        cor = cor or C["accent"]
        super().__init__(parent, bg=C["bg2"],
                         highlightthickness=1,
                         highlightbackground=C["border"], **kw)
        tk.Frame(self, bg=cor, height=2).pack(fill="x")
        inner = tk.Frame(self, bg=C["bg2"])
        inner.pack(fill="both", expand=True, padx=12, pady=8)
        tk.Label(inner, text=titulo.upper(), bg=C["bg2"], fg=C["text3"],
                 font=("Segoe UI", 7, "bold")).pack(anchor="w")
        self._val = tk.Label(inner, text=valor, bg=C["bg2"], fg=C["text"],
                             font=("Segoe UI", 20, "bold"))
        self._val.pack(anchor="w", pady=(1, 0))
        tk.Label(inner, text=sub, bg=C["bg2"], fg=C["text2"],
                 font=("Segoe UI", 8)).pack(anchor="w")

    def atualizar(self, v):
        self._val.config(text=str(v))


class Tabela(tk.Frame):
    def __init__(self, parent, colunas, altura=14, **kw):
        super().__init__(parent, bg=C["bg2"], **kw)
        self.tree = ttk.Treeview(self,
            columns=[c["id"] for c in colunas],
            show="headings", style="T.Treeview", height=altura)
        self.tree.tag_configure("even",    background=C["row_even"])
        self.tree.tag_configure("odd",     background=C["row_odd"])
        self.tree.tag_configure("baixo",   background=C["yellow_bg"])
        self.tree.tag_configure("zero",    background=C["red_bg"])
        self.tree.tag_configure("entrada", background=C["entrada_bg"])
        self.tree.tag_configure("saida",   background=C["saida_bg"])
        for c in colunas:
            self.tree.heading(c["id"], text=c["label"],
                              anchor=c.get("anc", "w"))
            self.tree.column(c["id"],
                width=c.get("w", 120), minwidth=c.get("min", 40),
                anchor=c.get("anc", "w"), stretch=c.get("s", False))
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def limpar(self):
        self.tree.delete(*self.tree.get_children())

    def linha(self, valores, tag="even"):
        self.tree.insert("", "end", values=valores, tags=(tag,))

    def selecionado(self):
        sel = self.tree.selection()
        return self.tree.item(sel[0], "values") if sel else None

    def duplo_clique(self, fn):
        self.tree.bind("<Double-1>", fn)


class BarraPesquisa(tk.Frame):
    def __init__(self, parent, ao_mudar=None, ph="🔍  Pesquisar...", **kw):
        super().__init__(parent, bg=C["bg2"], **kw)
        self._e = Entrada(self, placeholder=ph)
        self._e.pack(fill="x", ipady=4, padx=1)
        if ao_mudar:
            self._e.bind("<KeyRelease>", lambda _: ao_mudar(self.val()))

    def val(self):
        return self._e.val()

    def set(self, txt=""):
        self._e.set(txt)


def toast(root, msg, tipo="success"):
    cores  = {"success": C["green"], "error": C["red"], "warning": C["yellow"]}
    icones = {"success": "✔", "error": "✖", "warning": "⚠"}
    cor = cores.get(tipo, C["text"])
    t = tk.Toplevel(root)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    t.config(bg=C["bg2"])
    outer = tk.Frame(t, bg=cor); outer.pack()
    inner = tk.Frame(outer, bg=C["bg2"]); inner.pack(padx=1, pady=1)
    tk.Frame(inner, bg=cor, width=4).pack(side="left", fill="y")
    tk.Label(inner,
             text=f"  {icones.get(tipo,'ℹ')}  {msg}  ",
             bg=C["bg2"], fg=C["text"],
             font=("Segoe UI", 9), pady=7).pack(side="left")
    t.update_idletasks()
    sw, sh = t.winfo_screenwidth(), t.winfo_screenheight()
    t.geometry(f"+{sw - t.winfo_width() - 30}+{sh - t.winfo_height() - 60}")
    t.after(3000, t.destroy)


class DialogoConfirmar(tk.Toplevel):
    def __init__(self, parent, titulo, mensagem):
        super().__init__(parent)
        self.resultado = False
        self.title(titulo)
        self.resizable(False, False)
        self.config(bg=C["bg2"])
        self.transient(parent)
        self.grab_set()
        tk.Label(self, text=mensagem, bg=C["bg2"], fg=C["text"],
                 font=("Segoe UI", 9), wraplength=300,
                 justify="center").pack(padx=24, pady=18)
        row = tk.Frame(self, bg=C["bg2"]); row.pack(pady=(0, 14))
        Btn(row, "Cancelar",  cmd=self.destroy, estilo="ghost").pack(side="left", padx=5)
        Btn(row, "Confirmar", cmd=self._ok,     estilo="danger").pack(side="left", padx=5)
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width()  // 2 - self.winfo_width()  // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{px}+{py}")
        self.wait_window()

    def _ok(self):
        self.resultado = True
        self.destroy()
