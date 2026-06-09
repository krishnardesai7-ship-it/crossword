from django.db import models
from django.utils import timezone

# Create your models here.
class register(models.Model):
    username=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    password=models.TextField(max_length=50)
    otp=models.IntegerField(blank=True,null=True)
    confirm_password=models.TextField(max_length=50)
    s_name=models.CharField(max_length=50,blank=True,null=True)
    education=models.CharField(max_length=50,blank=True,null=True)
    address=models.CharField(max_length=50,blank=True,null=True)
    phone=models.CharField(max_length=20,blank=True,null=True)
    gender=models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    image=models.ImageField(upload_to="images",blank=True,null=True)

    def __str__(self) -> str:
        return self.username
    
    
    
    
class contact(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    subject=models.CharField(max_length=50)
    message=models.TextField()
    phone=models.IntegerField(blank=True,null=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class product(models.Model):
    CATEGORY_CHOICES = [
        ("love_story", "Love Story"),
        ("fantasy", "Fantasy"),
        ("juvenile_literature", "juvenile literature"),
        ("mystery", "Mystery"),
        ("thrillers", "Thrillers"),
        ("self_health_and_personal_growth", "Self Health and Personal Growth"),
        ("health_fitness_and_wellness", "Health Fitness and Wellness"),
        ("spirituality_and_philosophy", "Spirituality and Philosophy"),
        ("science_natural_and_technology", "Science Natural and Technology"),
        ("leadership_and_management", "Leadership and Management"),
        ("productivity_and_time_management", "Productivity and Time Management"),
        ("career_professional_development", "Career Professional Development"),
        ("holy_books_religious_texts_or_scriptures", "Holy Books, Religious Texts, or Scriptures"),
    ]

    name = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    author_name = models.CharField(max_length=200, blank=True, null=True)
    published_year = models.CharField(max_length=10, blank=True, null=True)
    summary_pdf = models.FileField(upload_to='book_summaries/', blank=True, null=True, help_text="PDF summary of the book")

    # Stored as text in current DB schema (`myapp_product.category`)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default="romance")

    bestseller = models.BooleanField(default=False)
    new_release = models.BooleanField(default=False)
    expert_pick = models.BooleanField(default=False)
    recommendation_tags = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated tags for recommendations (e.g., education, motivation, adventure)")

    def __str__(self):
        return self.name
    
class wishlist(models.Model):
    product=models.ForeignKey(product,on_delete=models.CASCADE,blank=True,null=True)
    register=models.ForeignKey(register,on_delete=models.CASCADE,blank=True,null=True)
    image=models.ImageField(upload_to='images')
    product_name=models.CharField(max_length=50)
    price=models.IntegerField()

    def __str__(self) -> str:
        return self.product_name
    
    
class add_to_cart(models.Model):
    product=models.ForeignKey(product,on_delete=models.CASCADE,blank=True,null=True)
    register=models.ForeignKey(register,on_delete=models.CASCADE,blank=True,null=True)
    image=models.ImageField(upload_to='images', blank=True, null=True)
    product_name=models.CharField(max_length=50)
    price=models.IntegerField()
    quantity=models.IntegerField()
    total=models.IntegerField()
    order_status=models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.product_name
    
class comment(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    message=models.TextField()

    def __str__(self) -> str:
        return self.name

class ProductReview(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(register, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review by {self.email} on {self.product.name}"

    class Meta:
        ordering = ['-created_at']


class checkout(models.Model):
    register = models.ForeignKey(register, on_delete=models.CASCADE, blank=True, null=True)
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    address=models.CharField(max_length=50)
    phone=models.CharField(max_length=20, blank=True, null=True)
    product_name=models.CharField(max_length=50)
    image=models.TextField(null=True, blank=True)
    price=models.IntegerField()
    quantity=models.IntegerField()
    total=models.IntegerField()
    status = models.CharField(max_length=20, default='Pending', choices=[('Pending', 'Pending'), ('Processed', 'Processed'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')])
    order_date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.name} - {self.product_name}"
    
    class Meta:
        ordering = ['-order_date']

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.IntegerField(default=0, help_text="Flat discount amount in ₹")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, default="Unknown") 
    category = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    image = models.ImageField(upload_to='books/', null=True, blank=True)
    def __str__(self):
        return self.title


class BookPurchase(models.Model):
    """Track user book purchases for personalization and recommendations"""
    user = models.ForeignKey(register, on_delete=models.CASCADE, related_name='book_purchases')
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name='purchases')
    order = models.ForeignKey(checkout, on_delete=models.CASCADE, related_name='book_purchases', null=True, blank=True)
    purchased_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    class Meta:
        ordering = ['-purchased_date']
        unique_together = ('user', 'product', 'purchased_date')


class PersonalizedRecommendation(models.Model):
    """Store personalized book recommendations based on user purchase history"""
    user = models.ForeignKey(register, on_delete=models.CASCADE, related_name='recommendations')
    recommended_product = models.ForeignKey(product, on_delete=models.CASCADE)
    recommendation_reason = models.CharField(max_length=500, help_text="Why this book is recommended")
    match_score = models.FloatField(default=0.0, help_text="Recommendation match score 0-100")
    created_at = models.DateTimeField(default=timezone.now)
    is_viewed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Recommendation for {self.user.username} - {self.recommended_product.name}"
    
    class Meta:
        ordering = ['-match_score', '-created_at']
        unique_together = ('user', 'recommended_product')