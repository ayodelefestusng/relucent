from django.urls import path
from . import views

urlpatterns = [
    # Brand & Home
    path('', views.home_view, name='home'),
    path('utility/', views.utility_view, name='utility'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('shipping-returns/', views.shipping_returns_view, name='shipping_returns'),
    path('size-guide/', views.size_guide_view, name='size_guide'),

    # Catalog & Product
    path('shop/', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('product/<slug:slug>/review/', views.submit_review_view, name='submit_review'),
    path('api/ai-size-recommend/', views.ai_size_recommend_view, name='ai_size_recommend'),

    # Shopping Bag & Wishlist
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.cart_add_view, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update_view, name='cart_update'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle_view, name='wishlist_toggle'),

    # Checkout & Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/paystack/callback/', views.paystack_callback_view, name='paystack_callback'),
    path('order/confirmed/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    path('track-order/', views.track_order_view, name='track_order'),

    # Currency & Newsletter
    path('currency/<str:currency_code>/', views.currency_switch_view, name='currency_switch'),
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),

    # Auth & Account
    path('account/register/', views.user_register_view, name='register'),
    path('account/login/', views.user_login_view, name='login'),
    path('account/logout/', views.user_logout_view, name='logout'),
    path('account/dashboard/', views.dashboard_view, name='dashboard'),
    path('account/orders/', views.order_history_view, name='order_history'),
]
