from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([Variant,Product,ProductImage,ProductVariant,ProductVariantPrice])