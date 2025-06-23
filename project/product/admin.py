from django.contrib import admin
from .models import Product, Category  # ✅ Import both models

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "description", "category")  # ✅ Proper tuple syntax

# Register the models
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
