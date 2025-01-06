from django import template

register = template.Library()


@register.inclusion_tag('messages.html', takes_context=True)
def render_messages(context, form=None):
    messages = context.get('messages', [])
    form_errors = form.errors if form else {}
    return {'messages': messages, 'form_errors': form_errors}
