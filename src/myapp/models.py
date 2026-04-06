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
    
    
class product(models.Model):
    name=models.CharField(max_length=50)
    price=models.IntegerField()
    description=models.TextField()
    image=models.ImageField(upload_to="images",blank=True,null=True)
    bestseller=models.BooleanField(default=False)
    new_release=models.BooleanField(default=False)
    expert_pick=models.BooleanField(default=False)

    def __str__(self) -> str:
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


class checkout(models.Model):
    register = models.ForeignKey(register, on_delete=models.CASCADE, blank=True, null=True)
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    address=models.CharField(max_length=50)
    phone=models.CharField(max_length=20, blank=True, null=True)
    product_name=models.CharField(max_length=50)
    price=models.IntegerField()
    quantity=models.IntegerField()
    total=models.IntegerField()
    order_date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.name} - {self.product_name}"
    
    class Meta:
        ordering = ['-order_date']