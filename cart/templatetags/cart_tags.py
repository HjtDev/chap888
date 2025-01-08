from django import template

register = template.Library()

@register.simple_tag
def selected(options: dict, item: str) -> str:
    if item in options.values():
        return 'selected'
    return ''
