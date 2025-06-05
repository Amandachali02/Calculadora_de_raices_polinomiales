from django.shortcuts import render
from .forms import PolinomioForm
from . import metodos_numericos
import numpy as np
import matplotlib.pyplot as plt
import io # Para manejar la imagen en memoria
import base64 # Para codificar la imagen para HTML

def generar_grafica(f, raiz_aprox=None, a=None, b=None, x0=None):
    """Genera una gráfica del polinomio y la raíz/intervalo."""
    try:
        if a is not None and b is not None and raiz_aprox is not None: # Bisección
            x_vals = np.linspace(min(a, raiz_aprox) - 2, max(b, raiz_aprox) + 2, 400)
        elif x0 is not None and raiz_aprox is not None: # Newton
            x_vals = np.linspace(min(x0, raiz_aprox) - 2, max(x0, raiz_aprox) + 2, 400)
        elif raiz_aprox is not None: # Si solo hay raíz pero no intervalo/x0
             x_vals = np.linspace(raiz_aprox - 5, raiz_aprox + 5, 400)
        else: # Si no hay raíz (ej. error antes de calcular)
            # Intenta graficar alrededor de 0 o un rango por defecto
            # Esto podría mejorarse obteniendo un rango del usuario si falla el cálculo
            x_test_points = np.array([-1, 0, 1])
            y_test_points = f(x_test_points)
            if np.all(np.isinf(y_test_points)) or np.all(np.isnan(y_test_points)):
                 return None # No se puede determinar un rango
            # heurística simple:
            center = 0
            if x0 is not None: center = x0
            elif a is not None and b is not None: center = (a+b)/2
            x_vals = np.linspace(center - 5, center + 5, 400)

        y_vals = f(x_vals)

        # Manejar valores infinitos o NaN en y_vals para evitar errores de graficación
        # y_vals = np.nan_to_num(y_vals, nan=0.0, posinf=np.finfo(np.float32).max, neginf=np.finfo(np.float32).min)
        # Una mejor aproximación es limitar el rango de y para evitar plots extremos.
        valid_indices = np.isfinite(y_vals)
        if not np.any(valid_indices): # Si todos los valores son inf/nan
            return None


        # Limitar el rango y para una mejor visualización
        median_y = np.median(y_vals[valid_indices])
        std_y = np.std(y_vals[valid_indices])
        y_min_plot = median_y - 5 * std_y
        y_max_plot = median_y + 5 * std_y
        if raiz_aprox is not None and f(raiz_aprox) < y_min_plot : y_min_plot = f(raiz_aprox) - 1*std_y
        if raiz_aprox is not None and f(raiz_aprox) > y_max_plot : y_max_plot = f(raiz_aprox) + 1*std_y


        plt.figure(figsize=(8, 6))
        plt.plot(x_vals[valid_indices], y_vals[valid_indices], label='f(x)')
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.ylim(y_min_plot, y_max_plot) # Limitar eje Y
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title('Gráfica del Polinomio')

        if raiz_aprox is not None:
            plt.scatter([raiz_aprox], [f(raiz_aprox)], color='red', zorder=5, label=f'Raíz Aprox: {raiz_aprox:.5f}')
        if a is not None and b is not None: # Para Bisección, mostrar intervalo
            plt.axvline(a, color='green', linestyle=':', label=f'Intervalo a={a}')
            plt.axvline(b, color='purple', linestyle=':', label=f'Intervalo b={b}')
        elif x0 is not None: # Para Newton, mostrar x0
             plt.scatter([x0], [f(x0)], color='orange', zorder=5, label=f'x₀ = {x0}')


        plt.legend()

        # Guardar la gráfica en un buffer de memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        # Codificar la imagen en base64 para pasarla al template
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close() # Cerrar la figura para liberar memoria
        return image_base64
    except Exception as e:
        print(f"Error generando gráfica: {e}") # Log para depuración
        return None


def calculadora_view(request):
    context = {'form': PolinomioForm()} # Inicializa el contexto con un formulario vacío

    if request.method == 'POST':
        form = PolinomioForm(request.POST)
        if form.is_valid():
            polinomio_str = form.cleaned_data['polinomio_str']
            metodo = form.cleaned_data['metodo']
            tolerancia = form.cleaned_data['tolerancia']
            max_iteraciones = form.cleaned_data['max_iteraciones']

            f, df, d2f, error_parse = metodos_numericos.parse_polinomio(polinomio_str)

            if error_parse:
                context['error_general'] = error_parse
                context['form'] = form # Reenviar el formulario con los datos ingresados
                return render(request, 'calculadora_raices/calculadora.html', context)

            raiz_aprox = None
            iteraciones_data = []
            error_metodo = None
            grafica_b64 = None
            params_usados = {} # Para mostrar en la plantilla qué parámetros se usaron

            try:
                if metodo == 'biseccion':
                    a = form.cleaned_data['a']
                    b = form.cleaned_data['b']
                    params_usados = {'a':a, 'b':b}
                    raiz_aprox, iteraciones_data, error_metodo = metodos_numericos.biseccion(
                        f, a, b, tolerancia, max_iteraciones
                    )
                    if not error_metodo:
                         grafica_b64 = generar_grafica(f, raiz_aprox, a=a, b=b)

                elif metodo == 'newton_raphson':
                    x0 = form.cleaned_data['x0']
                    params_usados = {'x0':x0}
                    raiz_aprox, iteraciones_data, error_metodo = metodos_numericos.newton_raphson(
                        f, df, x0, tolerancia, max_iteraciones
                    )
                    if not error_metodo:
                        grafica_b64 = generar_grafica(f, raiz_aprox, x0=x0)

                elif metodo == 'newton_raphson_modificado':
                    x0 = form.cleaned_data['x0']
                    params_usados = {'x0':x0}
                    raiz_aprox, iteraciones_data, error_metodo = metodos_numericos.newton_raphson_modificado(
                        f, df, d2f, x0, tolerancia, max_iteraciones
                    )
                    if not error_metodo:
                        grafica_b64 = generar_grafica(f, raiz_aprox, x0=x0)
                
                # Si no se pudo generar gráfica antes (ej. por error en el método), intentar de todas formas
                if not grafica_b64 and f:
                    grafica_b64 = generar_grafica(f, raiz_aprox, **params_usados)


            except Exception as e: # Captura errores inesperados en los métodos o graficación
                error_metodo = f"Ocurrió un error inesperado durante el cálculo: {str(e)}"


            context.update({
                'form': form, # Pasar el formulario (con datos) de vuelta
                'polinomio_str': polinomio_str,
                 'metodo_seleccionado': dict(form.fields['metodo'].choices)[metodo],
                'raiz_aprox': raiz_aprox,
                'iteraciones_data': iteraciones_data,
                'error_metodo': error_metodo,
                'grafica_b64': grafica_b64,
                'columnas_tabla': [], # Se llenará dinámicamente en el template o aquí
                'params_usados': params_usados,
                'tolerancia_usada': tolerancia,
                'max_iter_usadas': max_iteraciones
            })

            # Definir columnas de la tabla según el método
            if metodo == 'biseccion':
                context['columnas_tabla'] = ['n', 'a', 'b', 'c', 'f(c)', 'error_abs', 'error_rel']
            elif metodo in ['newton_raphson', 'newton_raphson_modificado']:
                cols = ['n', 'xi', 'f(xi)', 'df(xi)']
                if metodo == 'newton_raphson_modificado':
                    cols.append('d2f(xi)')
                cols.extend(['x_next', 'error_abs', 'error_rel'])
                context['columnas_tabla'] = cols

        else: # El formulario no es válido
            context['form'] = form # Pasa el formulario con errores de validación
            context['error_general'] = "Por favor, corrige los errores en el formulario."

    # Si es una solicitud GET o el formulario no era POST, simplemente renderiza la página con el formulario vacío o con errores.
    return render(request, 'calculadora_raices/calculadora.html', context)


