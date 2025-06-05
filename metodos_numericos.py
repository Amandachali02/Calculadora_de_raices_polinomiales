import numpy as np
import sympy

# Preparamos el símbolo 'x' que usaremos en SymPy
x_sym = sympy.symbols('x')

def parse_polinomio(poly_str):
    """
    Convierte una cadena de texto de un polinomio en una función evaluable
    y su derivada (si es posible).
    Retorna (funcion, derivada_func, error_str)
    """
    try:
        # Convertir la cadena a una expresión SymPy
        expr = sympy.sympify(poly_str)

        # Crear funciones evaluables (lambdify)
        # 'numpy' permite que estas funciones trabajen con arrays de NumPy
        f = sympy.lambdify(x_sym, expr, 'numpy')

        # Calcular la derivada
        deriv_expr = sympy.diff(expr, x_sym)
        df = sympy.lambdify(x_sym, deriv_expr, 'numpy')

        # Para Newton Modificado, necesitamos la segunda derivada
        deriv2_expr = sympy.diff(deriv_expr, x_sym)
        d2f = sympy.lambdify(x_sym, deriv2_expr, 'numpy')

        return f, df, d2f, None # Sin error
    except (sympy.SympifyError, TypeError, SyntaxError) as e:
        return None, None, None, f"Error al interpretar el polinomio: {str(e)}"

def biseccion(f, a, b, tol, max_iter):
    """
    Método de Bisección para encontrar la raíz de f en [a, b].
    Retorna (raiz_aprox, iteraciones_data, error_msg)
    """
    iteraciones_data = [] # Lista para guardar datos de cada iteración
    if f(a) * f(b) >= 0:
        return None, iteraciones_data, "El método de bisección requiere f(a) y f(b) con signos opuestos."

    iter_count = 0
    c_prev = a # o b, solo para calcular el primer error relativo

    while iter_count < max_iter:
        c = (a + b) / 2.0
        fc = f(c)
        error_abs = abs(b - a) / 2.0 # Error absoluto como la mitad del intervalo
        # Para el primer cálculo de error_rel, si c es 0, usamos un valor pequeño o lo manejamos
        error_rel = abs((c - c_prev) / c) * 100 if c != 0 else (float('inf') if c_prev != 0 else 0)


        iter_data = {
            'n': iter_count + 1,
            'a': a,
            'b': b,
            'c': c,
            'f(c)': fc,
            'error_abs': error_abs,
            'error_rel': error_rel if error_rel != float('inf') else "N/A"
        }
        iteraciones_data.append(iter_data)

        if fc == 0 or error_abs < tol: # Condición de paro: raíz encontrada o tolerancia alcanzada
            return c, iteraciones_data, None

        if f(a) * fc < 0:
            b = c
        else:
            a = c

        c_prev = c
        iter_count += 1

    return c, iteraciones_data, "Máximo número de iteraciones alcanzado."

def newton_raphson(f, df, x0, tol, max_iter):
    """
    Método de Newton-Raphson.
    Retorna (raiz_aprox, iteraciones_data, error_msg)
    """
    iteraciones_data = []
    xi = x0
    iter_count = 0

    while iter_count < max_iter:
        f_xi = f(xi)
        df_xi = df(xi)

        if abs(df_xi) < 1e-10: # Evitar división por cero o derivada muy pequeña
            return None, iteraciones_data, "Derivada muy cercana a cero. Posible división por cero."

        x_next = xi - f_xi / df_xi
        error_abs = abs(x_next - xi)
        error_rel = abs((x_next - xi) / x_next) * 100 if x_next != 0 else (float('inf') if xi != 0 else 0)

        iter_data = {
            'n': iter_count + 1,
            'xi': xi,
            'f(xi)': f_xi,
            'df(xi)': df_xi,
            'x_next': x_next,
            'error_abs': error_abs,
            'error_rel': error_rel if error_rel != float('inf') else "N/A"
        }
        iteraciones_data.append(iter_data)

        if error_abs < tol:
            return x_next, iteraciones_data, None

        xi = x_next
        iter_count += 1

    return xi, iteraciones_data, "Máximo número de iteraciones alcanzado."

def newton_raphson_modificado(f, df, d2f, x0, tol, max_iter):
    """
    Método de Newton-Raphson Modificado (para raíces múltiples).
    Retorna (raiz_aprox, iteraciones_data, error_msg)
    """
    iteraciones_data = []
    xi = x0
    iter_count = 0

    while iter_count < max_iter:
        f_xi = f(xi)
        df_xi = df(xi)
        d2f_xi = d2f(xi)

        denominador = df_xi**2 - f_xi * d2f_xi
        if abs(denominador) < 1e-10: # Evitar división por cero
            return None, iteraciones_data, "Denominador muy cercano a cero en Newton Modificado."

        x_next = xi - (f_xi * df_xi) / denominador
        error_abs = abs(x_next - xi)
        error_rel = abs((x_next - xi) / x_next) * 100 if x_next != 0 else (float('inf') if xi != 0 else 0)

        iter_data = {
            'n': iter_count + 1,
            'xi': xi,
            'f(xi)': f_xi,
            'df(xi)': df_xi,
            'd2f(xi)': d2f_xi,
            'x_next': x_next,
            'error_abs': error_abs,
            'error_rel': error_rel if error_rel != float('inf') else "N/A"
        }
        iteraciones_data.append(iter_data)

        if error_abs < tol:
            return x_next, iteraciones_data, None

        xi = x_next
        iter_count += 1

    return xi, iteraciones_data, "Máximo número de iteraciones alcanzado."