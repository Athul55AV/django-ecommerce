from django.contrib import admin
from . models import Product,Customer,Cart,Payment,OrderPlaced,Wishlist,Category,Subscription,Coupon,Ordersummary,ContactMessage,Review,Wallet,WalletTransaction


# Register your models here.
@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ['id','category_choice']

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','price','description','category','stock','stock_value','product_image']


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','name','locality','city','state','zipcode']


@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity']


@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','discount_applied','tax','wallet_deduction','paid']


@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer','name','locality','city','state','zipcode','product','product_title','product_price','product_image_url','quantity','ordered_date','status','payment','coupons_applied']

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product']

@admin.register(Subscription)
class SubscriptionModelAdmin(admin.ModelAdmin):
    list_display = ['name','email','subscribed_at']

@admin.register(Coupon)
class CouponModelAdmin(admin.ModelAdmin):
    list_display = ['code','discount_amount','is_active']
    list_editable = ('is_active',)
    filter_horizontal = ['categories']
    

@admin.register(Ordersummary)
class OrdersummaryModelAdmin(admin.ModelAdmin):
    list_display = ['user','cart_total','discount','tax','order_total','coupon_code','created_at']

@admin.register(ContactMessage)
class ContactMessageModelAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','email','message','created_at']    

@admin.register(Review)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ['product','name','email','number','rating','message','created_at']      

@admin.register(Wallet)
class WalletModelAdmin(admin.ModelAdmin):
    list_display = ['user','balance']     

@admin.register(WalletTransaction)
class WalletTransactionModelAdmin(admin.ModelAdmin):
    list_display = ['user','amount','transaction_type','created_at']       
