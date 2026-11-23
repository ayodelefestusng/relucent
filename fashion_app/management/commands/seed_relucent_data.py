from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
from fashion_app.models import (
    User, Category, Collection, Color, Size, Product,
    ProductImage, ProductVariant, Coupon, Review
)


class Command(BaseCommand):
    help = "Seeds the database with luxury fashion catalog data for Relucent Clothing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Relucent Clothing data seed..."))

        # 1. Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "concierge@relucentclothing.com", "relucent2026!")
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / relucent2026!"))

        # 2. Colors
        colors_data = [
            ("Champagne Gold", "#C9A865"),
            ("Midnight Onyx", "#111111"),
            ("Alabaster White", "#F8F8F8"),
            ("Emerald Green", "#1B4D3E"),
            ("Royal Navy", "#0B1D3A"),
            ("Camel Cashmere", "#C19A6B"),
            ("Crimson Velvet", "#800020"),
        ]
        color_objs = {}
        for name, hex_code in colors_data:
            c, _ = Color.objects.get_or_create(name=name, defaults={"hex_code": hex_code})
            color_objs[name] = c

        # 3. Sizes
        sizes_data = [
            ("XS", 1), ("S", 2), ("M", 3), ("L", 4), ("XL", 5), ("XXL", 6),
            ("UK 8", 10), ("UK 10", 11), ("UK 12", 12), ("UK 14", 13), ("UK 16", 14)
        ]
        size_objs = {}
        for name, order in sizes_data:
            s, _ = Size.objects.get_or_create(name=name, defaults={"order": order})
            size_objs[name] = s

        # 4. Collections
        col1, _ = Collection.objects.get_or_create(
            name="Lagos to Mayfair - A/W 2026",
            defaults={
                "tagline": "Modern Nigerian Luxury Meets British Tailoring",
                "description": "Structured silhouettes, hand-finished lapels, and opulent silk linings designed for high-profile transitions.",
                "banner_image_url": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1600&q=85",
                "order": 1,
            }
        )
        col2, _ = Collection.objects.get_or_create(
            name="Golden Hour Resort Edit",
            defaults={
                "tagline": "Flowing Draped Silhouettes in Luminous Hues",
                "description": "Effortless resort wear inspired by West African sunsets, crafted from 100% natural Mulberry silk and breathable linen.",
                "banner_image_url": "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1600&q=85",
                "order": 2,
            }
        )
        col3, _ = Collection.objects.get_or_create(
            name="The Monolithic Black Tie",
            defaults={
                "tagline": "Architectural Glamour & Midnight Velvet",
                "description": "Red carpet ready gowns, sharp double-breasted tuxedos, and signature gold metal hardware.",
                "banner_image_url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=1600&q=85",
                "order": 3,
            }
        )

        # 5. Categories
        cat_women_dresses, _ = Category.objects.get_or_create(
            name="Dresses & Gowns",
            gender="women",
            defaults={
                "description": "Draped silk satins, architectural cuts, and timeless black-tie silhouettes.",
                "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=800&q=80",
                "order": 1,
            }
        )
        cat_women_coords, _ = Category.objects.get_or_create(
            name="Silk Co-Ords",
            gender="women",
            defaults={
                "description": "Effortless matching sets with wide-leg trousers and plunging lapel tops.",
                "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80",
                "order": 2,
            }
        )
        cat_men_suits, _ = Category.objects.get_or_create(
            name="Suits & Tailoring",
            gender="men",
            defaults={
                "description": "Savile Row precision infused with contemporary African tailoring swagger.",
                "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80",
                "order": 3,
            }
        )
        cat_men_shirts, _ = Category.objects.get_or_create(
            name="Camp Collar & Silk Shirts",
            gender="men",
            defaults={
                "description": "Textured linens and fluid silks with signature gold buttons.",
                "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80",
                "order": 4,
            }
        )
        cat_outerwear, _ = Category.objects.get_or_create(
            name="Outerwear & Capes",
            gender="unisex",
            defaults={
                "description": "Cashmere wool blends, belted trench coats, and regal structured capes.",
                "image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?auto=format&fit=crop&w=800&q=80",
                "order": 5,
            }
        )

        # 6. Luxury Products Catalog
        products_data = [
            {
                "name": "The Aurelia Draped Silk Halter Gown",
                "sku_prefix": "REL-DRS-001",
                "category": cat_women_dresses,
                "collection": col2,
                "gender": "women",
                "tagline": "Liquid Champagne Silk with Open Back",
                "description": "A masterclass in effortless drama. The Aurelia gown is cut on the bias from heavy 22mm Mulberry silk satin that glides over curves. Features an elongated halter neckline with hand-polished 18k gold-finish toggles and a sweeping side slit.",
                "fabric_care": "100% Organic Mulberry Silk Satin. Specialized dry clean only.",
                "fit_notes": "Fluid bias cut. Model is 5'10 (178cm), wearing size UK 8 / S.",
                "price_ngn": Decimal("245000.00"),
                "discount_price_ngn": Decimal("215000.00"),
                "is_featured": True,
                "is_new_arrival": True,
                "is_best_seller": True,
                "images": [
                    "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=85"
                ],
                "colors": ["Champagne Gold", "Midnight Onyx", "Emerald Green"],
                "sizes": ["XS", "S", "M", "L", "XL"]
            },
            {
                "name": "Mayfair Double-Breasted Wool Tuxedo",
                "sku_prefix": "REL-SUT-002",
                "category": cat_men_suits,
                "collection": col1,
                "gender": "men",
                "tagline": "Super 140s Italian Wool with Silk Peak Lapels",
                "description": "Designed for commanding presence. This 6-button double-breasted tuxedo combines sharp British structured shoulders with a gently suppressed waist. Accented with contrast duchess satin lapels and Relucent custom engraved gold buttons.",
                "fabric_care": "100% Super 140s Merino Wool; 100% Silk Lapels & Cupro Lining. Dry clean only.",
                "fit_notes": "Tailored European fit. Model is 6'1 (185cm), chest 39\", wearing size 40R / M.",
                "price_ngn": Decimal("380000.00"),
                "discount_price_ngn": None,
                "is_featured": True,
                "is_new_arrival": True,
                "is_best_seller": True,
                "images": [
                    "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=900&q=85"
                ],
                "colors": ["Midnight Onyx", "Royal Navy"],
                "sizes": ["S", "M", "L", "XL", "XXL"]
            },
            {
                "name": "Elysian Silk Satin Co-Ord Set",
                "sku_prefix": "REL-CRD-003",
                "category": cat_women_coords,
                "collection": col2,
                "gender": "women",
                "tagline": "Two-Piece Relaxed Shirt & Pleated Palazzo Trouser",
                "description": "Effortless opulence for warm city evenings and Mediterranean yacht days. Features an oversized nonchalant camp shirt and high-waisted floor-skimming palazzo trousers with an elasticated back waistband for comfort.",
                "fabric_care": "100% Mulberry Silk. Hand wash cold or eco dry clean.",
                "fit_notes": "Relaxed slouchy luxury fit. Take your true size.",
                "price_ngn": Decimal("185000.00"),
                "discount_price_ngn": Decimal("165000.00"),
                "is_featured": True,
                "is_new_arrival": True,
                "is_best_seller": False,
                "images": [
                    "https://images.unsplash.com/photo-1581044777550-4cfa60707c03?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=900&q=85"
                ],
                "colors": ["Alabaster White", "Champagne Gold", "Midnight Onyx"],
                "sizes": ["XS", "S", "M", "L", "XL"]
            },
            {
                "name": "The Monarch Belted Cashmere Wool Coat",
                "sku_prefix": "REL-OUT-004",
                "category": cat_outerwear,
                "collection": col1,
                "gender": "unisex",
                "tagline": "Double-Faced Cashmere & Australian Wool",
                "description": "An architectural wrap coat that commands attention from Lagos departures to London arrivals. Tailored from hand-stitched double-faced cashmere wool with raglan sleeves and a detachable sash belt with gold metal aglets.",
                "fabric_care": "70% Australian Virgin Wool, 30% Mongolian Cashmere. Dry clean only.",
                "fit_notes": "Oversized cocoon silhouette. Designed to layer comfortably over tailoring.",
                "price_ngn": Decimal("320000.00"),
                "discount_price_ngn": None,
                "is_featured": True,
                "is_new_arrival": False,
                "is_best_seller": True,
                "images": [
                    "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=900&q=85"
                ],
                "colors": ["Camel Cashmere", "Midnight Onyx", "Alabaster White"],
                "sizes": ["S", "M", "L", "XL"]
            },
            {
                "name": "The Caspian Raw Silk Resort Shirt",
                "sku_prefix": "REL-SHT-005",
                "category": cat_men_shirts,
                "collection": col2,
                "gender": "men",
                "tagline": "Textured Raw Silk with Contrast Piping",
                "description": "Crafted from breathable slub raw silk featuring retro Cuban camp collar, tonal hand-embroidered monogram on the chest pocket, and bespoke Mother of Pearl buttons.",
                "fabric_care": "100% Textured Raw Silk. Hand wash cold or dry clean.",
                "fit_notes": "Boxy contemporary fit. Model wears size L.",
                "price_ngn": Decimal("95000.00"),
                "discount_price_ngn": Decimal("82000.00"),
                "is_featured": False,
                "is_new_arrival": True,
                "is_best_seller": True,
                "images": [
                    "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=85"
                ],
                "colors": ["Alabaster White", "Emerald Green", "Camel Cashmere"],
                "sizes": ["S", "M", "L", "XL", "XXL"]
            },
            {
                "name": "The Solange Corseted Velvet Evening Column",
                "sku_prefix": "REL-DRS-006",
                "category": cat_women_dresses,
                "collection": col3,
                "gender": "women",
                "tagline": "Sculpted Internal Boning in Midnight Stretch Velvet",
                "description": "Seductive minimalism meets red-carpet grandeur. The Solange column dress features couture-level internal corset boning that accentuates the waist before cascading into a statuesque straight column skirt.",
                "fabric_care": "Silk-blend micro-pile velvet. Specialized dry clean only.",
                "fit_notes": "Fitted through bodice, stretch through hips. True to size.",
                "price_ngn": Decimal("265000.00"),
                "discount_price_ngn": None,
                "is_featured": True,
                "is_new_arrival": True,
                "is_best_seller": False,
                "images": [
                    "https://images.unsplash.com/photo-1518895949257-7621c3c786d7?auto=format&fit=crop&w=900&q=85",
                    "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=900&q=85"
                ],
                "colors": ["Midnight Onyx", "Crimson Velvet", "Royal Navy"],
                "sizes": ["XS", "S", "M", "L", "XL"]
            }
        ]

        for p_data in products_data:
            product, created = Product.objects.get_or_create(
                sku_prefix=p_data["sku_prefix"],
                defaults={
                    "name": p_data["name"],
                    "category": p_data["category"],
                    "collection": p_data["collection"],
                    "gender": p_data["gender"],
                    "tagline": p_data["tagline"],
                    "description": p_data["description"],
                    "fabric_care": p_data["fabric_care"],
                    "fit_notes": p_data["fit_notes"],
                    "price_ngn": p_data["price_ngn"],
                    "discount_price_ngn": p_data["discount_price_ngn"],
                    "is_featured": p_data["is_featured"],
                    "is_new_arrival": p_data["is_new_arrival"],
                    "is_best_seller": p_data["is_best_seller"],
                    "rating_average": Decimal("4.9"),
                    "reviews_count": 8,
                    "views_count": 240,
                }
            )

            # Create Images
            for idx, img_url in enumerate(p_data["images"]):
                ProductImage.objects.get_or_create(
                    product=product,
                    image_url=img_url,
                    defaults={
                        "is_primary": (idx == 0),
                        "is_hover": (idx == 1),
                        "order": idx,
                        "alt_text": f"{product.name} luxury view {idx + 1}"
                    }
                )

            # Create Variants (Combinations of Colors & Sizes)
            for c_name in p_data["colors"]:
                color_obj = color_objs.get(c_name)
                for s_name in p_data["sizes"]:
                    size_obj = size_objs.get(s_name)
                    sku = f"{product.sku_prefix}-{color_obj.name[:3].upper()}-{size_obj.name.replace(' ', '')}"
                    ProductVariant.objects.get_or_create(
                        product=product,
                        color=color_obj,
                        size=size_obj,
                        defaults={
                            "sku": sku,
                            "stock_quantity": 25,
                            "is_active": True
                        }
                    )

            # Sample Reviews
            Review.objects.get_or_create(
                product=product,
                customer_name="Dr. Folashade Alakija",
                defaults={
                    "customer_email": "folashade@lagosvip.com",
                    "rating": 5,
                    "headline": "Exquisite drape and world-class craftsmanship",
                    "comment": "Wore this to a private gala in Victoria Island and received endless compliments. The silk weight is comparable to Savile Row couture. Proudly representing African luxury.",
                    "verified_purchase": True,
                    "helpful_votes": 14,
                }
            )
            Review.objects.get_or_create(
                product=product,
                customer_name="Julian Montgomery",
                defaults={
                    "customer_email": "julian.m@mayfairlondon.co.uk",
                    "rating": 5,
                    "headline": "Impeccable tailoring, fast international DHL delivery",
                    "comment": "Arrived in London within 3 business days. The fit is razor-sharp and the gold finish buttons are a sublime detail. Will be ordering the coat next.",
                    "verified_purchase": True,
                    "helpful_votes": 9,
                }
            )

        # 7. Coupons
        Coupon.objects.get_or_create(
            code="RELUCENT10",
            defaults={"discount_percent": 10, "min_order_ngn": Decimal("50000"), "is_active": True}
        )
        Coupon.objects.get_or_create(
            code="VIP20",
            defaults={"discount_percent": 20, "min_order_ngn": Decimal("150000"), "is_active": True}
        )

        self.stdout.write(self.style.SUCCESS("Relucent Clothing catalog seed completed successfully!"))
