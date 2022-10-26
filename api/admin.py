# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Category, Discount, ProductItem, Promocode, Basket, Order, Cashback, RegistredUser


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent')


class PromocodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent', 'expire')
    search_fields = ('name', )


class ProductItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'count_on_stock', 'category')
    search_fields = ('name', 'category__name')
    list_select_related = ('category', )


class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'number_of_items')
    search_fields = ('user__phone', 'product__name')
    list_select_related = ('user', 'product')


class OrderInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.get_fields()]


class CashbackAdmin(admin.ModelAdmin):
    list_display = ('percent', 'allowed_amount_to_substract')


class RegistredUserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'cashback_points', 'login', 'email')
    search_fields = ('phone', 'email')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(ProductItem, ProductItemAdmin)
admin.site.register(Promocode, PromocodeAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(Order, OrderInfoAdmin)
admin.site.register(Cashback, CashbackAdmin)
admin.site.register(RegistredUser, RegistredUserAdmin)

