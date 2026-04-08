"""
Custom template tags for simple translation and utility filters
"""
from django import template
from apps.core.translation_utils import simple_trans

register = template.Library()

@register.simple_tag
def trans(text):
    """Custom trans tag that works without gettext compilation"""
    return simple_trans(text)

@register.filter
def trans_filter(text):
    """Custom trans filter that works without gettext compilation"""
    return simple_trans(text)

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def announcement_title(announcement):
    """Get announcement title in current language"""
    from django.utils.translation import get_language
    lang = get_language()
    if lang and lang.startswith('zh') and announcement.title_zh:
        return announcement.title_zh
    return announcement.title_en
