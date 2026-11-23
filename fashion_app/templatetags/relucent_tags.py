from django import template
from decimal import Decimal

register = template.Library()

EXCHANGE_RATES = {
    'NGN': Decimal('1'),
    'USD': Decimal('0.00067'),
    'GBP': Decimal('0.00052'),
    'EUR': Decimal('0.00061'),
}

CURRENCY_SYMBOLS = {
    'NGN': '₦',
    'USD': '$',
    'GBP': '£',
    'EUR': '€',
}

@register.filter(name='currency_price')
def currency_price(price_ngn, currency='NGN'):
    if price_ngn is None:
        return ""
    try:
        val = Decimal(str(price_ngn))
        cur = (currency or 'NGN').upper()
        rate = EXCHANGE_RATES.get(cur, Decimal('1'))
        symbol = CURRENCY_SYMBOLS.get(cur, '₦')
        converted = val * rate
        if cur == 'NGN':
            return f"{symbol}{int(round(converted)):,}"
        return f"{symbol}{converted:,.2f}"
    except Exception:
        return f"₦{price_ngn}"

@register.filter(name='times')
def times(number):
    try:
        return range(int(number))
    except Exception:
        return range(0)
