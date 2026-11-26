from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal
import uuid


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    LOYALTY_CHOICES = [
        ('silver', 'Silver Member'),
        ('gold', 'Gold Member'),
        ('platinum', 'Platinum VIP'),
    ]
    loyalty_tier = models.CharField(max_length=20, choices=LOYALTY_CHOICES, default='silver')
    loyalty_points = models.PositiveIntegerField(default=100)
    newsletter_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.username or self.email


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=25)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    is_default_shipping = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"


class Category(models.Model):
    GENDER_CHOICES = [
        ('women', 'Women'),
        ('men', 'Men'),
        ('unisex', 'Unisex / Accessories'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='women')
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.gender}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_gender_display()} - {self.name}"


class Collection(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    banner_image_url = models.ImageField(upload_to='banners/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=20, default='#111111', help_text="Hex code e.g. #C9A865")

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Product(models.Model):
    GENDER_CHOICES = [
        ('women', 'Women'),
        ('men', 'Men'),
        ('unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku_prefix = models.CharField(max_length=50, unique=True, help_text="e.g. REL-DRS-01")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='women')
    
    # Narrative & Product Features
    tagline = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. 100% Organic Silk Satin")
    description = models.TextField(help_text="Detailed luxury product story and silhouette notes")
    fabric_care = models.TextField(blank=True, null=True, help_text="e.g. 100% Mulberry Silk. Dry clean only.")
    fit_notes = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. Tailored fit. Model is 5'10 and wears size S.")
    
    # Base Pricing in Nigerian Naira (NGN), with automatic multi-currency conversion
    price_ngn = models.DecimalField(max_digits=12, decimal_places=2, help_text="Base price in NGN")
    discount_price_ngn = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Sale price in NGN")

    # Badges & Sorting
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=True)
    is_best_seller = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    # Social Proof & Metrics
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('4.9'))
    reviews_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        if self.discount_price_ngn and self.price_ngn > self.discount_price_ngn:
            saving = ((self.price_ngn - self.discount_price_ngn) / self.price_ngn) * 100
            return int(round(saving))
        return 0

    @property
    def primary_image_url(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image_url
        first_img = self.images.first()
        if first_img:
            return first_img.image_url
        return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80"

    @property
    def hover_image_url(self):
        hover = self.images.filter(is_hover=True).first()
        if hover:
            return hover.image_url
        images = list(self.images.all())
        if len(images) > 1:
            return images[1].image_url
        return self.primary_image_url

    def get_price(self, currency='NGN'):
        # Exchange rates relative to NGN
        rates = {'NGN': Decimal('1'), 'USD': Decimal('0.00067'), 'GBP': Decimal('0.00052'), 'EUR': Decimal('0.00061')}
        rate = rates.get(currency.upper(), Decimal('1'))
        raw = (self.price_ngn * rate)
        if currency.upper() == 'NGN':
            return int(round(raw))
        return round(raw, 2)

    def get_discount_price(self, currency='NGN'):
        if not self.discount_price_ngn:
            return None
        rates = {'NGN': Decimal('1'), 'USD': Decimal('0.00067'), 'GBP': Decimal('0.00052'), 'EUR': Decimal('0.00061')}
        rate = rates.get(currency.upper(), Decimal('1'))
        raw = (self.discount_price_ngn * rate)
        if currency.upper() == 'NGN':
            return int(round(raw))
        return round(raw, 2)


class HomepageVideo(models.Model):
    title = models.CharField(max_length=150)
    video_url = models.URLField(help_text='Vimeo or YouTube embed URL')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Homepage Video'
        verbose_name_plural = 'Homepage Videos'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.ImageField(upload_to='product_images/', blank=True, null=True, help_text="Image URL (CDN, Unsplash, or media storage)")
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    is_hover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} Image #{self.id}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    sku = models.CharField(max_length=80, unique=True)
    stock_quantity = models.PositiveIntegerField(default=15)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'color', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.color.name} / {self.size.name}"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class Cart(models.Model):
    session_id = models.CharField(max_length=150, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} ({self.session_id})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal_ngn(self):
        total = Decimal('0.00')
        for item in self.items.select_related('variant__product'):
            unit_price = item.variant.product.discount_price_ngn or item.variant.product.price_ngn
            total += unit_price * item.quantity
        return total

    def get_subtotal(self, currency='NGN'):
        rates = {'NGN': Decimal('1'), 'USD': Decimal('0.00067'), 'GBP': Decimal('0.00052'), 'EUR': Decimal('0.00061')}
        rate = rates.get(currency.upper(), Decimal('1'))
        raw = self.subtotal_ngn * rate
        if currency.upper() == 'NGN':
            return int(round(raw))
        return round(raw, 2)

    def free_shipping_progress(self, currency='NGN'):
        # Free shipping threshold: ₦150,000 / $100 / £80 / €90
        thresholds_ngn = Decimal('150000')
        sub = self.subtotal_ngn
        pct = min(100, int((sub / thresholds_ngn) * 100))
        remaining = max(Decimal('0'), thresholds_ngn - sub)
        return {
            'percent': pct,
            'is_qualified': sub >= thresholds_ngn,
            'remaining_ngn': int(remaining),
        }


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f"{self.quantity}x {self.variant}"

    @property
    def unit_price_ngn(self):
        return self.variant.product.discount_price_ngn or self.variant.product.price_ngn

    @property
    def line_total_ngn(self):
        return self.unit_price_ngn * self.quantity

    def get_line_total(self, currency='NGN'):
        rates = {'NGN': Decimal('1'), 'USD': Decimal('0.00067'), 'GBP': Decimal('0.00052'), 'EUR': Decimal('0.00061')}
        rate = rates.get(currency.upper(), Decimal('1'))
        raw = self.line_total_ngn * rate
        if currency.upper() == 'NGN':
            return int(round(raw))
        return round(raw, 2)


class Wishlist(models.Model):
    session_id = models.CharField(max_length=150, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_id', 'product')

    def __str__(self):
        return f"Wishlist: {self.product.name}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=10, help_text="e.g. 10 for 10% off")
    min_order_ngn = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    valid_until = models.DateField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% OFF)"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('processing', 'Processing Order'),
        ('confirmed', 'Confirmed & Tailored'),
        ('shipped', 'Dispatched with Courier'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid Securely'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('paystack', 'Paystack (Cards, Bank Transfer, USSD)'),
        ('flutterwave', 'Flutterwave (Mobile Money, Cards)'),
        ('stripe', 'Stripe (Apple Pay, Google Pay, Global Cards)'),
        ('bank_transfer', 'Direct Bank Transfer / Concierge'),
    ]

    order_number = models.CharField(max_length=60, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_id = models.CharField(max_length=150, blank=True, null=True)

    # Customer info
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)

    # Shipping address
    shipping_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    postal_code = models.CharField(max_length=30, blank=True, null=True)

    # Shipping Carrier & Method
    shipping_method = models.CharField(max_length=100, default='DHL Express Nationwide')
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('5000.00'))
    tracking_carrier = models.CharField(max_length=50, default='DHL Express')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    # Pricing & Currency
    currency = models.CharField(max_length=10, default='NGN')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2)

    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='paystack')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=200, blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='processing')

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    variant_details = models.CharField(max_length=100, help_text="e.g. Gold / M")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.variant_details})"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    rating = models.PositiveIntegerField(default=5)
    headline = models.CharField(max_length=200)
    comment = models.TextField()
    verified_purchase = models.BooleanField(default=True)
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ Review for {self.product.name} by {self.customer_name}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email


class RecentlyViewed(models.Model):
    session_id = models.CharField(max_length=150, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('session_id', 'product')
