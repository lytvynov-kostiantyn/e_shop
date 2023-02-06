from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BrandFilter, CountryFilter, User, Category, Sale, Product, Comments, Basket

# adding new fields to User interface
fields = list(UserAdmin.fieldsets)
fields[1] = (
    'Personal Info',
    {'fields': ('first_name', 'last_name', 'email', 'address', 'phone_number', 'purchase_amount')}
)
fields[2] = (
    'Permissions',
    {'fields': ('is_superuser', 'is_staff', 'is_active', 'email_verify')}
)
UserAdmin.fieldsets = tuple(fields)

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(BrandFilter)
admin.site.register(CountryFilter)
admin.site.register(Comments)
admin.site.register(Basket)
