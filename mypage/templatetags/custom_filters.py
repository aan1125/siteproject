from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return value / arg
    except (ZeroDivisionError, TypeError):
        return 0  # 나누는 값이 0이거나 잘못된 타입인 경우

@register.filter
def add_one(value):
    return value + 1