from django.contrib import admin
from .models import Book, Category, register, contact as contact_model, product, wishlist, add_to_cart, checkout, comment, ProductReview, Coupon

# 1. Custom admin for register model
class RegisterAdmin(admin.ModelAdmin):
    list_display  = ['username', 'email', 'gender', 'phone', 'address']
    list_filter   = ['gender']
    search_fields = ['username', 'email', 'phone', 'address']
    readonly_fields = ['username', 'email', 'password', 'confirm_password', 'otp',
                       'gender', 'phone', 'address', 'image']

    def has_add_permission(self, request):
        return False

admin.site.register(register, RegisterAdmin)


# 2. Custom admin for wishlist model
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['register', 'product_name', 'price']
    search_fields = ['register__username', 'product_name']
    list_filter = ['register']

admin.site.register(wishlist, WishlistAdmin)


# 3. Custom admin for add_to_cart model
class AddToCartAdmin(admin.ModelAdmin):
    list_display = ['register', 'product_name', 'price', 'quantity', 'total', 'order_status']
    list_editable = ['order_status']
    list_filter = ['order_status', 'register']
    search_fields = ['register__username', 'product_name']

admin.site.register(add_to_cart, AddToCartAdmin)


# 4. Custom admin for comment model
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message']
    search_fields = ['name', 'email', 'message']

admin.site.register(comment, CommentAdmin)


# 5. Custom admin for Category model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

admin.site.register(Category, CategoryAdmin)


# 6. Custom admin for product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'author_name', 'published_year', 'bestseller', 'new_release', 'expert_pick']
    list_filter = ['category', 'bestseller', 'new_release', 'expert_pick']
    list_editable = ['bestseller', 'new_release', 'expert_pick']
    search_fields = ['name', 'author_name', 'description']

admin.site.register(product, ProductAdmin)


# 7. Custom admin for Book model
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'price', 'stock']
    list_filter = ['category', 'author']
    search_fields = ['title', 'author', 'category']

admin.site.register(Book, BookAdmin)


# 8. Custom admin for ProductReview model
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'email', 'message', 'created_at']
    list_filter = ['product', 'created_at']
    search_fields = ['email', 'message', 'product__name']
    readonly_fields = ['product', 'user', 'email', 'message', 'created_at']

admin.site.register(ProductReview, ProductReviewAdmin)


# 9. Custom admin for contact model
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'phone', 'message']
    search_fields = ['name', 'email', 'subject', 'phone', 'message']
    list_filter = ['subject']

admin.site.register(contact_model, ContactAdmin)


# 10. Custom admin for checkout model
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


# 11. Custom admin for Coupon model
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_amount', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['code']

admin.site.register(Coupon, CouponAdmin)