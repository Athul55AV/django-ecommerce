from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import RegexValidator,MinValueValidator
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField


# Create your models here.



STATE_CHOICES=(
    ('Kerala','Kerala'),
    ('TamilNadu','TamilNadu'),
    ('Karnataka','Karnataka'),
    ('Telangana','Telangana'),
    ('Andra','Andra')

)

STOCK_CHOICES=(
    ('InStock','InStock'),
    ('OutofStock','OutofStock'),
)
STATUS_CHOICES=(
    ('Active','Active'),
    ('Blocked','Blocked'),
)

class Category(models.Model):
    category_choice = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_choice)
        super().save(*args, **kwargs)
  
    def __str__(self):
        return self.category_choice


class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.PositiveIntegerField(validators=[MinValueValidator(0.0)])
    description = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    stock = models.CharField(choices=STOCK_CHOICES,max_length=20,default='InStock')
    status = models.CharField(choices=STATUS_CHOICES,max_length=20,default='Active')
    stock_value = models.PositiveIntegerField(default=0)
    product_image = CloudinaryField('product')

    def save(self, *args, **kwargs):
        if self.stock_value == 0:
            self.stock = 'OutofStock'
        else:
            self.stock = 'InStock'
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title


class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10,validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')])
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES,max_length=100)
    def __str__(self):
        return self.name

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    def __str__(self):
        return f"{self.balance}"
    
class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    transaction_type = models.CharField(max_length=10, choices=[('CREDIT', 'Credit'), ('DEBIT', 'Debit'), ('REFUND', 'Refund')])
    created_at = models.DateTimeField(auto_now_add=True)    

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.price
    
STATUS_CHOICES = (
    ('Pending','Pending'),
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
    ('Return','Return'),
)

class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    discount_amount = models.PositiveIntegerField(help_text="Flat discount amount in ₹")
    is_active = models.BooleanField(default=True)

    categories = models.ManyToManyField(Category, blank=True, related_name='coupons')

    def __str__(self):
        return self.code
    

class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    discount_applied = models.FloatField(max_length=100,blank=True,null=True)
    tax = models.FloatField(max_length=100,blank=True,null=True)
    wallet_deduction = models.FloatField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)


class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True,blank=True)

    name = models.CharField(max_length=200,null=True, blank=True)
    locality = models.CharField(max_length=200,null=True, blank=True)
    city = models.CharField(max_length=50,null=True, blank=True)
    mobile = models.CharField(max_length=10,null=True, blank=True)
    zipcode = models.IntegerField(null=True, blank=True)
    state = models.CharField(max_length=100,null=True, blank=True)
    
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True)

    product_title = models.CharField(max_length=200, null=True, blank=True)
    product_price = models.PositiveIntegerField(null=True, blank=True)
    product_image_url = models.URLField(null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
    coupons_applied = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)

    
    @property
    def total_cost(self):
        return (self.product_price or 0) * self.quantity

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)


class Subscription(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    
class Ordersummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_total = models.FloatField()
    discount = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    order_total = models.FloatField()
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"   
    

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} by {self.name}"   