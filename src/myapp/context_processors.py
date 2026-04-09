from django.db.models import Sum

from .models import add_to_cart, register, wishlist


def cart_summary(request):
    cart_count = 0
    wishlist_count = 0

    email = request.session.get("email")
    if not email:
        return {"cart_count": cart_count, "wishlist_count": wishlist_count}

    user = register.objects.filter(email=email).first()
    if not user:
        return {"cart_count": cart_count, "wishlist_count": wishlist_count}

    cart_count = (
        add_to_cart.objects.filter(register=user, order_status=False)
        .aggregate(total_qty=Sum("quantity"))
        .get("total_qty")
        or 0
    )
    wishlist_count = wishlist.objects.filter(register=user).count()

    return {"cart_count": cart_count, "wishlist_count": wishlist_count}
