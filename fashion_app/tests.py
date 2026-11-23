from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import Product, Category, Color, Size, ProductVariant, Cart, Order, User


class RelucentPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Base category, color, size
        self.category = Category.objects.create(name="Evening Dresses", gender="women")
        self.color = Color.objects.create(name="Champagne Gold", hex_code="#C9A865")
        self.size = Size.objects.create(name="M", order=3)

        # Base product
        self.product = Product.objects.create(
            name="The Aurelia Silk Gown",
            sku_prefix="REL-DRS-001",
            category=self.category,
            gender="women",
            description="Pure luxury silk satin.",
            price_ngn=Decimal("200000.00"),
            discount_price_ngn=Decimal("180000.00"),
            is_published=True,
            is_featured=True,
            is_new_arrival=True,
        )

        # Variant
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color=self.color,
            size=self.size,
            sku="REL-DRS-001-GLD-M",
            stock_quantity=20,
            is_active=True
        )

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relucent")
        self.assertContains(response, "Aurelia")

    def test_catalog_listing(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Aurelia Silk Gown")

    def test_product_detail(self):
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Aurelia Silk Gown")
        self.assertContains(response, "Add to Shopping Bag")

    def test_ai_size_recommendation_api(self):
        response = self.client.get(reverse('ai_size_recommend'), {'height': 175, 'weight': 68, 'fit': 'regular', 'gender': 'women'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('recommended_size', data)

    def test_cart_add_and_view(self):
        response = self.client.post(reverse('cart_add'), {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 1,
        })
        self.assertEqual(response.status_code, 302)

        cart_page = self.client.get(reverse('cart'))
        self.assertEqual(cart_page.status_code, 200)
        self.assertContains(cart_page, "The Aurelia Silk Gown")

    def test_currency_switch(self):
        response = self.client.get(reverse('currency_switch', kwargs={'currency_code': 'USD'}))
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session.get('relucent_currency'), 'USD')

    def test_wishlist_toggle(self):
        response = self.client.post(reverse('wishlist_toggle', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_wishlisted'])
        self.assertEqual(data['wishlist_count'], 1)

    def test_checkout_and_order_creation(self):
        # Add to cart first
        self.client.post(reverse('cart_add'), {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 1,
        })

        checkout_data = {
            'customer_name': 'Lady Ngozi Eze',
            'customer_email': 'ngozi@luxury.ng',
            'customer_phone': '+2348030001122',
            'shipping_address': '12 Victoria Island Crescent',
            'apartment': 'Penthouse 4B',
            'city': 'Lagos',
            'state': 'Lagos State',
            'country': 'Nigeria',
            'shipping_method': 'dhl_local',
            'payment_method': 'paystack',
            'coupon_code': 'RELUCENT10',
            'notes': 'Please deliver before 5 PM.',
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)

        # Check order in database
        order = Order.objects.filter(customer_email='ngozi@luxury.ng').first()
        self.assertIsNotNone(order)
        self.assertTrue(order.order_number.startswith('REL-'))
        self.assertEqual(order.items.count(), 1)
