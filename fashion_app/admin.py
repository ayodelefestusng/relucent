from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    User, Address, Category, Collection, Color, Size,
    Product, ProductImage, ProductVariant, Cart, CartItem, Wishlist,
    Coupon, Order, OrderItem, Review, NewsletterSubscriber, RecentlyViewed,
    HomepageVideo,
)



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ('image_url', 'image_preview', 'alt_text', 'is_primary', 'is_hover', 'order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 60px; object-fit: cover; border-radius: 4px;" />', obj.image_url)
        return "-"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3
    fields = ('color', 'size', 'sku', 'stock_quantity', 'is_active')


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category__name', 'gender', 'price_ngn', 'discount_price_ngn', 'is_new_arrival', 'is_best_seller')




@admin.register(HomepageVideo)
class HomepageVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title',)


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_classes = [ProductResource]
    list_display = ('thumbnail_preview', 'name', 'category', 'gender', 'display_price', 'display_discount', 'is_new_arrival', 'is_best_seller', 'is_featured', 'is_published')
    list_filter = ('gender', 'category', 'collection', 'is_published', 'is_new_arrival', 'is_best_seller', 'is_featured')
    search_fields = ('name', 'sku_prefix', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    ordering = ('-created_at',)

    def thumbnail_preview(self, obj):
        img = obj.primary_image_url
        if img:
            return format_html('<img src="{}" style="width: 45px; height: 55px; object-fit: cover; border-radius: 4px; border: 1px solid #C9A865;" />', img)
        return "-"
    thumbnail_preview.short_description = "Image"

    def display_price(self, obj):
        return f"₦{obj.price_ngn:,.0f}"
    display_price.short_description = "Price (NGN)"

    def display_discount(self, obj):
        if obj.discount_price_ngn:
            return f"₦{obj.discount_price_ngn:,.0f} (-{obj.discount_percentage}%)"
        return "-"
    display_discount.short_description = "Sale Price"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_details', 'unit_price', 'quantity', 'line_total', 'item_preview')
    fields = ('item_preview', 'product_name', 'variant_details', 'unit_price', 'quantity', 'line_total')

    def item_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 40px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.image_url)
        return "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'customer_email', 'total_display', 'currency', 'status_badge', 'payment_badge', 'created_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'currency', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone', 'tracking_number')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')

    def total_display(self, obj):
        return f"{obj.currency} {obj.total:,.2f}"
    total_display.short_description = "Total Amount"

    def status_badge(self, obj):
        colors = {
            'processing': '#FFB020',
            'confirmed': '#1E8E3E',
            'shipped': '#111111',
            'delivered': '#1E8E3E',
            'cancelled': '#D14343',
        }
        color = colors.get(obj.order_status, '#666')
        return format_html('<span style="background: {}; color: #fff; padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>', color, obj.get_order_status_display())
    status_badge.short_description = "Order Status"

    def payment_badge(self, obj):
        colors = {
            'paid': '#1E8E3E',
            'pending': '#FFB020',
            'failed': '#D14343',
            'refunded': '#888',
        }
        color = colors.get(obj.payment_status, '#666')
        return format_html('<span style="background: {}; color: #fff; padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>', color, obj.get_payment_status_display())
    payment_badge.short_description = "Payment Status"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'order', 'is_featured')
    prepopulated_fields = {'slug': ('gender', 'name')}
    list_editable = ('order', 'is_featured')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tagline', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_color_box')

    def hex_color_box(self, obj):
        return format_html('<div style="display: flex; align-items: center; gap: 8px;"><span style="width: 20px; height: 20px; background: {}; border: 1px solid #ccc; border-radius: 50%; display: inline-block;"></span>{}</div>', obj.hex_code, obj.hex_code)
    hex_color_box.short_description = "Hex Swatch"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'used_count', 'valid_until')
    list_editable = ('is_active',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer_name', 'rating', 'verified_purchase', 'created_at')
    list_filter = ('rating', 'verified_purchase')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'loyalty_tier', 'loyalty_points', 'is_staff')
    list_filter = ('loyalty_tier', 'is_staff', 'is_active')
