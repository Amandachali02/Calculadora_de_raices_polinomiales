from django import forms    

METODOS_CHOICES = [
    ('biseccion', 'Bisección'),
    ('newton_raphson', 'Newton-Raphson'),
    ('newton_raphson_modificado', 'Newton-Raphson Modificado'),
]

class PolinomioForm(forms.Form):
    polinomio_str = forms.CharField(
        label='Función Polinómica (ej: x**3 - 2*x - 5)',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'x**3 - 2*x + 1'})  # Corregido aquí
    )
    metodo = forms.ChoiceField(
        label='Método Numérico',
        choices=METODOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'metodoSelect'})
    )

    # Parámetros para Bisección
    a = forms.FloatField(
        label='Extremo inferior del intervalo [a]',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control biseccion-param'})
    )
    b = forms.FloatField(
        label='Extremo superior del intervalo [b]',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control biseccion-param'})
    )

    # Parámetros para Newton-Raphson y Modificado
    x0 = forms.FloatField(
        label='Valor inicial x₀',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control newton-param newton-mod-param'})
    )

    # Parámetros comunes
    tolerancia = forms.FloatField(
        label='Tolerancia (error permitido)',
        initial=0.0001,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00001'})
    )
    max_iteraciones = forms.IntegerField(
        label='Máximo número de iteraciones',
        initial=100,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')

        if metodo == 'biseccion':
            if cleaned_data.get('a') is None or cleaned_data.get('b') is None:
                raise forms.ValidationError("Para Bisección, los campos 'a' y 'b' son requeridos.")
            if cleaned_data.get('a') is not None and cleaned_data.get('b') is not None and cleaned_data.get('a') >= cleaned_data.get('b'):
                raise forms.ValidationError("En Bisección, 'a' debe ser menor que 'b'.")
        elif metodo in ['newton_raphson', 'newton_raphson_modificado']:
            if cleaned_data.get('x0') is None:
                raise forms.ValidationError(f"Para {dict(METODOS_CHOICES)[metodo]}, el valor inicial 'x₀' es requerido.")
        return cleaned_data