import os
import re
import sys
import glob
import shutil
import subprocess
import tempfile
import threading
import queue
import io
import contextlib
import traceback
import unicodedata
import json
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

try:
    from icons import PY_ICON_B64, DIAGRAM_ICON_B64
except Exception:
    PY_ICON_B64 = None
    DIAGRAM_ICON_B64 = None

APP_NAME = "AlgoNotas"
APP_VERSION = "2.0"

PYTHON_KEYWORDS = [
    "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "False", "finally", "for", "from",
    "global", "if", "import", "in", "is", "lambda", "None", "nonlocal", "not",
    "or", "pass", "raise", "return", "True", "try", "while", "with", "yield",
    "self",
]

PYTHON_BUILTINS = [
    "abs", "all", "any", "bin", "bool", "bytes", "callable", "chr", "dict",
    "dir", "divmod", "enumerate", "eval", "filter", "float", "format",
    "frozenset", "getattr", "hasattr", "hash", "help", "hex", "id", "input",
    "int", "isinstance", "issubclass", "iter", "len", "list", "map", "max",
    "min", "next", "object", "oct", "open", "ord", "pow", "print", "range",
    "repr", "reversed", "round", "set", "setattr", "slice", "sorted", "str",
    "sum", "super", "tuple", "type", "vars", "zip",
]

GLOSSARY = {
    "algoritmo": (
        "Algoritmo",
        "Una secuencia ordenada de pasos para resolver un problema. "
        "Piensa en una receta de cocina: si sigues los pasos en orden, "
        "obtienes el resultado. En programación esos pasos son el código.",
        "abrir la puerta:\n"
        "  1. levantarse\n"
        "  2. caminar hasta la puerta\n"
        "  3. girar la manija\n"
        "  4. empujar",
    ),
    "codigo": (
        "Código",
        "El conjunto de instrucciones que escribes en un lenguaje de "
        "programación (como Python) para decirle a la computadora qué hacer. "
        "El código se guarda en archivos con extensión .py.",
        "print(\"Hola mundo\")",
    ),
    "interprete": (
        "Intérprete",
        "Programa que lee tu código línea por línea y lo ejecuta al momento, "
        "sin necesidad de compilarlo antes. Python usa un intérprete, por eso "
        "puedes probar ideas rápidamente.",
        "El programa python.exe es el intérprete de Python.",
    ),
    "slice": (
        "Slice (rebanada)",
        "Forma de tomar una parte de una secuencia (texto, lista, etc.) usando "
        "corchetes con inicio:fin:paso. El inicio se incluye y el fin se excluye.",
        "texto = \"Python\"\n"
        "texto[0:3]   ->  \"Pyt\"\n"
        "texto[2:]    ->  \"thon\"\n"
        "texto[::-1]  ->  \"nohtyP\"  (invertido)",
    ),
    "comando": (
        "Comando",
        "Una instrucción u orden que le das a la computadora. También se llama "
        "así a lo que escribes en una terminal (por ejemplo: python programa.py).",
        "python mi_programa.py",
    ),
    "python": (
        "Python",
        "Lenguaje de programación fácil de leer y muy usado para aprender, "
        "crear juegos, analizar datos e inteligencia artificial. Se ejecuta "
        "con un intérprete y se guarda en archivos .py.",
        "print(\"¡Hola, Python!\")",
    ),
    "funcion": (
        "Función",
        "Bloque de código con un nombre que realiza una tarea y que puedes "
        "reutilizar llamándolo. Se define con la palabra reservada def y puede "
        "recibir datos (parámetros) y devolver un resultado (return).",
        "def sumar(a, b):\n"
        "    return a + b\n\n"
        "sumar(2, 3)  ->  5",
    ),
    "string": (
        "String (texto)",
        "Tipo de dato para texto: una cadena de caracteres entre comillas "
        "simples o dobles. Se puede unir (+) y sacar partes con slicing.",
        "nombre = \"Ana\"\n"
        "saludo = \"Hola \" + nombre",
    ),
    "int": (
        "int (entero)",
        "Tipo de dato para números enteros, sin decimales, positivos o "
        "negativos. Se usa para contar y en operaciones exactas.",
        "edad = 15\n"
        "int(\"42\")  ->  42",
    ),
    "float": (
        "float (decimal)",
        "Tipo de dato para números con decimales (punto flotante). Se escribe "
        "con punto, no con coma.",
        "precio = 3.50\n"
        "float(\"2.5\")  ->  2.5",
    ),
    "bool": (
        "bool (booleano)",
        "Tipo de dato con solo dos valores: True (verdadero) y False (falso). "
        "Se usa en condiciones y comparaciones.",
        "5 > 3        ->  True\n"
        "10 == 7      ->  False\n"
        "bool(0)      ->  False",
    ),
    "variable": (
        "Variable",
        "Nombre que guarda un valor en la memoria para usarlo después. Se crea "
        "con el operador = (asignación).",
        "edad = 15\n"
        "nombre = \"Ana\"",
    ),
    "lista": (
        "Lista",
        "Colección ordenada de varios valores entre corchetes. Puedes agregar, "
        "quitar y acceder a sus elementos por su posición (índice, desde 0).",
        "notas = [7, 9, 10]\n"
        "notas[0]     ->  7\n"
        "notas.append(8)",
    ),
    "diccionario": (
        "Diccionario",
        "Colección de pares clave:valor entre llaves. Sirve para guardar datos "
        "con nombre, como una ficha.",
        "alumno = {\"nombre\": \"Ana\", \"edad\": 15}\n"
        "alumno[\"nombre\"]  ->  \"Ana\"",
    ),
    "bucle": (
        "Bucle",
        "Estructura que repite instrucciones varias veces. En Python se usan "
        "for (para repetir sobre una secuencia) y while (mientras se cumpla "
        "una condición).",
        "for i in range(3):\n"
        "    print(i)",
    ),
    "condicional": (
        "Condicional",
        "Estructura que decide qué código ejecutar según una condición: if "
        "(si), elif (si no, si...), else (si no).",
        "nota = 8\n"
        "if nota >= 6:\n"
        "    print(\"Aprobado\")\n"
        "else:\n"
        "    print(\"A mejorar\")",
    ),
    "print": (
        "print()",
        "Función que muestra un mensaje en la pantalla (en la salida). Sirve "
        "para ver resultados y comprobar que tu programa funciona.",
        "print(\"Hola\")\n"
        "print(2 + 3)  ->  5",
    ),
    "input": (
        "input()",
        "Función que pide al usuario escribir algo por el teclado y lo devuelve "
        "como texto (string).",
        "nombre = input(\"¿Cómo te llamas? \")\n"
        "print(\"Hola\", nombre)",
    ),
    "comentario": (
        "Comentario",
        "Texto que Python ignora; sirve para explicar el código. Empieza con # "
        "y llega hasta el final de la línea.",
        "# Esto es un comentario\n"
        "edad = 15  # también aquí",
    ),
    "indentacion": (
        "Indentación",
        "Los espacios al inicio de una línea. En Python son obligatorios: "
        "marcan qué instrucciones están dentro de un if, for, def, etc. Se "
        "suele usar 4 espacios.",
        "if True:\n"
        "    print(\"dentro\")",
    ),
    "operador": (
        "Operador",
        "Símbolo que realiza una operación: aritmética (+, -, *, /, //, %, **), "
        "comparación (==, !=, <, >) o lógica (and, or, not).",
        "7 + 2   ->  9\n"
        "7 // 2  ->  3   (división entera)\n"
        "7 % 2   ->  1   (resto)",
    ),
    "modulo": (
        "Módulo",
        "Archivo de código con funciones y herramientas listas para usar. Se "
        "importa con import para aprovechar el trabajo ya hecho.",
        "import math\n"
        "math.sqrt(16)  ->  4.0",
    ),
    "error": (
        "Error",
        "Aviso de que algo salió mal. El más común al empezar es SyntaxError "
        "(algo mal escrito). Leer el mensaje te dice la línea y el motivo.",
        "print(\"Hola\"   # falta el )  ->  SyntaxError",
    ),
    "depurar": (
        "Depurar (debug)",
        "Encontrar y corregir errores en tu programa. Trucos: leer el mensaje "
        "de error, probar por partes y usar print() para ver valores.",
        "print(\"valor de x:\", x)",
    ),
}

GLOSSARY_ALIASES = {
    "commando": "comando",
    "codigos": "codigo",
    "intérprete": "interprete",
    "rebanada": "slice",
    "slicing": "slice",
    "funcion": "funcion",
    "función": "funcion",
    "string": "string",
    "texto": "string",
    "cadena": "string",
    "entero": "int",
    "decimal": "float",
    "booleano": "bool",
    "debug": "depurar",
    "depuracion": "depurar",
    "arreglo": "lista",
    "indentación": "indentacion",
    "bucle_for": "bucle",
    "while": "bucle",
    "for": "bucle",
    "if": "condicional",
    "else": "condicional",
}


def normalize_word(word):
    sin_acentos = unicodedata.normalize("NFKD", word)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return sin_acentos.strip().lower()


def lookup_concept(word):
    key = normalize_word(word)
    if not key:
        return None
    if key in GLOSSARY:
        return GLOSSARY[key]
    alias = GLOSSARY_ALIASES.get(key)
    if alias and alias in GLOSSARY:
        return GLOSSARY[alias]
    if alias:
        return GLOSSARY.get(normalize_word(alias))
    return None


THEMES = {
    "claro": {
        "bg": "#ffffff",
        "fg": "#1f2328",
        "gutter_bg": "#eef0f3",
        "gutter_fg": "#8a919a",
        "cursor": "#1f2328",
        "select": "#bcd6ff",
        "keyword": "#cf222e",
        "builtin": "#8250df",
        "string": "#0a7c4a",
        "comment": "#8b949e",
        "number": "#0550ae",
        "function": "#953800",
        "classname": "#b35100",
        "decorator": "#b87a00",
        "operator": "#cf222e",
        "self": "#d6336c",
        "params": "#6639ba",
        "punct": "#57606a",
        "brackets": ["#d9822b", "#0aa2c0", "#8250df", "#d6336c"],
        "output_bg": "#f6f8fa",
        "line_highlight": "#eaf2fd",
        "toolbar_bg": "#e3e6ea",
        "toolbar_fg": "#1f2328",
        "accent": "#2563eb",
    },
    "oscuro": {
        "bg": "#1e1e28",
        "fg": "#e4e4ec",
        "gutter_bg": "#171720",
        "gutter_fg": "#5a5a6e",
        "cursor": "#e4e4ec",
        "select": "#2f4b7c",
        "keyword": "#ff7b72",
        "builtin": "#d2a8ff",
        "string": "#7ee787",
        "comment": "#7d8590",
        "number": "#79c0ff",
        "function": "#ffa657",
        "classname": "#ffca7a",
        "decorator": "#e3b341",
        "operator": "#ff7b72",
        "self": "#ff9eb5",
        "params": "#b392f0",
        "punct": "#8b949e",
        "brackets": ["#e5c07b", "#56b6c2", "#c678dd", "#e06c75"],
        "output_bg": "#14141c",
        "line_highlight": "#26263a",
        "toolbar_bg": "#262632",
        "toolbar_fg": "#e4e4ec",
        "accent": "#4c8dff",
    },
}

WELCOME = '''# ¡Bienvenido a AlgoNotas! 🐍
# Escribe código aquí y presiona F5 (o el botón ▶ Ejecutar).

nombre = "alumno"

def saludar(quien):
    for i in range(3):
        print(f"¡Hola {quien}! ({i + 1})")

saludar(nombre)

# Prueba cambiar colores, escribir más código y ejecutarlo.
# Escribe ?python o ?algoritmo y presiona Enter para ver su definición.
'''

DIAGRAM_COLORS = [
    "#000000", "#4c8dff", "#22b8cf", "#2f9e44", "#f59f00",
    "#e8590c", "#e03131", "#9c36b5",
]

ANCHORS = ("top", "bottom", "left", "right")


def _fig_persona(c, cx, cy, tag, color, fill):
    c.create_oval(cx - 12, cy - 40, cx + 12, cy - 16, outline=color, fill=fill,
                  width=2, tags=tag)
    c.create_arc(cx - 24, cy - 16, cx + 24, cy + 32, start=0, extent=180,
                 style="chord", outline=color, fill=fill, width=2, tags=tag)


def _fig_computadora(c, cx, cy, tag, color, fill):
    c.create_rectangle(cx - 30, cy - 34, cx + 30, cy + 8, outline=color,
                       fill=fill, width=2, tags=tag)
    c.create_rectangle(cx - 25, cy - 29, cx + 25, cy + 3, outline=color,
                       width=2, tags=tag)
    c.create_polygon(cx - 40, cy + 20, cx + 40, cy + 20, cx + 30, cy + 8,
                     cx - 30, cy + 8, outline=color, fill=fill, width=2, tags=tag)


def _fig_basedatos(c, cx, cy, tag, color, fill):
    c.create_line(cx - 24, cy - 25, cx - 24, cy + 13, fill=color, width=2, tags=tag)
    c.create_line(cx + 24, cy - 25, cx + 24, cy + 13, fill=color, width=2, tags=tag)
    c.create_arc(cx - 24, cy + 4, cx + 24, cy + 22, start=180, extent=180,
                 style="arc", outline=color, width=2, tags=tag)
    c.create_arc(cx - 24, cy - 12, cx + 24, cy + 6, start=180, extent=180,
                 style="arc", outline=color, width=2, tags=tag)
    c.create_oval(cx - 24, cy - 34, cx + 24, cy - 16, outline=color, fill=fill,
                  width=2, tags=tag)


def _fig_monitor(c, cx, cy, tag, color, fill):
    c.create_rectangle(cx - 32, cy - 34, cx + 32, cy + 12, outline=color,
                       fill=fill, width=2, tags=tag)
    c.create_rectangle(cx - 27, cy - 29, cx + 27, cy + 7, outline=color,
                       width=2, tags=tag)
    c.create_line(cx, cy + 12, cx, cy + 26, fill=color, width=2, tags=tag)
    c.create_rectangle(cx - 16, cy + 26, cx + 16, cy + 32, outline=color,
                       fill=fill, width=2, tags=tag)


def _fig_servidor(c, cx, cy, tag, color, fill):
    c.create_rectangle(cx - 22, cy - 36, cx + 22, cy + 36, outline=color,
                       fill=fill, width=2, tags=tag)
    for yy in (cy - 18, cy, cy + 18):
        c.create_line(cx - 22, yy, cx + 22, yy, fill=color, width=2, tags=tag)
    for yc in (cy - 28, cy - 10, cy + 8, cy + 26):
        c.create_oval(cx + 8, yc - 4, cx + 16, yc + 4, outline=color, width=2, tags=tag)


def _fig_rombo(c, cx, cy, tag, color, fill):
    c.create_polygon(cx, cy - 38, cx + 46, cy, cx, cy + 38, cx - 46, cy,
                     outline=color, fill=fill, width=2, tags=tag)


def _fig_nube(c, cx, cy, tag, color, fill):
    circles = [(-22, 2, 24), (10, -6, 26), (34, 6, 20)]
    points = [(cx - 46, cy + 18)]
    for x in range(-46, 55, 3):
        top = None
        for ccx, ccy, r in circles:
            dx = x - ccx
            if abs(dx) <= r:
                ytop = ccy - math.sqrt(r * r - dx * dx)
                if top is None or ytop < top:
                    top = ytop
        if top is not None:
            points.append((cx + x, cy + top))
    points.append((cx + 54, cy + 18))
    c.create_polygon(points, outline=color, fill=fill, width=2, smooth=True, tags=tag)


def _fig_documento(c, cx, cy, tag, color, fill):
    c.create_polygon(cx - 26, cy - 34, cx + 14, cy - 34, cx + 26, cy - 22,
                     cx + 26, cy + 34, cx - 26, cy + 34,
                     outline=color, fill=fill, width=2, tags=tag)
    c.create_line(cx + 14, cy - 34, cx + 14, cy - 22, cx + 26, cy - 22,
                  fill=color, width=2, tags=tag)


FIGURE_DRAW = {
    "persona": _fig_persona,
    "computadora": _fig_computadora,
    "basedatos": _fig_basedatos,
    "monitor": _fig_monitor,
    "servidor": _fig_servidor,
    "rombo": _fig_rombo,
    "nube": _fig_nube,
    "documento": _fig_documento,
}

FIGURES = [
    ("persona", "👤", "Persona"),
    ("computadora", "💻", "Computadora"),
    ("basedatos", "🗄️", "Base de datos"),
    ("monitor", "🖥️", "Monitor"),
    ("servidor", "🖧", "Servidor"),
    ("rombo", "🔶", "Rombo (decisión)"),
    ("nube", "☁️", "Nube"),
    ("documento", "📄", "Documento"),
]


def find_python():
    if not getattr(sys, "frozen", False):
        return sys.executable
    for name in ("python", "python3"):
        path = shutil.which(name)
        if path:
            return path
    path = shutil.which("py")
    if path:
        return path
    patterns = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python3*\python.exe"),
        os.path.expandvars(r"%ProgramFiles%\Python3*\python.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Python3*\python.exe"),
        r"C:\Python3*\python.exe",
    ]
    for pattern in patterns:
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    return None


class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} - Sin título")
        self.minsize(700, 460)

        self.current_file = None
        self.dirty = False
        self.theme_name = "oscuro"
        self.font_size = 13
        self._highlight_job = None
        self._line_job = None
        self._output_queue = queue.Queue()

        self.diagram_tool = "select"
        self.diagram_color = "#000000"
        self.diagram_no_fill = True
        self.figure_kind = "persona"
        self._arrow_start_shape = None
        self._arrow_start_anchor = None
        self._shape_counter = 0
        self._shapes = {}
        self._selected = None
        self._selected_tag = None
        self._drag_start = None
        self._drag_item = None
        self._move_last = None

        self._build_menu()
        self._build_notebook()
        self._build_toolbar()
        self._build_widgets()
        self._build_diagram()
        self._bind_events()
        self.apply_theme()

        self.text.insert("1.0", WELCOME)
        self.text.edit_modified(False)
        self.dirty = False
        self._update_line_numbers()
        self._schedule_highlight()
        self._center_window()
        self.after(80, self._poll_output)

    def _center_window(self):
        self.update_idletasks()
        width = min(1060, self.winfo_screenwidth() - 80)
        height = min(700, self.winfo_screenheight() - 120)
        x = (self.winfo_screenwidth() - width) // 2
        y = max(0, (self.winfo_screenheight() - height) // 3)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_notebook(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.code_page = tk.Frame(self.notebook)
        self.diagram_page = tk.Frame(self.notebook)

        self._py_icon = self._load_tab_icon(PY_ICON_B64)
        self._diagram_icon = self._load_tab_icon(DIAGRAM_ICON_B64)
        if self._py_icon:
            self.notebook.add(self.code_page, text="   Código   ",
                              image=self._py_icon, compound="left")
        else:
            self.notebook.add(self.code_page, text="   📝  Código   ")
        if self._diagram_icon:
            self.notebook.add(self.diagram_page, text="   Diagrama   ",
                              image=self._diagram_icon, compound="left")
        else:
            self.notebook.add(self.diagram_page, text="   🔷  Diagrama   ")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    @staticmethod
    def _load_tab_icon(data_b64):
        if not data_b64:
            return None
        try:
            return tk.PhotoImage(data=data_b64)
        except tk.TclError:
            return None

    def _on_tab_changed(self, event=None):
        if self.notebook.index(self.notebook.select()) == 1:
            self._focus_canvas()
        else:
            self.text.focus_set()

    # ------------------------------------------------------------------ UI
    def _build_menu(self):
        menubar = tk.Menu(self)

        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="Nuevo", accelerator="Ctrl+N", command=self.new_file)
        m_file.add_command(label="Abrir...", accelerator="Ctrl+O", command=self.open_file)
        m_file.add_command(label="Guardar", accelerator="Ctrl+S", command=self.save_file)
        m_file.add_command(label="Guardar como...", accelerator="Ctrl+Shift+S",
                           command=self.save_file_as)
        m_file.add_separator()
        m_file.add_command(label="Salir", command=self.on_close)
        menubar.add_cascade(label="Archivo", menu=m_file)

        m_edit = tk.Menu(menubar, tearoff=0)
        m_edit.add_command(label="Deshacer", accelerator="Ctrl+Z",
                           command=lambda: self.text.event_generate("<<Undo>>"))
        m_edit.add_command(label="Rehacer", accelerator="Ctrl+Y",
                           command=lambda: self.text.event_generate("<<Redo>>"))
        m_edit.add_separator()
        m_edit.add_command(label="Cortar", accelerator="Ctrl+X",
                           command=lambda: self.text.event_generate("<<Cut>>"))
        m_edit.add_command(label="Copiar", accelerator="Ctrl+C",
                           command=lambda: self.text.event_generate("<<Copy>>"))
        m_edit.add_command(label="Pegar", accelerator="Ctrl+V",
                           command=lambda: self.text.event_generate("<<Paste>>"))
        m_edit.add_separator()
        m_edit.add_command(label="Seleccionar todo", accelerator="Ctrl+A",
                           command=self.select_all)
        menubar.add_cascade(label="Editar", menu=m_edit)

        m_run = tk.Menu(menubar, tearoff=0)
        m_run.add_command(label="Ejecutar código", accelerator="F5", command=self.run_code)
        m_run.add_command(label="Limpiar salida", command=self.clear_output)
        menubar.add_cascade(label="Ejecutar", menu=m_run)

        m_view = tk.Menu(menubar, tearoff=0)
        m_view.add_command(label="Aumentar fuente", accelerator="Ctrl++",
                           command=lambda: self.change_font(1))
        m_view.add_command(label="Disminuir fuente", accelerator="Ctrl+-",
                           command=lambda: self.change_font(-1))
        m_view.add_separator()
        self.theme_var = tk.StringVar(value=self.theme_name)
        m_view.add_radiobutton(label="Tema oscuro", value="oscuro",
                               variable=self.theme_var, command=self.apply_theme)
        m_view.add_radiobutton(label="Tema claro", value="claro",
                               variable=self.theme_var, command=self.apply_theme)
        menubar.add_cascade(label="Ver", menu=m_view)

        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="Lista de conceptos (?)",
                           command=lambda: self.show_concept(""))
        m_help.add_command(label="Acerca de", command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=m_help)

        self.config(menu=menubar)

    def _build_toolbar(self):
        self.toolbar = tk.Frame(self.code_page, height=44)
        self.toolbar.pack(fill="x", side="top")

        self.run_button = tk.Button(self.toolbar, text="▶  Ejecutar (F5)",
                                    command=self.run_code, relief="flat",
                                    padx=14, pady=6, cursor="hand2",
                                    font=("Segoe UI", 10, "bold"))
        self.run_button.pack(side="left", padx=(8, 6), pady=6)

        def make_btn(text, cmd):
            b = tk.Button(self.toolbar, text=text, command=cmd, relief="flat",
                          padx=10, pady=6, cursor="hand2",
                          font=("Segoe UI", 10))
            b.pack(side="left", padx=3, pady=6)
            return b

        make_btn("Nuevo", self.new_file)
        make_btn("Abrir", self.open_file)
        make_btn("Guardar", self.save_file)
        make_btn("Limpiar salida", self.clear_output)

    def _build_widgets(self):
        container = tk.Frame(self.code_page)
        container.pack(fill="both", expand=True)

        self.paned = ttk.PanedWindow(container, orient="vertical")
        self.paned.pack(fill="both", expand=True)

        self.editor_frame = tk.Frame(self.paned)
        self.paned.add(self.editor_frame, weight=4)

        self.linenumbers = tk.Text(
            self.editor_frame, width=4, padx=6, takefocus=0, border=0,
            highlightthickness=0, state="disabled", wrap="none", cursor="arrow",
        )
        self.linenumbers.grid(row=0, column=0, sticky="ns")

        self.text = tk.Text(
            self.editor_frame, wrap="none", undo=True, border=0,
            highlightthickness=0, padx=8, pady=6, insertwidth=2,
        )
        self.text.grid(row=0, column=1, sticky="nsew")

        self.vscroll = ttk.Scrollbar(self.editor_frame, orient="vertical",
                                     command=self._on_scroll)
        self.vscroll.grid(row=0, column=2, sticky="ns")

        self.editor_frame.rowconfigure(0, weight=1)
        self.editor_frame.columnconfigure(1, weight=1)

        self.text.configure(yscrollcommand=self._on_yscroll)
        self.linenumbers.configure(yscrollcommand=self._on_yscroll)

        self.output_panel = tk.Frame(self.paned)
        self.output_label = tk.Label(self.output_panel, text="▶ SALIDA  ·  F5 para ejecutar",
                                     anchor="w", padx=8, pady=3)
        self.output_label.pack(fill="x")
        self.output = tk.Text(self.output_panel, height=8, border=0,
                              highlightthickness=0, padx=10, pady=8, wrap="word")
        self.output.pack(fill="both", expand=True)
        self.output.configure(state="disabled")
        self.paned.add(self.output_panel, weight=1)

        self.status = tk.Label(self, text="Ln 1, Col 1", anchor="e", padx=10)
        self.status.pack(fill="x", side="bottom")

    # ------------------------------------------------------------ diagrama
    def _build_diagram(self):
        self.diagram_toolbar = tk.Frame(self.diagram_page)
        self.diagram_toolbar.pack(fill="x", side="top")

        self.tool_buttons = {}
        tools = [
            ("select", "🖱  Mover (V)"),
            ("oval", "⭕  Círculo (C)"),
            ("rect", "▭  Caja (B)"),
            ("text", "🅃  Texto (T)"),
            ("arrow", "➜  Flecha (F)"),
            ("figure", "🧩  Figuras"),
            ("eraser", "🧽  Borrador (Q)"),
        ]
        for name, label in tools:
            command = (self._open_figures_menu if name == "figure"
                       else (lambda n=name: self._set_tool(n)))
            b = tk.Button(self.diagram_toolbar, text=label, relief="flat",
                          padx=10, pady=6, cursor="hand2",
                          font=("Segoe UI", 10), command=command)
            b.pack(side="left", padx=3, pady=6)
            self.tool_buttons[name] = b

        tk.Label(self.diagram_toolbar, text="  Color:", font=("Segoe UI", 9)
                 ).pack(side="left", padx=(10, 2))
        self.color_buttons = {}
        for color in DIAGRAM_COLORS:
            b = tk.Button(self.diagram_toolbar, bg=color, width=2, relief="flat",
                          cursor="hand2", command=lambda c=color: self._set_color(c))
            b.pack(side="left", padx=1, pady=10)
            self.color_buttons[color] = b

        self.no_fill_button = tk.Button(
            self.diagram_toolbar, text="∅  Sin relleno", relief="flat",
            padx=8, pady=6, cursor="hand2", font=("Segoe UI", 9),
            command=self._toggle_no_fill)
        self.no_fill_button.pack(side="left", padx=(8, 3), pady=6)

        tk.Button(self.diagram_toolbar, text="🧹 Borrar todo (Alt+Q)", relief="flat",
                  padx=10, pady=6, cursor="hand2", font=("Segoe UI", 10),
                  command=self._clear_diagram).pack(side="left", padx=(10, 3), pady=6)

        tk.Button(self.diagram_toolbar, text="💾 Guardar", relief="flat",
                  padx=10, pady=6, cursor="hand2", font=("Segoe UI", 10),
                  command=self._save_diagram).pack(side="right", padx=(3, 8), pady=6)
        tk.Button(self.diagram_toolbar, text="📂 Abrir", relief="flat",
                  padx=10, pady=6, cursor="hand2", font=("Segoe UI", 10),
                  command=self._open_diagram).pack(side="right", padx=3, pady=6)

        self.canvas = tk.Canvas(self.diagram_page, bg="#ffffff",
                                highlightthickness=0, cursor="crosshair",
                                takefocus=True)
        self.canvas.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.canvas.bind("<ButtonPress-1>", self._diagram_press)
        self.canvas.bind("<B1-Motion>", self._diagram_motion)
        self.canvas.bind("<ButtonRelease-1>", self._diagram_release)
        self.canvas.bind("<Double-Button-1>", self._diagram_double)
        self.canvas.bind("<Motion>", self._diagram_hover)
        self.canvas.bind("<Leave>", self._diagram_leave)
        self.canvas.bind("<Key>", self._diagram_key)
        self.bind_all("<Key>", self._on_shortcut_key, add="+")
        self.bind_all("<Alt-q>", self._on_shortcut_clear, add="+")
        self.bind_all("<Alt-Q>", self._on_shortcut_clear, add="+")
        self.canvas.bind("<Delete>", self._delete_selected)
        self.canvas.bind("<BackSpace>", self._delete_selected)
        for child in self.diagram_toolbar.winfo_children():
            try:
                child.configure(takefocus=0)
            except tk.TclError:
                pass
        self._set_tool("select")

    def _set_tool(self, name):
        self.diagram_tool = name
        if hasattr(self, "canvas"):
            cursor = {"select": "arrow", "eraser": "none"}.get(name, "crosshair")
            self.canvas.configure(cursor=cursor)
            self.canvas.delete("eraser_cursor")
            self.canvas.delete("anchor_hot")
            self._style_diagram_buttons()
            self._refresh_anchors()
            self._focus_canvas()

    def _set_color(self, color):
        self.diagram_color = color
        self._style_diagram_buttons()
        self._focus_canvas()

    def _toggle_no_fill(self):
        self.diagram_no_fill = not self.diagram_no_fill
        self._style_diagram_buttons()
        self._focus_canvas()

    def _open_figures_menu(self):
        menu = tk.Menu(self, tearoff=0)
        for key, emoji, name in FIGURES:
            menu.add_command(label=f"{emoji}  {name}",
                             command=lambda k=key: self._choose_figure(k))
        btn = self.tool_buttons["figure"]
        try:
            menu.tk_popup(btn.winfo_rootx(),
                          btn.winfo_rooty() + btn.winfo_height())
        finally:
            menu.grab_release()

    def _choose_figure(self, kind):
        self.figure_kind = kind
        name = next((n for k, e, n in FIGURES if k == kind), "Figuras")
        self.tool_buttons["figure"].configure(text=f"🧩  {name}")
        self._set_tool("figure")

    def _add_figure(self, kind, cx, cy):
        draw = FIGURE_DRAW.get(kind)
        if draw is None:
            return None
        tag = f"shape{self._shape_counter}"
        self._shape_counter += 1
        color = self.diagram_color
        fill = "" if self.diagram_no_fill else color
        draw(self.canvas, cx, cy, tag, color, fill)
        self._shapes[tag] = {
            "kind": "figure", "color": color, "item": None,
            "fill": fill, "outline": color, "width": 2,
            "start": None, "end": None,
            "start_anchor": None, "end_anchor": None,
            "figure": kind, "center": (cx, cy),
        }
        self._refresh_anchors()
        return tag

    def _shape_style(self):
        if self.diagram_no_fill:
            return {"fill": "", "outline": self.diagram_color, "width": 3}
        return {"fill": self.diagram_color, "outline": "#1f2328", "width": 2}

    def _style_diagram_buttons(self):
        t = THEMES[self.theme_name]
        for name, btn in self.tool_buttons.items():
            if name == self.diagram_tool:
                btn.configure(bg=t["accent"], fg="#ffffff",
                              activebackground=t["accent"],
                              activeforeground="#ffffff")
            else:
                btn.configure(bg=t["toolbar_bg"], fg=t["toolbar_fg"],
                              activebackground=t["accent"],
                              activeforeground="#ffffff")
        if getattr(self, "no_fill_button", None) is not None:
            if self.diagram_no_fill:
                self.no_fill_button.configure(bg=t["accent"], fg="#ffffff",
                                              activebackground=t["accent"],
                                              activeforeground="#ffffff")
            else:
                self.no_fill_button.configure(bg=t["toolbar_bg"], fg=t["toolbar_fg"],
                                              activebackground=t["accent"],
                                              activeforeground="#ffffff")

    def _new_shape(self, item, kind):
        tag = f"shape{self._shape_counter}"
        self._shape_counter += 1
        self.canvas.itemconfig(item, tags=(tag,))
        style = self._shape_style()
        self._shapes[tag] = {
            "kind": kind,
            "color": self.diagram_color,
            "item": item,
            "fill": style["fill"],
            "outline": style["outline"],
            "width": style["width"],
            "start": None,
            "end": None,
            "start_anchor": None,
            "end_anchor": None,
        }
        self.canvas.tag_raise(item)
        return tag

    def _shape_at(self, x, y, margin=8):
        items = self.canvas.find_overlapping(x - margin, y - margin,
                                             x + margin, y + margin)
        for item in reversed(items):
            tags = self.canvas.gettags(item)
            if not tags or "selection" in tags:
                continue
            tag = tags[0]
            if tag in self._shapes and self._shapes[tag]["kind"] in ("oval", "rect", "text", "figure"):
                return tag
        return None

    def _point_in_shape(self, tag, x, y):
        bbox = self.canvas.bbox(tag)
        if not bbox:
            return False
        x0, y0, x1, y1 = bbox
        if self._shapes[tag]["kind"] == "oval":
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            hw = max((x1 - x0) / 2, 1)
            hh = max((y1 - y0) / 2, 1)
            return ((x - cx) / hw) ** 2 + ((y - cy) / hh) ** 2 <= 1.0
        return x0 <= x <= x1 and y0 <= y <= y1

    def _shape_hit(self, x, y):
        for item in reversed(self.canvas.find_all()):
            tags = self.canvas.gettags(item)
            if any(t in ("selection", "anchor", "anchor_hot", "eraser_cursor")
                   for t in tags):
                continue
            for t in tags:
                if t in self._shapes and self._shapes[t]["kind"] in ("oval", "rect", "text", "figure"):
                    if self._point_in_shape(t, x, y):
                        return t
                    break
        return None

    def _shape_center(self, tag):
        bbox = self.canvas.bbox(tag)
        if not bbox:
            return None
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

    def _anchor_coords(self, tag, anchor):
        bbox = self.canvas.bbox(tag)
        if not bbox:
            return None
        x0, y0, x1, y1 = bbox
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return {
            "top": (cx, y0),
            "bottom": (cx, y1),
            "left": (x0, cy),
            "right": (x1, cy),
        }.get(anchor)

    def _nearest_anchor(self, x, y, margin=26):
        best = None
        for tag, meta in self._shapes.items():
            if meta["kind"] not in ("oval", "rect", "text", "figure"):
                continue
            for anchor in ANCHORS:
                point = self._anchor_coords(tag, anchor)
                if not point:
                    continue
                dist = (point[0] - x) ** 2 + (point[1] - y) ** 2
                if dist <= margin * margin and (best is None or dist < best[0]):
                    best = (dist, tag, anchor, point)
        return best

    def _refresh_anchors(self):
        self.canvas.delete("anchor")
        if self.diagram_tool != "arrow":
            return
        for tag, meta in self._shapes.items():
            if meta["kind"] not in ("oval", "rect", "text", "figure"):
                continue
            for anchor in ANCHORS:
                point = self._anchor_coords(tag, anchor)
                if not point:
                    continue
                r = 4
                self.canvas.create_oval(point[0] - r, point[1] - r,
                                        point[0] + r, point[1] + r,
                                        fill="#ffffff", outline=self.diagram_color,
                                        width=2, tags=("anchor",))
        self.canvas.tag_raise("anchor")

    def _hot_anchor(self, x, y):
        self.canvas.delete("anchor_hot")
        if self.diagram_tool != "arrow":
            return None
        near = self._nearest_anchor(x, y)
        if not near:
            return None
        _, tag, anchor, point = near
        r = 6
        self.canvas.create_oval(point[0] - r, point[1] - r, point[0] + r, point[1] + r,
                                fill="#ffd43b", outline="#e03131", width=2,
                                tags=("anchor_hot",))
        self.canvas.tag_raise("anchor_hot")
        return (tag, anchor, point)

    def _anchor_point(self, tag, toward):
        items = self.canvas.find_withtag(tag)
        if not items:
            return None
        bbox = self.canvas.bbox(items[0])
        if not bbox:
            return None
        x0, y0, x1, y1 = bbox
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = toward[0] - cx, toward[1] - cy
        if dx == 0 and dy == 0:
            return (cx, cy)
        halfw = max((x1 - x0) / 2, 1)
        halfh = max((y1 - y0) / 2, 1)
        kind = self._shapes[tag]["kind"]
        if kind in ("rect", "text"):
            tx = halfw / abs(dx) if dx else float("inf")
            ty = halfh / abs(dy) if dy else float("inf")
            t = min(tx, ty)
        else:
            t = 1.0 / math.sqrt((dx / halfw) ** 2 + (dy / halfh) ** 2)
        return (cx + dx * t, cy + dy * t)

    def _update_arrow(self, tag):
        meta = self._shapes.get(tag)
        items = self.canvas.find_withtag(tag)
        if not meta or not items or len(self.canvas.coords(items[0])) < 4:
            return
        item = items[0]
        x0, y0, x1, y1 = self.canvas.coords(item)[:4]
        start_tag = meta.get("start")
        end_tag = meta.get("end")
        start_anchor = meta.get("start_anchor")
        end_anchor = meta.get("end_anchor")

        if start_tag and start_anchor:
            point = self._anchor_coords(start_tag, start_anchor)
            if point:
                x0, y0 = point
        elif start_tag:
            ref = (self._shape_center(end_tag) if end_tag else None) or (x1, y1)
            point = self._anchor_point(start_tag, ref)
            if point:
                x0, y0 = point

        if end_tag and end_anchor:
            point = self._anchor_coords(end_tag, end_anchor)
            if point:
                x1, y1 = point
        elif end_tag:
            ref = (self._shape_center(start_tag) if start_tag else None) or (x0, y0)
            point = self._anchor_point(end_tag, ref)
            if point:
                x1, y1 = point

        self.canvas.coords(item, x0, y0, x1, y1)

    def _update_connected_arrows(self, shape_tag):
        for tag, meta in list(self._shapes.items()):
            if meta.get("kind") == "arrow" and (
                    meta.get("start") == shape_tag or meta.get("end") == shape_tag):
                self._update_arrow(tag)

    def _diagram_press(self, event):
        x, y = event.x, event.y
        self._focus_canvas()
        tool = self.diagram_tool
        if tool == "eraser":
            self._draw_eraser(x, y)
            self._erase_at(x, y)
            return
        if tool == "figure":
            self._add_figure(self.figure_kind, x, y)
            return
        if tool in ("oval", "rect"):
            self._drag_start = (x, y)
            style = self._shape_style()
            if tool == "oval":
                item = self.canvas.create_oval(x, y, x, y, **style)
            else:
                item = self.canvas.create_rectangle(x, y, x, y, **style)
            self._new_shape(item, tool)
            self._drag_item = item
        elif tool == "arrow":
            near = self._nearest_anchor(x, y)
            if near:
                _, self._arrow_start_shape, self._arrow_start_anchor, point = near
                x, y = point
            else:
                self._arrow_start_shape = None
                self._arrow_start_anchor = None
            self._drag_start = (x, y)
            item = self.canvas.create_line(x, y, x, y, arrow="last",
                                           fill=self.diagram_color, width=3,
                                           arrowshape=(14, 18, 6))
            self._new_shape(item, "arrow")
            self._drag_item = item
        elif tool == "text":
            text = simpledialog.askstring("Agregar texto",
                                          "Escribe el texto:", parent=self)
            if text:
                item = self.canvas.create_text(x, y, text=text,
                                               fill=self.diagram_color,
                                               font=("Segoe UI", 13, "bold"),
                                               anchor="center")
                self._new_shape(item, "text")
            self._focus_canvas()
        elif tool == "select":
            tag = self._shape_hit(x, y)
            if not tag:
                for item in reversed(self.canvas.find_overlapping(
                        x - 2, y - 2, x + 2, y + 2)):
                    for t in self.canvas.gettags(item):
                        if t in self._shapes:
                            tag = t
                            break
                    if tag:
                        break
            self._select(tag)
            self._move_last = (x, y)

    def _diagram_motion(self, event):
        x, y = event.x, event.y
        tool = self.diagram_tool
        if tool == "eraser":
            self._draw_eraser(x, y)
            self._erase_at(x, y)
            return
        if self._drag_item is not None and tool in ("oval", "rect"):
            x0, y0 = self._drag_start
            self.canvas.coords(self._drag_item, x0, y0, x, y)
        elif self._drag_item is not None and tool == "arrow":
            x0, y0 = self._drag_start
            near = self._hot_anchor(x, y)
            if near:
                x, y = near[2]
            self.canvas.coords(self._drag_item, x0, y0, x, y)
        elif tool == "select" and self._selected is not None:
            dx = x - self._move_last[0]
            dy = y - self._move_last[1]
            self.canvas.move(self._selected, dx, dy)
            self._move_last = (x, y)
            meta = self._shapes.get(self._selected_tag)
            if meta and meta["kind"] == "arrow":
                meta["start"] = None
                meta["end"] = None
            elif meta:
                self._update_connected_arrows(self._selected_tag)
            self._show_selection(self._selected)

    def _diagram_release(self, event):
        item = self._drag_item
        self._drag_item = None
        self._drag_start = None
        if item is None:
            return
        tags = self.canvas.gettags(item)
        tag = tags[0] if tags else None
        meta = self._shapes.get(tag)
        bbox = self.canvas.bbox(item)
        too_small = bbox is None or ((bbox[2] - bbox[0]) < 6 and (bbox[3] - bbox[1]) < 6)
        if too_small:
            self.canvas.delete(item)
            if tag in self._shapes:
                del self._shapes[tag]
            return
        if meta and meta["kind"] == "arrow":
            self.canvas.delete("anchor_hot")
            near = self._nearest_anchor(event.x, event.y)
            if near:
                _, end_tag, end_anchor, _ = near
                meta["end"] = end_tag
                meta["end_anchor"] = end_anchor
            else:
                meta["end"] = None
                meta["end_anchor"] = None
            meta["start"] = self._arrow_start_shape
            meta["start_anchor"] = self._arrow_start_anchor
            if (meta["start"] == meta["end"] and meta["start"] is not None
                    and meta["start_anchor"] == meta["end_anchor"]):
                meta["start"] = None
                meta["start_anchor"] = None
                meta["end"] = None
                meta["end_anchor"] = None
            self._update_arrow(tag)

    def _diagram_hover(self, event):
        if self.diagram_tool == "arrow" and self._drag_item is None:
            self._hot_anchor(event.x, event.y)
        elif self.diagram_tool == "eraser":
            self._draw_eraser(event.x, event.y)

    def _diagram_leave(self, event):
        self.canvas.delete("anchor_hot")
        self.canvas.delete("eraser_cursor")

    def _diagram_key(self, event):
        if event.state & (0x4 | 0x8 | 0x20000):
            return None
        mapping = {
            "v": "select", "c": "oval", "b": "rect",
            "f": "arrow", "q": "eraser", "t": "text",
        }
        tool = mapping.get(event.keysym.lower())
        if tool:
            self._set_tool(tool)
            return "break"
        return None

    def _diagram_active(self):
        try:
            return self.notebook.index(self.notebook.select()) == 1
        except Exception:
            return False

    def _focus_canvas(self):
        if self._diagram_active():
            self.canvas.focus_set()

    def _on_shortcut_key(self, event):
        if not self._diagram_active():
            return None
        focus = self.focus_get()
        if isinstance(focus, (tk.Text, tk.Entry, ttk.Entry)):
            return None
        return self._diagram_key(event)

    def _on_shortcut_clear(self, event=None):
        if self._diagram_active():
            self._clear_diagram()
        return "break"

    def _draw_eraser(self, x, y):
        self.canvas.delete("eraser_cursor")
        self.canvas.create_rectangle(x - 17, y - 26, x + 17, y - 2,
                                     fill="#ffffff", outline="#000000", width=2,
                                     tags="eraser_cursor")
        self.canvas.create_rectangle(x - 17, y - 26, x + 17, y - 18,
                                     fill="#e8590c", outline="#000000", width=2,
                                     tags="eraser_cursor")
        self.canvas.tag_raise("eraser_cursor")

    def _erase_at(self, x, y):
        tag = self._shape_hit(x, y)
        if tag:
            self._delete_shape(tag)
            return
        items = self.canvas.find_overlapping(x - 3, y - 3, x + 3, y + 3)
        for item in reversed(items):
            tags = self.canvas.gettags(item)
            if any(t in ("selection", "anchor", "anchor_hot", "eraser_cursor")
                   for t in tags):
                continue
            for t in tags:
                if t in self._shapes:
                    self._delete_shape(t)
                    return

    def _delete_shape(self, tag):
        if tag not in self._shapes:
            return
        self.canvas.delete(tag)
        del self._shapes[tag]
        if self._selected_tag == tag:
            self._deselect()
        for meta in self._shapes.values():
            if meta.get("kind") == "arrow":
                if meta.get("start") == tag:
                    meta["start"] = None
                    meta["start_anchor"] = None
                if meta.get("end") == tag:
                    meta["end"] = None
                    meta["end_anchor"] = None
        self._refresh_anchors()

    def _diagram_double(self, event):
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x - 2, y - 2, x + 2, y + 2)
        for item in reversed(items):
            tags = self.canvas.gettags(item)
            if tags and tags[0] in self._shapes:
                meta = self._shapes[tags[0]]
                if meta["kind"] == "text":
                    actual = self.canvas.find_withtag(tags[0])
                    item = actual[0] if actual else item
                    new = simpledialog.askstring(
                        "Editar texto", "Texto:",
                        initialvalue=self.canvas.itemcget(item, "text"),
                        parent=self)
                    if new is not None:
                        self.canvas.itemconfig(item, text=new)
                self._focus_canvas()
                return

    def _select(self, tag):
        self._deselect()
        if not tag or tag not in self._shapes:
            return
        self._selected = tag
        self._selected_tag = tag
        self._show_selection(tag)

    def _deselect(self):
        self._selected = None
        self._selected_tag = None
        self.canvas.delete("selection")

    def _show_selection(self, tag):
        self.canvas.delete("selection")
        bbox = self.canvas.bbox(tag)
        if bbox:
            x0, y0, x1, y1 = bbox
            self.canvas.create_rectangle(x0 - 5, y0 - 5, x1 + 5, y1 + 5,
                                         outline="#e03131", dash=(5, 3), width=2,
                                         tags="selection")
            self.canvas.tag_raise("selection")

    def _delete_selected(self, event=None):
        if self._selected_tag:
            self._delete_shape(self._selected_tag)

    def _clear_diagram(self):
        if not self._shapes:
            return
        if messagebox.askyesno(APP_NAME, "¿Borrar todo el diagrama?"):
            self.canvas.delete("all")
            self._shapes.clear()
            self._selected = None
            self._selected_tag = None
            self._refresh_anchors()
        self._focus_canvas()

    def _save_diagram(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Diagrama AlgoNotas", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        order = list(self._shapes.keys())
        index = {tag: i for i, tag in enumerate(order)}
        data = []
        for tag in order:
            meta = self._shapes[tag]
            items = self.canvas.find_withtag(tag)
            if not items:
                continue
            item = items[0]
            if meta["kind"] == "figure":
                data.append({
                    "kind": "figure", "figure": meta["figure"],
                    "center": list(meta["center"]), "color": meta["color"],
                    "fill": meta["fill"], "outline": meta["outline"],
                })
                continue
            entry = {"kind": meta["kind"], "color": meta["color"],
                     "coords": list(self.canvas.coords(item))}
            if meta["kind"] in ("oval", "rect"):
                entry["fill"] = meta.get("fill", "")
                entry["outline"] = meta.get("outline", "#1f2328")
                entry["width"] = meta.get("width", 2)
            if meta["kind"] == "text":
                entry["text"] = self.canvas.itemcget(item, "text")
            if meta["kind"] == "arrow":
                entry["start"] = index.get(meta.get("start"))
                entry["end"] = index.get(meta.get("end"))
                entry["start_anchor"] = meta.get("start_anchor")
                entry["end_anchor"] = meta.get("end_anchor")
            data.append(entry)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"shapes": data}, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"No se pudo guardar:\n{exc}")
        self._focus_canvas()

    def _open_diagram(self):
        path = filedialog.askopenfilename(
            filetypes=[("Diagrama AlgoNotas", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"No se pudo abrir:\n{exc}")
            return
        self.canvas.delete("all")
        self._shapes.clear()
        self._selected = None
        self._selected_tag = None

        shapes_data = data.get("shapes", [])
        tag_by_index = {}
        for i, shape in enumerate(shapes_data):
            kind = shape.get("kind")
            color = shape.get("color", "#4c8dff")
            coords = shape.get("coords", [])
            tag = f"shape{self._shape_counter}"
            self._shape_counter += 1
            if kind == "figure":
                fig = shape.get("figure")
                if fig not in FIGURE_DRAW:
                    continue
                cx, cy = shape.get("center", [0, 0])
                fill = shape.get("fill", "")
                FIGURE_DRAW[fig](self.canvas, cx, cy, tag, color, fill)
                self._shapes[tag] = {
                    "kind": "figure", "color": color, "item": None,
                    "fill": fill, "outline": color, "width": 2,
                    "start": None, "end": None,
                    "start_anchor": None, "end_anchor": None,
                    "figure": fig, "center": (cx, cy),
                }
                tag_by_index[i] = tag
                continue
            if kind == "oval":
                item = self.canvas.create_oval(
                    *coords, fill=shape.get("fill", color),
                    outline=shape.get("outline", "#1f2328"),
                    width=shape.get("width", 2))
            elif kind == "rect":
                item = self.canvas.create_rectangle(
                    *coords, fill=shape.get("fill", color),
                    outline=shape.get("outline", "#1f2328"),
                    width=shape.get("width", 2))
            elif kind == "arrow":
                item = self.canvas.create_line(*coords, arrow="last", fill=color,
                                               width=3, arrowshape=(14, 18, 6))
            elif kind == "text":
                item = self.canvas.create_text(*coords, text=shape.get("text", ""),
                                               fill=color,
                                               font=("Segoe UI", 13, "bold"))
            else:
                continue
            self.canvas.itemconfig(item, tags=(tag,))
            self._shapes[tag] = {
                "kind": kind, "color": color, "item": item,
                "fill": shape.get("fill", ""),
                "outline": shape.get("outline", "#1f2328"),
                "width": shape.get("width", 2),
                "start": None, "end": None,
                "start_anchor": None, "end_anchor": None,
            }
            tag_by_index[i] = tag

        for i, shape in enumerate(shapes_data):
            if shape.get("kind") != "arrow":
                continue
            meta = self._shapes.get(tag_by_index.get(i))
            if not meta:
                continue
            start = shape.get("start")
            end = shape.get("end")
            meta["start"] = tag_by_index.get(start) if start is not None else None
            meta["end"] = tag_by_index.get(end) if end is not None else None
            meta["start_anchor"] = shape.get("start_anchor")
            meta["end_anchor"] = shape.get("end_anchor")
            self._update_arrow(tag_by_index[i])
        self._refresh_anchors()
        self._focus_canvas()

    def _bind_events(self):
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", self._on_key)
        self.text.bind("<ButtonRelease-1>", self._on_key)
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.linenumbers.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<KeyPress>", self._on_keypress, add="+")

        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-S>", lambda e: self.save_file_as())
        self.bind_all("<F5>", lambda e: self.run_code())
        self.bind_all("<Control-plus>", lambda e: self.change_font(1))
        self.bind_all("<Control-equal>", lambda e: self.change_font(1))
        self.bind_all("<Control-minus>", lambda e: self.change_font(-1))
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------- theming
    def apply_theme(self):
        self.theme_name = self.theme_var.get()
        t = THEMES[self.theme_name]

        self.configure(bg=t["bg"])
        self.toolbar.configure(bg=t["toolbar_bg"])
        self.run_button.configure(bg=t["accent"], fg="#ffffff",
                                  activebackground=t["accent"],
                                  activeforeground="#ffffff")
        for child in self.toolbar.winfo_children():
            if child is not self.run_button:
                child.configure(bg=t["toolbar_bg"], fg=t["toolbar_fg"],
                                activebackground=t["accent"],
                                activeforeground="#ffffff")

        self.editor_frame.configure(bg=t["gutter_bg"])
        self.linenumbers.configure(bg=t["gutter_bg"], fg=t["gutter_fg"],
                                   font=("Consolas", self.font_size))
        self.text.configure(bg=t["bg"], fg=t["fg"], insertbackground=t["cursor"],
                            selectbackground=t["select"], selectforeground=t["fg"],
                            font=("Consolas", self.font_size))
        self.output_panel.configure(bg=t["output_bg"])
        self.output_label.configure(bg=t["output_bg"], fg=t["accent"],
                                    font=("Segoe UI", 9, "bold"))
        self.output.configure(bg=t["output_bg"], fg=t["fg"],
                              font=("Consolas", self.font_size - 1))
        self.status.configure(bg=t["gutter_bg"], fg=t["gutter_fg"],
                              font=("Segoe UI", 9))

        self.code_page.configure(bg=t["bg"])
        self.diagram_page.configure(bg=t["bg"])
        self.diagram_toolbar.configure(bg=t["toolbar_bg"])
        keep = set(self.color_buttons.values()) | set(self.tool_buttons.values())
        for child in self.diagram_toolbar.winfo_children():
            if child not in keep:
                child.configure(bg=t["toolbar_bg"], fg=t["toolbar_fg"],
                                activebackground=t["accent"],
                                activeforeground="#ffffff")
        self._style_diagram_buttons()

        self.text.tag_configure("keyword", foreground=t["keyword"])
        self.text.tag_configure("builtin", foreground=t["builtin"])
        self.text.tag_configure("string", foreground=t["string"])
        self.text.tag_configure("comment", foreground=t["comment"],
                                font=("Consolas", self.font_size, "italic"))
        self.text.tag_configure("number", foreground=t["number"])
        self.text.tag_configure("function", foreground=t["function"])
        self.text.tag_configure("classname", foreground=t["classname"],
                                font=("Consolas", self.font_size, "bold"))
        self.text.tag_configure("decorator", foreground=t["decorator"])
        self.text.tag_configure("operator", foreground=t["operator"])
        self.text.tag_configure("punct", foreground=t["punct"])
        self.text.tag_configure("self", foreground=t["self"],
                                font=("Consolas", self.font_size, "italic"))
        self.text.tag_configure("params", foreground=t["params"])
        for i, color in enumerate(t["brackets"]):
            self.text.tag_configure(f"bracket{i}", foreground=color,
                                    font=("Consolas", self.font_size, "bold"))
        self.text.tag_configure("current_line", background=t["line_highlight"])

        self._schedule_highlight()

    def _on_scroll(self, *args):
        self.text.yview(*args)
        self.linenumbers.yview(*args)

    def _on_yscroll(self, first, last):
        self.vscroll.set(first, last)
        self.linenumbers.yview_moveto(first)
        self.text.yview_moveto(first)

    def _on_mousewheel(self, event):
        if event.state & 0x0004:
            self.change_font(1 if event.delta > 0 else -1)
            return "break"
        delta = -1 if event.delta > 0 else 1
        self.text.yview_scroll(delta, "units")
        self.linenumbers.yview_scroll(delta, "units")
        return "break"

    # ---------------------------------------------------------- line numbers
    def _update_line_numbers(self):
        count = int(self.text.index("end-1c").split(".")[0])
        digits = max(3, len(str(count)))
        self.linenumbers.configure(width=digits)

        self.linenumbers.configure(state="normal")
        self.linenumbers.delete("1.0", "end")
        numbers = "\n".join(str(i) for i in range(1, count + 1))
        self.linenumbers.insert("1.0", numbers)
        self.linenumbers.tag_configure("right", justify="right")
        self.linenumbers.tag_add("right", "1.0", "end")
        self.linenumbers.configure(state="disabled")
        self._highlight_current_line()

    def _highlight_current_line(self):
        self.text.tag_remove("current_line", "1.0", "end")
        if self.text.index("insert") != "end":
            self.text.tag_add("current_line", "insert linestart", "insert lineend+1c")
        self.text.tag_lower("current_line")

    # ------------------------------------------------------------ editing
    def _on_modified(self, event):
        if self.text.edit_modified():
            self.dirty = True
            self.text.edit_modified(False)
            self._schedule_lines()

    def _on_key(self, event=None):
        self._schedule_lines()
        self._update_status()
        self._update_line_numbers()

    def _schedule_lines(self):
        if self._line_job:
            self.after_cancel(self._line_job)
        self._line_job = self.after(60, self._update_line_numbers)

    def _update_status(self):
        line, col = self.text.index("insert").split(".")
        extras = f"  ·  {'*' if self.dirty else '✓'}"
        self.status.configure(text=f"Ln {line}, Col {int(col) + 1}{extras}")

    def _on_return(self, event):
        line = self.text.get("insert linestart", "insert")
        query = re.fullmatch(r"[ \t]*\?\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]*)", line)
        if query:
            self.show_concept(query.group(1))
        indent = re.match(r"[ \t]*", line).group(0)
        extra = "    " if line.rstrip().endswith(":") else ""
        self.text.insert("insert", "\n" + indent + extra)
        self._schedule_lines()
        self._schedule_highlight()
        return "break"

    def _on_keypress(self, event):
        ch = event.char
        if ch in "([{" and not self.text.tag_ranges("sel"):
            close = {"(": ")", "[": "]", "{": "}"}[ch]
            self.text.insert("insert", ch + close)
            self.text.mark_set("insert", "insert-1c")
            return "break"
        if ch in "\"'" and not self.text.tag_ranges("sel"):
            nxt = self.text.get("insert", "insert+1c")
            self.text.insert("insert", ch * 2)
            self.text.mark_set("insert", "insert-1c")
            return "break"
        return None

    # ------------------------------------------------------- highlighting
    def _schedule_highlight(self):
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(120, self.highlight)

    def highlight(self, event=None):
        code = self.text.get("1.0", "end-1c")
        tags = ("keyword", "builtin", "string", "comment", "number", "function",
                "classname", "decorator", "operator", "punct", "self", "params",
                "bracket0", "bracket1", "bracket2", "bracket3")
        for tag in tags:
            self.text.tag_remove(tag, "1.0", "end")

        spans = []

        for m in re.finditer(r"#.*$", code, re.MULTILINE):
            self.text.tag_add("comment", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
            spans.append((m.start(), m.end()))

        for m in re.finditer(
            r"('''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")",
            code,
        ):
            self.text.tag_add("string", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
            spans.append((m.start(), m.end()))

        exempt = []
        fstring = re.compile(
            r"[fF](?:'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\""
            r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")"
        )
        for m in fstring.finditer(code):
            base = m.start()
            body = m.group(0)
            for b in re.finditer(r"\{[^{}]*\}", body):
                exempt.append((base + b.start(), base + b.end()))

        def inside(pos):
            if any(a <= pos < b for a, b in spans):
                return not any(a <= pos < b for a, b in exempt)
            return False

        def add(tag, start, end):
            self.text.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

        kw = "|".join(PYTHON_KEYWORDS)
        for m in re.finditer(rf"\b({kw})\b", code):
            if inside(m.start()):
                continue
            if m.group(1) == "self":
                add("self", m.start(), m.end())
            else:
                add("keyword", m.start(), m.end())

        bl = "|".join(PYTHON_BUILTINS)
        for m in re.finditer(rf"\b({bl})\b(?=\s*\()", code):
            if not inside(m.start()):
                add("builtin", m.start(), m.end())

        for m in re.finditer(r"\b\d+(\.\d+)?\b", code):
            if not inside(m.start()):
                add("number", m.start(), m.end())

        for m in re.finditer(r"\b(?:def|class)\s+(\w+)", code):
            tag = "function" if m.group(0).startswith("def") else "classname"
            if not inside(m.start(1)):
                add(tag, m.start(1), m.end(1))

        for m in re.finditer(r"@\w+(?:\.\w+)*", code):
            if not inside(m.start()):
                add("decorator", m.start(), m.end())

        for m in re.finditer(r"\bdef\s+\w+\s*\(([^)]*)\)", code):
            group_start = m.start(1)
            for p in re.finditer(r"[A-Za-z_]\w*", m.group(1)):
                pos = group_start + p.start()
                if not inside(pos):
                    add("params", pos, group_start + p.end())

        for m in re.finditer(r"(\*\*|//|<<|>>|<=|>=|==|!=|->|:=|[-+*/%=<>!&|^~])", code):
            if not inside(m.start()):
                add("operator", m.start(), m.end())

        for m in re.finditer(r"(?<!\d)\.(?!\d)", code):
            if not inside(m.start()):
                add("operator", m.start(), m.end())

        for m in re.finditer(r"[,:;]", code):
            if not inside(m.start()):
                add("punct", m.start(), m.end())

        stack = []
        pairs = {")": "(", "]": "[", "}": "{"}
        ncolors = len(THEMES[self.theme_name]["brackets"])
        for i, ch in enumerate(code):
            if ch not in "([{)]}":
                continue
            if inside(i):
                continue
            if ch in "([{":
                idx = len(stack) % ncolors
                add(f"bracket{idx}", i, i + 1)
                stack.append(ch)
            else:
                if stack:
                    stack.pop()
                idx = len(stack) % ncolors
                add(f"bracket{idx}", i, i + 1)

        self._highlight_current_line()

    # ----------------------------------------------------------- file ops
    def _confirm_discard(self):
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel(
            APP_NAME, "Hay cambios sin guardar. ¿Deseas guardarlos?")
        if answer is None:
            return False
        if answer:
            return self.save_file()
        return True

    def new_file(self):
        if not self._confirm_discard():
            return
        self.text.delete("1.0", "end")
        self.current_file = None
        self.dirty = False
        self.text.edit_modified(False)
        self.title(f"{APP_NAME} - Sin título")
        self._update_line_numbers()
        self._schedule_highlight()

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[("Python", "*.py"), ("Texto", "*.txt"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"No se pudo abrir el archivo:\n{exc}")
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.current_file = path
        self.dirty = False
        self.text.edit_modified(False)
        self.title(f"{APP_NAME} - {os.path.basename(path)}")
        self._update_line_numbers()
        self._schedule_highlight()

    def save_file(self):
        if self.current_file is None:
            return self.save_file_as()
        return self._write(self.current_file)

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python", "*.py"), ("Texto", "*.txt"), ("Todos", "*.*")])
        if not path:
            return False
        return self._write(path)

    def _write(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"No se pudo guardar:\n{exc}")
            return False
        self.current_file = path
        self.dirty = False
        self.text.edit_modified(False)
        self.title(f"{APP_NAME} - {os.path.basename(path)}")
        self._update_status()
        return True

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "1.0")
        return "break"

    # ------------------------------------------------------------- running
    def run_code(self):
        code = self.text.get("1.0", "end-1c")
        query = re.fullmatch(r"\s*\?\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]*)\s*", code)
        if query:
            self.show_concept(query.group(1))
            return
        if not code.strip():
            self._set_output("No hay código para ejecutar.\n")
            return
        interpreter = find_python()
        self._set_output("▶ Ejecutando...\n\n")
        if interpreter:
            tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                              encoding="utf-8")
            tmp.write(code)
            tmp.close()
            threading.Thread(target=self._execute,
                             args=(tmp.name, interpreter), daemon=True).start()
        else:
            threading.Thread(target=self._execute_inprocess,
                             args=(code,), daemon=True).start()

    def _execute(self, path, interpreter):
        try:
            env = dict(os.environ, PYTHONIOENCODING="utf-8")
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            result = subprocess.run(
                [interpreter, path], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=30, env=env,
                creationflags=flags)
            out = result.stdout or ""
            err = result.stderr or ""
            text = out
            if err:
                text += ("\n--- Errores ---\n" if out else "") + err
            if not text:
                text = "(el programa no produjo salida)\n"
            text += f"\n● Proceso finalizado (código {result.returncode})\n"
        except subprocess.TimeoutExpired:
            text = "⏱ Tiempo agotado (30s). ¿Hay un bucle infinito?\n"
        except Exception as exc:
            text = f"No se pudo ejecutar: {exc}\n"
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
        self._output_queue.put(text)

    def _execute_inprocess(self, code):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                exec(compile(code, "<AlgoNotas>", "exec"), {"__name__": "__main__"})
            text = buf.getvalue() or "(el programa no produjo salida)\n"
            text += "\n● Ejecutado en modo interno (input() no disponible).\n"
        except Exception:
            text = buf.getvalue() + "\n--- Errores ---\n" + traceback.format_exc()
        self._output_queue.put(text)

    def _poll_output(self):
        latest = None
        try:
            while True:
                latest = self._output_queue.get_nowait()
        except queue.Empty:
            pass
        if latest is not None:
            self._set_output(latest)
        if self.winfo_exists():
            self.after(80, self._poll_output)

    def _set_output(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")

    def clear_output(self):
        self._set_output("")

    # ---------------------------------------------------------- conceptos
    def show_concept(self, word):
        word = word.strip()
        if not word:
            self._set_output(self._concept_list())
            return
        concept = lookup_concept(word)
        if concept is None:
            text = (f"❓ Todavía no conozco «{word}».\n\n"
                    + self._concept_list())
            self._set_output(text)
            return
        title, definition, example = concept
        text = f"📘  {title.upper()}\n" + "─" * 44 + f"\n\n{definition}\n"
        if example:
            text += f"\nEjemplo:\n   {example}\n"
        text += ("\n" + "─" * 44 +
                 "\n💡 Escribe ?palabra (y Enter) para otro concepto · "
                 "? para la lista completa.\n")
        self._set_output(text)

    def _concept_list(self):
        words = ", ".join(sorted(GLOSSARY))
        return ("📚  CONCEPTOS DISPONIBLES\n" + "─" * 44 + "\n\n"
                + words + "\n\n"
                "Escribe ?palabra y presiona Enter (o F5) para ver su "
                "definición.\nEjemplo:  ?algoritmo\n")

    # --------------------------------------------------------------- misc
    def change_font(self, delta):
        self.font_size = max(9, min(32, self.font_size + delta))
        self.apply_theme()

    def show_about(self):
        messagebox.showinfo(
            APP_NAME,
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Bloc de notas divertido para ideas y código Python.\n"
            "Colores, paréntesis arcoíris y ejecución con F5.\n\n"
            "Escribe ?palabra y pulsa Enter para ver un concepto.\n"
            "Ejemplos: ?algoritmo · ?slice · ?python · ?funcion\n\n"
            "Pestaña 🔷 Diagrama: dibuja círculos, cajas, textos y flechas.\n"
            "Herramienta Figuras: persona, computadora, base de datos, monitor, "
            "servidor, rombo, nube y documento.\n"
            "Relleno transparente (∅) y flechas que siguen a las formas.\n\n"
            "Atajos diagrama: V mover · C círculo · B caja · T texto · "
            "F flecha · Q borrador · Alt+Q borrar todo\n\n"
            "Atajos: Ctrl+N/O/S · F5 ejecutar · Ctrl+rueda zoom")

    def on_close(self):
        if self._confirm_discard():
            self.destroy()


def main():
    app = Editor()
    app.mainloop()


if __name__ == "__main__":
    main()
