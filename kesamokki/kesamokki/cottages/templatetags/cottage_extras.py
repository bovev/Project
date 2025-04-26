from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string and return the given index"""
    return value.split(arg)