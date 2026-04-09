from django.contrib import admin
from .models import Category, register, contact as contact_model, product, wishlist, add_to_cart, checkout, comment, ProductReview
# Register your models here.
admin.site.register(register)
admin.site.register(wishlist)
admin.site.register(add_to_cart)
admin.site.register(comment)
admin.site.register(Category)
admin.site.register(product)

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'email', 'message', 'created_at']
    list_filter = ['product', 'created_at']
    search_fields = ['email', 'message', 'product__name']
    readonly_fields = ['product', 'user', 'email', 'message', 'created_at']

admin.site.register(ProductReview, ProductReviewAdmin)
# Custom admin for product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'bestseller', 'new_release', 'expert_pick']
    list_filter = ['bestseller', 'new_release', 'expert_pick']
    list_editable = ['bestseller', 'new_release', 'expert_pick']
    search_fields = ['name', 'description']



admin.site.register(contact_model)

# Custom admin for checkout model to display all products
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ['order_date', 'name', 'email', 'product_name', 'total', 'status']
    list_editable = ['status']
    list_filter = ['status', 'order_date', 'name', 'email']
    search_fields = ['name', 'email', 'product_name', 'phone', 'register__username']
    readonly_fields = ['name', 'email', 'address', 'phone', 'product_name', 'price', 'quantity', 'total', 'order_date', 'register']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True

admin.site.register(checkout, CheckoutAdmin)