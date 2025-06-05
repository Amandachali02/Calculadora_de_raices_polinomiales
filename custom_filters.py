from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key, default=""):
    """Accede a diccionarios con clave variable y valor por defecto"""
    return dictionary.get(key, default)

@register.filter(name='is_float')
def is_float(value):
    """Determina si un valor es convertible a float"""
    # Caso especial: valores vacíos
    if value in [None, "", "N/A"]:
        return False
        
    try:
        float(value)  # Intenta convertir a float
        return True
    except (TypeError, ValueError):
        return False