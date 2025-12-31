from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return ""


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    request = context["request"]
    query = request.GET.copy()

    for key, value in kwargs.items():
        query[key] = value

    return query.urlencode()
