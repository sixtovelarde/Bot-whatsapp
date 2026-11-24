import ast
import operator
import tkinter as tk

# --- 1. MOTOR DE CONVERSIÓN DE NÚMEROS A LETRAS (ESPAÑOL) ---

UNIDADES = (
    "cero", "uno", "dos", "tres", "cuatro",
    "cinco", "seis", "siete", "ocho", "nueve"
)

ESPECIALES_10_29 = {
    10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce",
    15: "quince", 16: "dieciséis", 17: "diecisiete", 18: "dieciocho", 19: "diecinueve",
    20: "veinte", 21: "veintiuno", 22: "veintidós", 23: "veintitrés", 24: "veinticuatro",
    25: "veinticinco", 26: "veintiséis", 27: "veintisiete", 28: "veintiocho", 29: "veintinueve"
}

DECENAS = {
    30: "treinta", 40: "cuarenta", 50: "cincuenta",
    60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"
}

CENTENAS = {
    100: "ciento", 200: "doscientos", 300: "trescientos", 400: "cuatrocientos",
    500: "quinientos", 600: "seiscientos", 700: "setecientos", 800: "ochocientos",
    900: "novecientos"
}


def entero_menor_1000(n: int) -> str:
    """Convierte enteros de 0 a 999 a letras."""
    if n < 10:
        return UNIDADES[n]
    if n < 30:
        return ESPECIALES_10_29[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DECENAS[d * 10] if u == 0 else f"{DECENAS[d * 10]} y {UNIDADES[u]}"
    if n == 100:
        return "cien"
    c, resto = divmod(n, 100)
    return CENTENAS[c * 100] if resto == 0 else f"{CENTENAS[c * 100]} {entero_menor_1000(resto)}"


def entero_a_letras(n: int) -> str:
    """Convierte enteros grandes (hasta millones) a letras."""
    if n == 0:
        return "cero"
    if n < 0:
        return f"menos {entero_a_letras(abs(n))}"
    if n < 1000:
        return entero_menor_1000(n)
    if n < 1_000_000:
        miles, resto = divmod(n, 1000)
        prefijo = "mil" if miles == 1 else f"{entero_menor_1000(miles)} mil"
        return prefijo if resto == 0 else f"{prefijo} {entero_menor_1000(resto)}"
    if n < 1_000_000_000:
        millones, resto = divmod(n, 1_000_000)
        prefijo = "un millón" if millones == 1 else f"{entero_a_letras(millones)} millones"
        return prefijo if resto == 0 else f"{prefijo} {entero_a_letras(resto)}"
    return str(n)


def numero_a_letras(valor: float) -> str:
    """Convierte enteros o decimales a texto legible en español."""
    if valor == int(valor):
        return entero_a_letras(int(valor))

    # Redondeo limpio a máximo 4 decimales para evitar basura flotante (ej. 0.30000000004)
    texto_num = f"{valor:.4f}".rstrip("0").rstrip(".")
    negativo = texto_num.startswith("-")
    if negativo:
        texto_num = texto_num[1:]

    parte_entera, parte_decimal = texto_num.split(".")
    letras_entera = entero_a_letras(int(parte_entera))

    # Lee los decimales dígito a dígito si empiezan por 0 (ej. .05 -> cero cinco) o como número
    if parte_decimal.startswith("0") and len(parte_decimal) > 1:
        letras_decimal = " ".join(UNIDADES[int(d)] for d in parte_decimal)
    else:
        letras_decimal = entero_a_letras(int(parte_decimal))

    resultado = f"{letras_entera} punto {letras_decimal}"
    return f"menos {resultado}" if negativo else resultado


# --- 2. EVALUADOR ARITMÉTICO SEGURO (SIN USAR eval() DIRECTO) ---

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluar_expresion(expr: str) -> float:
    """Evalúa operaciones aritméticas básicas (+, -, *, /) de forma segura."""
    expr = expr.replace("×", "*").replace("÷", "/").replace(",", ".")
    nodo = ast.parse(expr, mode="eval").body

    def _eval(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in OPERADORES:
            izq = _eval(n.left)
            der = _eval(n.right)
            if isinstance(n.op, ast.Div) and der == 0:
                raise ZeroDivisionError("División entre cero")
            return OPERADORES[type(n.op)](izq, der)
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPERADORES:
            return OPERADORES[type(n.op)](_eval(n.operand))
        raise ValueError("Operación no válida")

    return _eval(nodo)


# --- 3. INTERFAZ MINIMALISTA TIPO CALCULADORA ESTÁNDAR ---

class CalculadoraBot:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CalcBot")
        self.root.geometry("300x430")
        self.root.resizable(False, False)
        self.root.configure(bg="#18181b")

        self.expresion = ""

        # Pantalla superior: operación ingresada
        self.var_operacion = tk.StringVar(value="")
        lbl_op = tk.Label(
            root,
            textvariable=self.var_operacion,
            anchor="e",
            bg="#18181b",
            fg="#a1a1aa",
            font=("Segoe UI", 11),
            padx=16
        )
        lbl_op.pack(fill="x", pady=(14, 0))

        # Pantalla principal: respuesta del bot en letras
        self.var_resultado = tk.StringVar(value="cero")
        lbl_res = tk.Label(
            root,
            textvariable=self.var_resultado,
            anchor="e",
            justify="right",
            wraplength=268,
            bg="#18181b",
            fg="#f4f4f5",
            font=("Segoe UI", 17, "bold"),
            height=2,
            padx=16
        )
        lbl_res.pack(fill="x", pady=(2, 10))

        # Contenedor de botones
        frame_botones = tk.Frame(root, bg="#18181b", padx=10, pady=6)
        frame_botones.pack(expand=True, fill="both")

        botones = [
            ["C", "⌫", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="]
        ]

        # Fila 0 (C ocupa 2 columnas)
        self._crear_boton(frame_botones, "C", 0, 0, colspan=2, bg="#27272a", fg="#f87171")
        self._crear_boton(frame_botones, "⌫", 0, 2, bg="#27272a")
        self._crear_boton(frame_botones, "÷", 0, 3, bg="#27272a", fg="#60a5fa")

        # Filas 1 a 3
        for r in range(1, 4):
            for c, texto in enumerate(botones[r]):
                es_op = texto in ("×", "-", "+")
                self._crear_boton(
                    frame_botones,
                    texto,
                    r,
                    c,
                    bg="#27272a" if es_op else "#202024",
                    fg="#60a5fa" if es_op else "#f4f4f5"
                )

        # Fila 4 (0 ocupa 2 columnas, = resaltado en azul)
        self._crear_boton(frame_botones, "0", 4, 0, colspan=2, bg="#202024")
        self._crear_boton(frame_botones, ".", 4, 2, bg="#202024")
        self._crear_boton(frame_botones, "=", 4, 3, bg="#2563eb", fg="#ffffff")

        for i in range(5):
            frame_botones.rowconfigure(i, weight=1)
        for j in range(4):
            frame_botones.columnconfigure(j, weight=1)

        # Soporte para teclado físico
        self.root.bind("<Key>", self._teclado)

    def _crear_boton(self, parent, texto, fila, col, colspan=1, bg="#202024", fg="#f4f4f5"):
        btn = tk.Button(
            parent,
            text=texto,
            font=("Segoe UI", 13, "bold" if texto == "=" else "normal"),
            bg=bg,
            fg=fg,
            activebackground="#3f3f46",
            activeforeground="#ffffff",
            bd=0,
            cursor="hand2",
            command=lambda t=texto: self._al_pulsar(t)
        )
        btn.grid(row=fila, column=col, columnspan=colspan, sticky="nsew", padx=3, pady=3)

    def _al_pulsar(self, tecla: str):
        if tecla == "C":
            self.expresion = ""
            self.var_operacion.set("")
            self.var_resultado.set("cero")
            return

        if tecla == "⌫":
            self.expresion = self.expresion[:-1]
            self.var_operacion.set(self.expresion)
            if not self.expresion:
                self.var_resultado.set("cero")
            return

        if tecla == "=":
            self._calcular()
            return

        self.expresion += tecla
        self.var_operacion.set(self.expresion)

    def _calcular(self):
        if not self.expresion:
            return
        try:
            resultado_num = evaluar_expresion(self.expresion)
            respuesta_bot = numero_a_letras(resultado_num)
            self.var_operacion.set(f"{self.expresion} =")
            self.var_resultado.set(respuesta_bot)
            # Guarda el resultado numérico por si quieres seguir operando encima
            self.expresion = (
                str(int(resultado_num))
                if resultado_num == int(resultado_num)
                else str(round(resultado_num, 4))
            )
        except ZeroDivisionError:
            self.var_resultado.set("no se puede dividir entre cero")
            self.expresion = ""
        except Exception:
            self.var_resultado.set("operación inválida")
            self.expresion = ""

    def _teclado(self, event):
        tecla = event.char
        if tecla in "0123456789.+-*/":
            mapa = {"*": "×", "/": "÷"}
            self._al_pulsar(mapa.get(tecla, tecla))
        elif event.keysym in ("Return", "KP_Enter"):
            self._al_pulsar("=")
        elif event.keysym == "BackSpace":
            self._al_pulsar("⌫")
        elif event.keysym == "Escape":
            self._al_pulsar("C")


if __name__ == "__main__":
    ventana = tk.Tk()
    app = CalculadoraBot(ventana)
    ventana.mainloop()