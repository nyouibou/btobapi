from django.contrib import admin
from .models import Product,Category,Order,BusinessUser

# Register your models here
admin.site.register(BusinessUser)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
