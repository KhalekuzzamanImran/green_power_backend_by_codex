from django import template

register = template.Library()


@register.filter
def has_role(user, role_code):
    return getattr(user, "role", None) == role_code

