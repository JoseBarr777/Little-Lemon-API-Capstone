from django.contrib import admin

from .models import Category, MenuItem, Cart, Order, OrderItem

# Register your models here.

# admin.site.register(Category)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug")
    search_fields = ("title", "slug")

# admin.site.register(MenuItem)
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "featured", "category")
    list_filter = ("featured", "category")
    search_fields = ("title",)
    list_editable = ("price",)
    ordering = ("id",)
    list_per_page = 10
    

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)