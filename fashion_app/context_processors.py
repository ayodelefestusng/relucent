from .models import Cart, Wishlist, Category, Collection
from decimal import Decimal

CURRENCY_SYMBOLS = {
    'NGN': '₦',
    'USD': '$',
    'GBP': '£',
    'EUR': '€',
}

EXCHANGE_RATES = {
    'NGN': Decimal('1'),
    'USD': Decimal('0.00067'),
    'GBP': Decimal('0.00052'),
    'EUR': Decimal('0.00061'),
}

def relucent_global_context(request):
    """
    Supplies luxury brand parameters, multi-currency session state,
    cart badge count, wishlist badge count, and navigation structure across all templates.
    """
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    # Currency selection (stored in session, defaults to NGN)
    active_currency = request.session.get('relucent_currency', 'NGN').upper()
    if active_currency not in CURRENCY_SYMBOLS:
        active_currency = 'NGN'

    currency_symbol = CURRENCY_SYMBOLS.get(active_currency, '₦')

    # Cart retrieval
    cart = None
    cart_count = 0
    try:
        cart = Cart.objects.filter(session_id=session_id).prefetch_related('items__variant__product').first()
        if cart:
            cart_count = cart.total_items
    except Exception:
        cart_count = 0

    # Wishlist count
    wishlist_count = 0
    try:
        wishlist_count = Wishlist.objects.filter(session_id=session_id).count()
    except Exception:
        wishlist_count = 0

    # Navigation collections and categories
    try:
        nav_women_categories = Category.objects.filter(gender__in=['women', 'unisex'])[:6]
        nav_men_categories = Category.objects.filter(gender__in=['men', 'unisex'])[:6]
        nav_collections = Collection.objects.filter(is_active=True)[:4]
    except Exception:
        nav_women_categories = []
        nav_men_categories = []
        nav_collections = []

    return {
        'BRAND_NAME': 'Relucent Clothing',
        'BRAND_TAGLINE': 'Affordable Luxury & Modern Elegance',
        'BRAND_LOGO_URL': '/static/images/relucent-logo.jpg',
        'SUPPORT_WHATSAPP': '+234800RELUCENT',
        'SUPPORT_EMAIL': 'concierge@relucentclothing.com',
        'SUPPORT_PHONE': '+234 1 800 7358',
        'ACTIVE_CURRENCY': active_currency,
        'CURRENCY_SYMBOL': currency_symbol,
        'ALL_CURRENCIES': [
            {'code': 'NGN', 'symbol': '₦', 'name': 'Nigerian Naira'},
            {'code': 'USD', 'symbol': '$', 'name': 'US Dollar'},
            {'code': 'GBP', 'symbol': '£', 'name': 'British Pound'},
            {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
        ],
        'CART': cart,
        'CART_COUNT': cart_count,
        'WISHLIST_COUNT': wishlist_count,
        'NAV_WOMEN_CATEGORIES': nav_women_categories,
        'NAV_MEN_CATEGORIES': nav_men_categories,
        'NAV_COLLECTIONS': nav_collections,
        'FREE_SHIPPING_THRESHOLD_TEXT': 'Free Express Delivery on orders over ₦150,000 / $100',
    }
