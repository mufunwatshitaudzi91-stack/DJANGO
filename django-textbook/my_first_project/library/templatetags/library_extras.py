from django import template

register = template.Library()


@register.filter
def stars(value, max_stars=5):
    """Turn a rating like 4 into ★★★★☆."""
    try:
        value = int(value)
        max_stars = int(max_stars)
    except (TypeError, ValueError):
        return ''
    value = max(0, min(value, max_stars))
    return '★' * value + '☆' * (max_stars - value)