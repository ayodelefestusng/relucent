from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
import uuid

from .models import (
    Product, ProductVariant, Category, Collection, Color, Size,
    Cart, CartItem, Wishlist, Order, OrderItem, Review, Coupon,
    NewsletterSubscriber, RecentlyViewed, Address, User
)
from .forms import (
    CustomUserRegisterForm, UserLoginForm, UserProfileForm,
    AddressForm, CheckoutForm, ReviewForm, NewsletterForm,
    SizeRecommendationForm
)


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key
    user = request.user if request.user.is_authenticated else None
    cart, created = Cart.objects.get_or_create(session_id=session_id)
    if user and cart.user != user:
        cart.user = user
        cart.save()
    return cart


# ==========================================
# HOMEPAGE & BRAND VIEWS
# ==========================================

def home_view(request):
    """
    Luxury high-converting homepage for Relucent Clothing.
    """
    featured_products = Product.objects.filter(is_published=True, is_featured=True).prefetch_related('images', 'variants')[:8]
    new_arrivals = Product.objects.filter(is_published=True, is_new_arrival=True).prefetch_related('images', 'variants')[:8]
    best_sellers = Product.objects.filter(is_published=True, is_best_seller=True).prefetch_related('images', 'variants')[:8]
    trending_products = Product.objects.filter(is_published=True).order_by('-views_count')[:6]
    collections = Collection.objects.filter(is_active=True).order_by('order')[:3]
    recent_reviews = Review.objects.filter(rating__gte=4).order_by('-created_at')[:6]

    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'trending_products': trending_products,
        'collections': collections,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'relucent/home.html', context)


def about_view(request):
    return render(request, 'relucent/about.html')


def contact_view(request):
    if request.method == 'POST':
        messages.success(request, "Thank you for reaching out to Relucent Concierge. Our fashion advisors will respond within 4 business hours.")
        return redirect('contact')
    return render(request, 'relucent/contact.html')


def faq_view(request):
    return render(request, 'relucent/faq.html')


def shipping_returns_view(request):
    return render(request, 'relucent/shipping_returns.html')


def size_guide_view(request):
    return render(request, 'relucent/size_guide.html')

def utility_view(request):
    return HttpResponse("Utility Page 24112026")

# ==========================================
# PRODUCT LISTING & DETAILS
# ==========================================

def product_list_view(request):
    """
    Catalog listing page with multi-facet filtering and sorting.
    """
    products = Product.objects.filter(is_published=True).prefetch_related('images', 'variants__color', 'variants__size', 'category')

    # Filtering by Gender
    gender = request.GET.get('gender')
    if gender in ['women', 'men', 'unisex']:
        products = products.filter(Q(gender=gender) | Q(gender='unisex'))

    # Filtering by Category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Filtering by Collection
    collection_slug = request.GET.get('collection')
    if collection_slug:
        products = products.filter(collection__slug=collection_slug)

    # Filtering by Badges
    badge = request.GET.get('badge')
    if badge == 'new':
        products = products.filter(is_new_arrival=True)
    elif badge == 'bestseller':
        products = products.filter(is_best_seller=True)
    elif badge == 'sale':
        products = products.filter(discount_price_ngn__isnull=False)

    # Search keyword
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q) |
            Q(sku_prefix__icontains=q)
        )

    # Filter by Color
    color_id = request.GET.get('color')
    if color_id:
        products = products.filter(variants__color_id=color_id)

    # Filter by Size
    size_id = request.GET.get('size')
    if size_id:
        products = products.filter(variants__size_id=size_id)

    # Filter by Price Range (in NGN)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price_ngn__gte=Decimal(min_price))
        except Exception:
            pass
    if max_price:
        try:
            products = products.filter(price_ngn__lte=Decimal(max_price))
        except Exception:
            pass

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price_ngn')
    elif sort_by == 'price_high':
        products = products.order_by('-price_ngn')
    elif sort_by == 'popular':
        products = products.order_by('-views_count')
    elif sort_by == 'bestselling':
        products = products.order_by('-is_best_seller', '-created_at')
    else:  # newest
        products = products.order_by('-created_at')

    products = products.distinct()

    # Available filter options for sidebar
    categories = Category.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()
    collections = Collection.objects.filter(is_active=True)

    context = {
        'products': products,
        'product_count': products.count(),
        'categories': categories,
        'colors': colors,
        'sizes': sizes,
        'collections': collections,
        'active_gender': gender,
        'active_category': category_slug,
        'active_collection': collection_slug,
        'active_badge': badge,
        'active_sort': sort_by,
        'search_query': q,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'relucent/partials/product_grid.html', context)

    return render(request, 'relucent/product_list.html', context)


def product_detail_view(request, slug):
    """
    Luxury Product Details Page (PDP) with high-res gallery,
    sticky mobile CTA, size guide, AI size recommendation, and cross-selling.
    """
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants__color', 'variants__size', 'reviews'),
        slug=slug,
        is_published=True
    )

    # Increment views
    product.views_count += 1
    product.save(update_fields=['views_count'])

    # Track in Recently Viewed
    session_id = request.session.session_key
    if session_id:
        RecentlyViewed.objects.update_or_create(
            session_id=session_id,
            product=product,
            defaults={'user': request.user if request.user.is_authenticated else None}
        )

    # Related / Cross-sell
    related_products = Product.objects.filter(
        category=product.category,
        is_published=True
    ).exclude(id=product.id)[:4]

    complete_look = Product.objects.filter(
        is_published=True
    ).exclude(category=product.category).order_by('?')[:3]

    # Available unique colors and sizes for this product
    variants = product.variants.filter(is_active=True)
    available_colors = Color.objects.filter(productvariant__in=variants).distinct()
    available_sizes = Size.objects.filter(productvariant__in=variants).distinct()

    # Reviews and Review Form
    reviews = product.reviews.order_by('-created_at')
    review_form = ReviewForm()

    context = {
        'product': product,
        'variants': variants,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
        'related_products': related_products,
        'complete_look': complete_look,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'relucent/product_detail.html', context)


@require_POST
def submit_review_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        if request.user.is_authenticated:
            review.user = request.user
            review.customer_name = request.user.get_full_name() or request.user.username
            review.customer_email = request.user.email
        review.save()
        messages.success(request, "Your review has been submitted with our gratitude!")
    else:
        messages.error(request, "Please check your review submission.")
    return redirect('product_detail', slug=slug)


# ==========================================
# AI FITFINDER (SIZE RECOMMENDATION)
# ==========================================

def ai_size_recommend_view(request):
    """
    Intelligent sizing engine calculating recommended size based on
    height, weight, fit preference, and category.
    """
    height = int(request.GET.get('height', 175))
    weight = int(request.GET.get('weight', 70))
    fit = request.GET.get('fit', 'regular')
    gender = request.GET.get('gender', 'women')

    # BMI baseline calculation
    bmi = weight / ((height / 100) ** 2)

    if gender == 'women':
        if bmi < 19:
            base_size = 'XS'
        elif bmi < 22:
            base_size = 'S'
        elif bmi < 25:
            base_size = 'M'
        elif bmi < 29:
            base_size = 'L'
        else:
            base_size = 'XL'
    else:
        if bmi < 21:
            base_size = 'S'
        elif bmi < 25:
            base_size = 'M'
        elif bmi < 28:
            base_size = 'L'
        elif bmi < 32:
            base_size = 'XL'
        else:
            base_size = 'XXL'

    # Adjust for fit preference
    size_scale = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
    current_idx = size_scale.index(base_size) if base_size in size_scale else 2
    if fit == 'slim' and current_idx > 0:
        recommended_size = size_scale[current_idx - 1]
    elif fit == 'relaxed' and current_idx < len(size_scale) - 1:
        recommended_size = size_scale[current_idx + 1]
    else:
        recommended_size = base_size

    confidence = 94 if (18 <= bmi <= 30) else 88

    return JsonResponse({
        'status': 'success',
        'recommended_size': recommended_size,
        'confidence': f"{confidence}%",
        'message': f"Based on your profile ({height}cm, {weight}kg, {fit} fit), size {recommended_size} will drape flawlessly.",
    })


# ==========================================
# SHOPPING CART & WISHLIST
# ==========================================

def cart_view(request):
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
    }
    return render(request, 'relucent/cart.html', context)


@require_POST
def cart_add_view(request):
    """
    AJAX / HTMX endpoint to add an item to the shopping cart.
    """
    variant_id = request.POST.get('variant_id')
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    cart = get_or_create_cart(request)

    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
    elif product_id:
        # Fallback to first in-stock variant of product
        product = get_object_or_404(Product, id=product_id)
        variant = product.variants.filter(is_active=True, stock_quantity__gt=0).first()
        if not variant:
            variant = product.variants.first()

    if not variant:
        if request.headers.get('HX-Request'):
            return HttpResponse('<script>alert("Item out of stock.");</script>')
        messages.error(request, "Selected variant is currently out of stock.")
        return redirect('cart')

    item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    if request.headers.get('HX-Request'):
        return render(request, 'relucent/partials/cart_drawer.html', {'cart': cart})

    messages.success(request, f"Added {variant.product.name} ({variant.size.name}) to your shopping bag.")
    return redirect('cart')


@require_POST
def cart_update_view(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == 'remove':
        item.delete()

    if request.headers.get('HX-Request'):
        return render(request, 'relucent/partials/cart_drawer.html', {'cart': cart})

    return redirect('cart')


def wishlist_view(request):
    session_id = request.session.session_key
    items = Wishlist.objects.filter(session_id=session_id).select_related('product')
    return render(request, 'relucent/wishlist.html', {'wishlist_items': items})


@require_POST
def wishlist_toggle_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key
    user = request.user if request.user.is_authenticated else None

    wishlist_item = Wishlist.objects.filter(session_id=session_id, product=product).first()
    if wishlist_item:
        wishlist_item.delete()
        is_wishlisted = False
    else:
        Wishlist.objects.create(session_id=session_id, user=user, product=product)
        is_wishlisted = True

    wishlist_count = Wishlist.objects.filter(session_id=session_id).count()

    return JsonResponse({
        'status': 'success',
        'is_wishlisted': is_wishlisted,
        'wishlist_count': wishlist_count,
    })


# ==========================================
# STREAMLINED ONE-PAGE CHECKOUT & PAYMENTS
# ==========================================

def checkout_view(request):
    """
    World-class luxury one-page checkout supporting guest and registered users,
    multi-currency conversion, coupon validation, and Paystack/Stripe/Flutterwave.
    """
    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        messages.warning(request, "Your shopping bag is currently empty.")
        return redirect('product_list')

    active_currency = request.session.get('relucent_currency', 'NGN').upper()

    # Pre-fill data if user is authenticated
    initial_data = {}
    if request.user.is_authenticated:
        initial_data['customer_name'] = request.user.get_full_name() or request.user.username
        initial_data['customer_email'] = request.user.email
        initial_data['customer_phone'] = request.user.phone_number or ''
        default_addr = request.user.addresses.filter(is_default_shipping=True).first()
        if default_addr:
            initial_data['shipping_address'] = default_addr.street_address
            initial_data['apartment'] = default_addr.apartment
            initial_data['city'] = default_addr.city
            initial_data['state'] = default_addr.state
            initial_data['country'] = default_addr.country
            initial_data['postal_code'] = default_addr.postal_code

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            order_number = f"REL-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

            # Calculate shipping fee
            shipping_method = data['shipping_method']
            if shipping_method == 'dhl_intl':
                shipping_fee = Decimal('25000.00')
                carrier = 'DHL Express Worldwide'
            elif shipping_method == 'lagos_express':
                shipping_fee = Decimal('7500.00')
                carrier = 'Lagos Express Courier'
            else:
                shipping_fee = Decimal('5000.00')
                carrier = 'DHL Express Nigeria'

            # Check Free Shipping qualification (threshold ₦150,000)
            if cart.subtotal_ngn >= Decimal('150000'):
                shipping_fee = Decimal('0.00')

            subtotal_ngn = cart.subtotal_ngn
            discount_amount = Decimal('0.00')

            # Coupon application
            coupon_code = data.get('coupon_code', '').strip().upper()
            if coupon_code:
                coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
                if coupon:
                    discount_amount = (subtotal_ngn * Decimal(coupon.discount_percent)) / Decimal('100')
                    coupon.used_count += 1
                    coupon.save()

            total_ngn = subtotal_ngn + shipping_fee - discount_amount

            is_paystack = (data['payment_method'] == 'paystack')
            # Create Order
            order = Order.objects.create(
                order_number=order_number,
                user=request.user if request.user.is_authenticated else None,
                session_id=request.session.session_key,
                customer_name=data['customer_name'],
                customer_email=data['customer_email'],
                customer_phone=data['customer_phone'],
                shipping_address=data['shipping_address'],
                apartment=data.get('apartment', ''),
                city=data['city'],
                state=data['state'],
                country=data['country'],
                postal_code=data.get('postal_code', ''),
                shipping_method=data['shipping_method'],
                shipping_fee=shipping_fee,
                tracking_carrier=carrier,
                currency='NGN',
                subtotal=subtotal_ngn,
                discount_amount=discount_amount,
                total=total_ngn,
                coupon_code=coupon_code,
                payment_method=data['payment_method'],
                payment_status='pending' if is_paystack else 'paid',
                notes=data.get('notes', ''),
            )

            # Create Order Items from Cart
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    product_name=item.variant.product.name,
                    variant_details=f"{item.variant.color.name} / {item.variant.size.name}",
                    unit_price=item.unit_price_ngn,
                    quantity=item.quantity,
                    line_total=item.line_total_ngn,
                    image_url=item.variant.product.primary_image_url
                )

            # Clear cart
            cart.items.all().delete()

            # Paystack live initialization
            if is_paystack:
                try:
                    import requests
                    paystack_url = "https://api.paystack.co/transaction/initialize"
                    headers = {
                        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                        "Content-Type": "application/json",
                    }
                    callback_url = request.build_absolute_uri(reverse('paystack_callback'))
                    payload = {
                        "email": order.customer_email,
                        "amount": int(order.total * 100),  # in Kobo
                        "reference": order.order_number,
                        "callback_url": callback_url,
                        "metadata": {
                            "order_number": order.order_number,
                            "customer_name": order.customer_name,
                        }
                    }
                    res = requests.post(paystack_url, json=payload, headers=headers, timeout=10)
                    res_json = res.json()
                    if res_json.get('status') and 'authorization_url' in res_json.get('data', {}):
                        return redirect(res_json['data']['authorization_url'])
                except Exception as e:
                    pass

            messages.success(request, f"Order {order.order_number} confirmed successfully!")
            return redirect('order_confirmation', order_number=order.order_number)
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'relucent/checkout.html', context)


def paystack_callback_view(request):
    reference = request.GET.get('reference') or request.GET.get('trxref')
    if reference:
        try:
            import requests
            verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            }
            res = requests.get(verify_url, headers=headers, timeout=10).json()
            if res.get('status') and res.get('data', {}).get('status') == 'success':
                order = Order.objects.filter(order_number=reference).first()
                if order:
                    order.payment_status = 'paid'
                    order.payment_reference = res['data'].get('reference')
                    order.order_status = 'confirmed'
                    order.save()
                    messages.success(request, f"Payment verified successfully via Paystack for order {order.order_number}!")
                    return redirect('order_confirmation', order_number=order.order_number)
        except Exception as e:
            pass

    order = Order.objects.filter(order_number=reference).first()
    if order:
        return redirect('order_confirmation', order_number=order.order_number)
    messages.error(request, "Unable to verify Paystack payment.")
    return redirect('home')


def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    return render(request, 'relucent/order_confirmation.html', {'order': order})


def track_order_view(request):
    order = None
    searched = False
    order_num = request.GET.get('order_number', '').strip()
    email = request.GET.get('email', '').strip()

    if order_num:
        searched = True
        query = Q(order_number__iexact=order_num)
        if email:
            query &= Q(customer_email__iexact=email)
        order = Order.objects.filter(query).prefetch_related('items').first()

    context = {
        'order': order,
        'searched': searched,
        'order_number': order_num,
        'email': email,
    }
    return render(request, 'relucent/track_order.html', context)


# ==========================================
# CURRENCY & UTILITIES
# ==========================================

def currency_switch_view(request, currency_code):
    """
    Sets the active currency in session and redirects back.
    """
    code = currency_code.upper()
    if code in ['NGN', 'USD', 'GBP', 'EUR']:
        request.session['relucent_currency'] = code
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


@require_POST
def newsletter_subscribe_view(request):
    email = request.POST.get('email', '').strip()
    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)
        messages.success(request, "Welcome to the Relucent Circle. Use coupon code RELUCENT10 for 10% off your order.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ==========================================
# CUSTOMER DASHBOARD & AUTHENTICATION
# ==========================================

def user_register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Relucent Clothing, {user.username}!")
            return redirect('dashboard')
    else:
        form = CustomUserRegisterForm()
    return render(request, 'relucent/auth/register.html', {'form': form})


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}.")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = UserLoginForm()
    return render(request, 'relucent/auth/login.html', {'form': form})


def user_logout_view(request):
    logout(request)
    messages.info(request, "You have been securely signed out.")
    return redirect('home')


@login_required
def dashboard_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    addresses = request.user.addresses.all()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    context = {
        'orders': orders,
        'addresses': addresses,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'relucent/account/dashboard.html', context)


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'relucent/account/orders.html', {'orders': orders})
