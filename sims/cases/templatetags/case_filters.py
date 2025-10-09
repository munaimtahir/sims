import os
from django import template

register = template.Library()


@register.filter
def basename(value):
    """Return the basename of a file path"""
    if value:
        return os.path.basename(str(value))
    return value
