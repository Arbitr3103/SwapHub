from django import template
from pprint import pformat  # Импортируем pformat из модуля pprint

register = template.Library()

@register.filter
def pprint(value):
    return pformat(value)

