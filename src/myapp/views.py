from unicodedata import category
from urllib import request

from django.shortcuts import render,HttpResponse,redirect
from .models import register as RegisterUser, contact as contact_model, product as product_model, wishlist as wishlist_model, add_to_cart, checkout as checkout_model, Category, ProductReview, Coupon
from django.core.paginator import Paginator
from  django.core.mail import send_mail
from django.contrib import messages
import random
# Create your views here.
def home(request):
    if "email" in request.session:
        uid = RegisterUser.objects.get(email=request.session['email'])
        # Fetch products for each section
        bestsellers = product_model.objects.filter(bestseller=True)[:6]
        new_releases = product_model.objects.filter(new_release=True)[:6]
        expert_picks = product_model.objects.filter(expert_pick=True)[:6]
        wishlist_ids = set(
            wishlist_model.objects.filter(register=uid).values_list("product_id", flat=True)
        )
        
        context = {
            "bestsellers": bestsellers,
            "new_releases": new_releases,
            "expert_picks": expert_picks,
            "wishlist_ids": wishlist_ids,
        }
        return render(request, "customerapp/home.html", context)
    else:
         return render(request, "accounts/login.html")


def about(request):    
    if "email" in request.session:
        return render(request,"customerapp/about.html")
    else:
        return render(request,"customerapp/login.html")


def contact(request):
    if "email" in request.session:
        uid=RegisterUser.objects.get(email=request.session['email'])

        print(uid.email)

        if request.POST:
            name = request.POST.get("name", '').strip()
            email = request.POST.get("email", '').strip()
            phone = request.POST.get("phone", '').strip()
            subject = request.POST.get("subject", '').strip()
            message = request.POST.get("message", '').strip()

            # Validate all required fields
            if not name or not email or not phone or not subject or not message:
                messages.error(request, 'All fields are required! Please fill in all the fields.')
            else:
                print(name,email,phone,subject,message)
                contact_model.objects.create(name=name,email=email,phone=phone,subject=subject,message=message)
                messages.success(request, 'Your message has been sent successfully!')

        contaxt={
            "uid":uid
        }

        return render(request,"customerapp/contact.html",contaxt)
    else:
        return redirect('accounts:login')

def base(request):
    return render(request, 'customerapp/base.html')


def search(request):
    if request.POST:
        search=request.POST["search"]
        print(search)
        pid=product_model.objects.filter(name__icontains=search)
        contaxt={
            "pid":pid
        }
        return render(request,"customerapp/shop.html",contaxt)

def faq(request):
    return render(request, 'customerapp/faq.html')

# def register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username', '').strip()
#         email = request.POST.get('email', '').strip()
#         password = request.POST.get('password', '').strip()
#         confirm_password = request.POST.get('confirm_password', '').strip()
#         
#         # Check if all fields are filled
#         if not username or not email or not password or not confirm_password:
#             messages.error(request, 'All fields are required. Please fill in all the fields!')
#             return render(request, 'customerapp/register.html')
#         
#         # Check if passwords match
#         if password != confirm_password:
#             messages.error(request, 'Passwords do not match!')
#             return render(request, 'customerapp/register.html')
#         
#         # Check if user already exists
#         if RegisterUser.objects.filter(email=email).exists():
#             messages.error(request, 'Email already exists!')
#             return render(request, 'customerapp/register.html')
#         
#         # Generate OTP
#         
#         # Save user with OTP (but not active yet)
#         user = RegisterUser.objects.create(
#             username=username,
#             email=email,
#             password=password,
#             confirm_password=confirm_password,
#         )
#         
#         # Send OTP email
#         messages.success(request, 'Registration successful! Please login with your credentials.')
#         return redirect('accounts:login')
#     
#     return render(request, 'customerapp/register.html')



# def login(request):
#     if "email" in request.session:
#         return redirect('home')  # Changed from index to home
#     else:
#         if request.method == 'POST':
#             email = request.POST.get("email", '').strip()
#             password = request.POST.get("password", '').strip()
#             
#             # Check if fields are empty
#             if not email or not password:
#                 messages.error(request, 'Email and Password are required!')
#                 return render(request, "customerapp/login.html")
#             
#             try:
#                 uid = RegisterUser.objects.get(email=email)
#                 if password == uid.password:
#                     request.session["email"] = email
#                     return redirect('home')  # Redirects to home page after successful login
#                 else:
#                     messages.error(request, 'Invalid password!')
#                     return render(request, "customerapp/login.html", {"email": email})
#             except RegisterUser.DoesNotExist:
#                 messages.error(request, 'Invalid email!')
#                 return render(request, "customerapp/login.html", {"email": email})
#         
#         return render(request, 'customerapp/login.html')

def logout(request):
    if 'email' in request.session:
        del request.session['email']
    return redirect('accounts:login')



# def forgotpassword(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         if register.objects.filter(email=email).exists():
#             user = register.objects.get(email=email)
#             otp = random.randint(100000, 999999)
#             user.otp = otp
#             user.save()
#             
#             try:
#                 send_mail(
#                     'Password Reset OTP',
#                     f'Your OTP for password reset is: {otp}\nThis OTP will expire in 10 minutes.',
#                     'gohiljayb10@gmail.com',
#                     [email],
#                     fail_silently=False,
#                 )
#                 messages.success(request, 'OTP sent to your email!')
#                 return redirect('reset_password', user_id=user.id)
#             except Exception as e:
#                 messages.error(request, f'Failed to send OTP: {str(e)}')
#         else:
#             messages.error(request, 'Email not found!')
#     
#     return render(request, 'customerapp/forgotpassword.html')

def shop(request):
    products = product_model.objects.all().order_by("-id")
    wishlist_ids = set()
    if "email" in request.session:
        uid = RegisterUser.objects.get(email=request.session['email'])
        wishlist_ids = set(
            wishlist_model.objects.filter(register=uid).values_list("product_id", flat=True)
        )
    selected_category = request.GET.get("category", "all")
    filter_type = request.GET.get("filter", "all")
    sort_by = request.GET.get("sort_by", "newest")

    if selected_category and selected_category != "all":
        products = products.filter(category=selected_category)

    if filter_type == "bestseller":
        products = products.filter(bestseller=True)
    elif filter_type == "new_release":
        products = products.filter(new_release=True)
    elif filter_type == "expert_pick":
        products = products.filter(expert_pick=True)

    if sort_by == "price_low":
        products = products.order_by("price")
    elif sort_by == "price_high":
        products = products.order_by("-price")

    total_count = products.count()
    paginator = Paginator(products, 12)
    page = request.GET.get("page")
    pid = paginator.get_page(page)

    context = {
        "pid": pid,
        "category": selected_category,
        "filter": filter_type,
        "sort_by": sort_by,
        "total_count": total_count,
        "wishlist_ids": wishlist_ids,
    }

    return render(request, "customerapp/shop.html", context)

def checkout(request):
    if "email" not in request.session:
        return redirect('accounts:login')

    uid = RegisterUser.objects.get(email=request.session['email'])
    cart_items = add_to_cart.objects.filter(register=uid, order_status=False).order_by('-id')
    subtotal = sum(item.total for item in cart_items)
    shipping = 40 if subtotal > 0 else 0
    
    discount = 0
    coupon_id = request.session.get('coupon_id')
    if coupon_id and subtotal > 0:
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            discount = coupon.discount_amount
            if discount > subtotal:
                discount = subtotal
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
            
    total = subtotal + shipping - discount

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        full_name = f"{first_name} {last_name}".strip()

        if not first_name or not last_name or not email or not phone or not address or not city or not pincode:
            messages.error(request, 'All fields are required! Please fill in all the fields before checkout.')
        elif not cart_items:
            messages.error(request, 'Your cart is empty. Add products before checkout.')
        else:
            for item in cart_items:
                checkout_model.objects.create(
                    register=uid,
                    name=full_name,
                    email=email,
                    address=address,
                    phone=phone,
                    product_name=item.product_name,
                    image=item.image.name if hasattr(item.image, 'name') else item.image,
                    price=item.price,
                    quantity=item.quantity,
                    total=item.total,
                )
                item.order_status = True
                item.save()

            messages.success(request, 'Checkout completed successfully. Your order is submitted.')
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            return redirect('shop')

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'discount': discount,
        'total': total,
        'uid': uid,
    }
    return render(request, 'customerapp/checkout.html', context)



def product(request, id):
    if "email" in request.session:
        uid = RegisterUser.objects.get(email=request.session['email'])
        spid=product_model.objects.get(id=id)
        is_wishlisted = wishlist_model.objects.filter(register=uid, product=spid).exists()
        reviews = ProductReview.objects.filter(product=spid)
        contaxt={
            "spid":spid,
            "is_wishlisted": is_wishlisted,
            "reviews": reviews,
            "review_count": reviews.count(),
            "user_email": uid.email,
        }
        return render(request,"customerapp/product.html",contaxt)
    else:
        return redirect('accounts:login')

def submit_review(request, id):
    if "email" not in request.session:
        return redirect('accounts:login')
    if request.method == 'POST':
        uid = RegisterUser.objects.get(email=request.session['email'])
        spid = product_model.objects.get(id=id)
        message = request.POST.get('message', '').strip()
        if message:
            ProductReview.objects.create(
                product=spid,
                user=uid,
                email=uid.email,
                message=message,
            )
            messages.success(request, 'Your review has been posted successfully!')
        else:
            messages.error(request, 'Please enter a review message.')
    return redirect('product', id=id)

def blog(request):
    return render(request, 'customerapp/blog.html')

# def reset_password(request, user_id):
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp')
#         new_password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')
#         
#         try:
#             user = register.objects.get(id=user_id)
#             if str(user.otp) == entered_otp:
#                 if new_password == confirm_password:
#                     user.password = new_password
#                     user.confirm_password = confirm_password
#                     user.otp = None
#                     user.save()
#                     messages.success(request, 'Password reset successfully!')
#                     return redirect('accounts:login')
#                 else:
#                     messages.error(request, 'Passwords do not match!')
#             else:
#                 messages.error(request, 'Invalid OTP!')
#         except register.DoesNotExist:
#             messages.error(request, 'User not found!')
#             return redirect('forgotpassword')
#     
#     return render(request, 'customerapp/reset_password.html', {'user_id': user_id})



def wishlist(request):
    if "email" in request.session:
        uid = RegisterUser.objects.get(email=request.session['email'])
        user_wishlist = wishlist_model.objects.filter(register=uid).order_by("-id")

        contaxt = {
            "pid": user_wishlist,
            "wid": user_wishlist,
        }
        return render(request, "customerapp/wishlist.html", contaxt)
    return redirect('accounts:login')


def add_wishlist(request, id):
    if "email" in request.session:
        uid = RegisterUser.objects.get(email=request.session['email'])
        spid = product_model.objects.get(id=id)

        existing = wishlist_model.objects.filter(register=uid, product=spid).first()
        if existing:
            existing.delete()
        else:
            wishlist_model.objects.create(
                register=uid,
                product=spid,
                product_name=spid.name,
                price=spid.price,
                image=spid.image
            )
        return redirect('shop')
    return redirect('accounts:login')


def wishlist_delete(request, id):
    wishlist_model.objects.filter(id=id).delete()
    return redirect('wishlist')


def cart(request):
    print("Cart view called")
    if "email" in request.session:
        print(f"User email in session: {request.session['email']}")
        uid=RegisterUser.objects.get(email=request.session['email'])
        print(f"User found: {uid}")
        pid=add_to_cart.objects.filter(register=uid,order_status=False).order_by("-id")
        print(f"Cart items found: {pid.count()}")
        for item in pid:
            print(f"Cart item: {item.product_name}, quantity: {item.quantity}")
       
        l1=[]
        for i in pid:
            l1.append(i.total)
        print(l1)

        subtotal=sum(l1)
        shipping = 40 if subtotal > 0 else 0
        discount = 0
        applied_coupon_code = None

        coupon_id = request.session.get('coupon_id')
        if coupon_id and subtotal > 0:
            try:
                coupon = Coupon.objects.get(id=coupon_id, is_active=True)
                discount = coupon.discount_amount
                if discount > subtotal:
                    discount = subtotal
                applied_coupon_code = coupon.code
            except Coupon.DoesNotExist:
                del request.session['coupon_id']

        total = subtotal + shipping - discount
        contaxt={
            "pid":pid,
            "l1":l1,
            "subtotal":subtotal,
            "shipping": shipping,
            "total" : total,
            "discount": discount,
            "applied_coupon_code": applied_coupon_code
        }
        return render(request,"customerapp/cart.html",contaxt)
    else:
        return redirect('accounts:login')
    
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip()
        if code:
            try:
                coupon = Coupon.objects.get(code=code, is_active=True)
                request.session['coupon_id'] = coupon.id
                messages.success(request, f'Coupon "{code}" applied successfully!')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code.')
        else:
            messages.error(request, 'Please enter a valid coupon code.')
    return redirect('cart')

def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.info(request, 'Coupon removed successfully.')
    return redirect('cart')

def cart_add(request,id):
    print(f"cart_add called with id: {id}")
    if "email" in request.session:
        print(f"User email in session: {request.session['email']}")
        uid=RegisterUser.objects.get(email=request.session['email'])
        print(f"User found: {uid}")
        next_url = request.META.get("HTTP_REFERER", "/shop/")
        
        # Get quantity from request, default to 1
        qty = request.POST.get('qty', request.GET.get('qty', 1))
        try:
            qty = int(qty)
            if qty < 1: qty = 1
        except (ValueError, TypeError):
            qty = 1

        try:
            spid=product_model.objects.get(id=id)
            print(f"Product found: {spid.name}")
        except product_model.DoesNotExist:
            print("Product not found!")
            messages.error(request, 'Product not found.')
            return redirect(next_url)
        
        # Only check for products that are not yet purchased (order_status=False)
        cart_item = add_to_cart.objects.filter(register=uid, product=spid, order_status=False).first()
        if cart_item:
            # If product already in cart, increase quantity by the requested amount
            cart_item.quantity += qty
            cart_item.total = cart_item.price * cart_item.quantity
            cart_item.save()
            print(f"Updated quantity to {cart_item.quantity}")
        else:
            # Add new product to cart with the requested quantity
            cart_item = add_to_cart.objects.create(
                register=uid, 
                product=spid, 
                product_name=spid.name, 
                price=spid.price, 
                quantity=qty, 
                total=spid.price * qty, 
                order_status=False
            )
            print(f"Created new cart item: {cart_item}")
        
        messages.success(request, f'{qty} item(s) added to cart successfully.')
        return redirect(next_url)
    else:    
        print("No email in session - redirecting to login")
        return redirect('accounts:login')
    

def cart_minus(request,id):
    seid=add_to_cart.objects.get(id=id)
    if seid.quantity >1:
        seid.quantity-=1
        seid.total=seid.price*seid.quantity
        seid.save() 
    else:
        seid.delete()
    return redirect('cart')

def cart_plus(request,id):
    seid=add_to_cart.objects.get(id=id)
    seid.quantity+=1
    seid.total=seid.price*seid.quantity
    seid.save() 
    return redirect('cart')

def cart_delete(request,id):
    seid=add_to_cart.objects.get(id=id)
    seid.delete() 
    return redirect('cart')

def profile(request):
    if "email" not in request.session:
        return redirect('accounts:login')
    
    uid = RegisterUser.objects.get(email=request.session['email'])
    all_orders = checkout_model.objects.filter(register=uid).order_by('-order_date')
    
    # "Active" can be defined as anything not yet delivered
    active_orders = all_orders.exclude(status='Delivered')
    past_orders = all_orders.filter(status='Delivered')
    
    active_items_count = sum(order.quantity for order in active_orders)
    
    context = {
        'uid': uid,
        'active_orders': active_orders,
        'past_orders': past_orders,
        'active_items_count': active_items_count,
    }
    return render(request, 'customerapp/profile.html', context)
