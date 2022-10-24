from datetime import datetime, timedelta

import pytz
from django import template

register = template.Library()


@register.simple_tag
def date_range():
    today_date = datetime.today()
    for n in range(31):
        yield pytz.utc.localize((today_date - timedelta(days=n)))


@register.simple_tag
def pickup_date_range():
    today_date = datetime.today()
    for n in range(1):
        yield pytz.utc.localize((today_date - timedelta(days=n)))


@register.simple_tag
def your_orders_date_range():
    today_date = datetime.today()
    for n in range(1, 30):
        yield pytz.utc.localize((today_date - timedelta(days=n)))


@register.simple_tag(takes_context=True)
def order_day_checker(context, day):
    orders = context["orders"]
    check = orders.filter(created_at__date=day.date()).exists()
    return check


@register.simple_tag(takes_context=True)
def break_checker(context, day, format_string):
    orders = context["orders"]
    check = orders.filter(
        created_at__date=day.date(), pickup_time=format_string
    ).count()
    return check

@register.simple_tag(takes_context=True)
def revenue_day_checker(context, day):
    revenues = context["revenues"]
    check = revenues.filter(created_at__date=day.date()).exists()
    return check