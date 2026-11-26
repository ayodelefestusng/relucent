import os
import random
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from fashion_app.models import Collection, ProductImage

GALLERY_PATH = r'C:\Users\Pro\Desktop\CLIENTS\RAVEXAH\FASHION\Highlights'

class Command(BaseCommand):
    help = 'Bulk replace collection banners and product images with files from local gallery.'

    def handle(self, *args, **options):
        if not os.path.isdir(GALLERY_PATH):
            self.stderr.write(self.style.ERROR(f'Gallery path not found: {GALLERY_PATH}'))
            return
        files = [f for f in os.listdir(GALLERY_PATH) if os.path.isfile(os.path.join(GALLERY_PATH, f))]
        if not files:
            self.stdout.write(self.style.WARNING('No files found in gallery path.'))
            return
        random.shuffle(files)
        # Ensure media subfolders exist
        banner_dir = Path(settings.MEDIA_ROOT) / 'banners'
        product_dir = Path(settings.MEDIA_ROOT) / 'product_images'
        banner_dir.mkdir(parents=True, exist_ok=True)
        product_dir.mkdir(parents=True, exist_ok=True)
        # Assign images to collections (first N files)
        collections = Collection.objects.filter(is_active=True)
        for col, filename in zip(collections, files):
            src = Path(GALLERY_PATH) / filename
            dest = banner_dir / filename
            shutil.copy2(src, dest)
            col.banner_image_url.name = f'banners/{filename}'
            col.save(update_fields=['banner_image_url'])
            self.stdout.write(f'Updated Collection {col.name} banner with {filename}')
        # Assign remaining images to product images (create if none)
        remaining = files[len(collections):]
        product_images = list(ProductImage.objects.all())
        for filename in remaining:
            src = Path(GALLERY_PATH) / filename
            dest = product_dir / filename
            shutil.copy2(src, dest)
            if product_images:
                pi = product_images.pop(0)
                pi.image_url.name = f'product_images/{filename}'
                pi.save(update_fields=['image_url'])
                self.stdout.write(f'Updated ProductImage {pi.id} with {filename}')
            else:
                # Create a new ProductImage for a random product
                product = random.choice(list(ProductImage.objects.values_list('product', flat=True)))
                pi = ProductImage.objects.create(product_id=product, image_url=f'product_images/{filename}')
                self.stdout.write(f'Created new ProductImage for product {product} with {filename}')
        self.stdout.write(self.style.SUCCESS('Image replacement completed.'))
