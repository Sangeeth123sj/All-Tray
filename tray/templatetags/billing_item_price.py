from django import template
from tray.models import Item
register = template.Library()

@register.simple_tag(takes_context = True)
def item_price(context,item_name):
    items = context['items']
    item = items.objects.filter(item = item_name)
    item_price = item.price
    return item_price