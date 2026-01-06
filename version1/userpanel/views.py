from django.http import JsonResponse,Http404
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.views import View
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.db.models import Count,Avg
from . forms import CustomerRegistrationForm,CustomerProfileForm,SubscriptionForm,ContactForm,ReviewForm
from userpanel.models import Customer,Product,Cart,Payment,OrderPlaced,Wishlist,Category,Subscription,Coupon,Review,Wallet,WalletTransaction
from django.contrib import messages
from django.db.models import Q
import razorpay
from django.conf import settings
from django.utils.decorators import method_decorator
import time
from django.contrib.auth.decorators import permission_required
from django.db import IntegrityError, DatabaseError
import logging
logger = logging.getLogger(__name__)

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def base(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user)) 
    return render(request,'userpanel/base.html',locals())

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    try:
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))

        if request.method == "POST":
            form = SubscriptionForm(request.POST)
            email = request.POST.get('email')

            if Subscription.objects.filter(email=email).exists():
                return JsonResponse({
                    "status": "exists",
                    "message": "You are already subscribed!"
                })

            if form.is_valid():
                form.save()
                return JsonResponse({
                    "status": "success",
                    "message": "Thank you for subscribing!"
                })
            
            return JsonResponse({
                "status": "error",
                "message": "Invalid data. Please check your input."
            })

        else:
            form = SubscriptionForm()

        return render(request, 'userpanel/index.html', locals())
    except DatabaseError:
        logger.exception("Database error on index")
        return JsonResponse({"status": "error", "message": "Database issue"}, status=500)

    except Exception:
        logger.exception("Unexpected error on index")
        return JsonResponse({"status": "error", "message": "Something went wrong"}, status=500)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def about(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user))  
    return render(request,'userpanel/about.html',locals())

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def contact(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user)) 
    success = False    
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactForm() 
    else:
        form = ContactForm()   
    return render(request,'userpanel/contact.html',locals())


@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def account(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))  
    return render(request,'userpanel/account.html',locals())

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userprofile(request):
    return render(request, 'userpanel/userprofile.html')

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch') 
class CategoryView(View):
    def get(self,request,val):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))   
            wishitem = len(Wishlist.objects.filter(user=request.user))  
        category = get_object_or_404(Category, slug=val)
        product = Product.objects.filter(category=category, status="Active")
        titles = product.values('title')
        return render(request,'userpanel/category.html',locals())


@method_decorator(login_required(login_url='/account/login/'), name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch') 
class ProductDetail(View):
    def get(self,request,pk):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))   
            wishitem = len(Wishlist.objects.filter(user=request.user))      
        for key in ['single_coupon', 'single_discount']:
            request.session.pop(key, None)    

        product = get_object_or_404(Product, pk=pk)
        reviews = Review.objects.filter(product=product)
        total_reviews = reviews.count()
        overall_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
        incart = Cart.objects.filter(Q(product=product) & Q(user=request.user))
        form = ReviewForm()
        reviews = product.reviews.all()
        return render(request,'userpanel/productdetail.html',locals())
    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        reviews = Review.objects.filter(product=product)
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.save()
            form.save()
            return redirect('productdetail', pk=pk)
        reviews = product.reviews.all()
        return render(request,'userpanel/productdetail.html',locals())


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')   
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,'userpanel/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            login(request,form.save())
            return redirect('index')
        for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
        return render(request,'userpanel/customerregistration.html',locals())


@method_decorator(login_required(login_url='/account/login/'), name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class ProfileView(View):
    def get(self,request):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))   
            wishitem = len(Wishlist.objects.filter(user=request.user))          
        form = CustomerProfileForm()
        return render(request,'userpanel/profile.html',locals())

    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            
            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Profile Saved Successfully")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
        return render(request,'userpanel/profile.html',locals())

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)    
def address(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user))      
    add = Customer.objects.filter(user=request.user)
    return render(request,'userpanel/address.html',locals())


@method_decorator(login_required(login_url='/account/login/'), name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))   
            wishitem = len(Wishlist.objects.filter(user=request.user))          
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request,'userpanel/updateAddress.html',locals())
    def post(self,request,pk):
        add = Customer.objects.get(pk=pk, user=request.user)
        form = CustomerProfileForm(request.POST,instance=add)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('address')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
        return render(request,'userpanel/updateAddress.html',locals())


@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True) 
def deleteAddress(request, pk):
    add = Customer.objects.get(pk=pk)
    if request.method == 'POST':
        add.delete()
        messages.success(request, 'Address deleted.')
        return redirect('address')  
    


def add_to_cart(request):
    try:
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))   
            wishitem = len(Wishlist.objects.filter(user=request.user))      
        user = request.user
        product_id = request.GET.get('prod_id')
        product = Product.objects.get(id=product_id)
        Cart(user=user,product=product).save()
        Wishlist.objects.filter(user=user, product=product).delete()
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        if 'cart_coupon' in request.session:
            del request.session['cart_coupon']
            if 'discount' in request.session:
                del request.session['discount']
        return redirect("/showcart")
    except Http404:
        messages.error(request, "Product not found")
        return redirect("index")

    except IntegrityError:
        messages.warning(request, "Item already in cart")
        return redirect("showcart")

    except Exception:
        logger.exception("Add to cart failed")
        messages.error(request, "Unable to add product")
        return redirect("index")

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_cart(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user))      
    user = request.user
    cart = Cart.objects.filter(user=user).order_by('-id')
    amount = 0
    for p in cart:
        value = p.quantity * p.product.price
        p.total = p.quantity * p.product.price
        amount = amount + value
    totalamount = amount
    return render(request,'userpanel/addtocart.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
        product = c.product
        
        if c.quantity < product.stock_value:
            c.quantity += 1
            c.save()
            status = 'success'
            message = 'Quantity updated successfully.'
        else:
            status = 'warning'
            message = f'Only {product.stock_value} item(s) available in stock.'

        for key in ['cart_coupon', 'discount']:
            request.session.pop(key, None)
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.price
            p.total = p.quantity * p.product.price
            amount = amount + value
        totalamount = amount
        data = {
            'quantity':c.quantity,
            'item_total':c.quantity * c.product.price,
            'amount':amount,
            'totalamount':totalamount,
            'status': status,
            'message': message,
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
        if c.quantity > 1:
            c.quantity-=1
            c.save()
        for key in ['cart_coupon', 'discount']:
            request.session.pop(key, None)    
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.price
            p.total = p.quantity * p.product.price
            amount = amount + value
        totalamount = amount
        data = {
            'quantity':c.quantity,
            'item_total':c.quantity * c.product.price,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
        c.delete()
        for key in ['cart_coupon', 'discount']:
            request.session.pop(key, None)        
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.price
            p.total = p.quantity * p.product.price
            amount = amount + value
        totalamount = amount
        cart_count = cart.count()
        data = {
            'amount':amount,
            'totalamount':totalamount,
            'cart_count': cart_count,
        }
        return JsonResponse(data)

@method_decorator(login_required(login_url='/account/login/'), name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')  
class checkout(View):
    def get(self,request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        out_of_stock_items = []
        for item in cart_items:
            if item.product.stock == "OutofStock" or item.product.status == "Blocked":
                out_of_stock_items.append(item.product.title)

        if out_of_stock_items:
            messages.error(
                request,
                f"These items are out of stock and cannot be purchased: {', '.join(out_of_stock_items)}"
            )
            return redirect('showcart')
        balance = Wallet.objects.get(user=user)
        wallet_balance = balance.balance
        add = Customer.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.price
            famount = famount + value   
        coupon_instance = None
        discount = 0
        coupon_code = request.session.get('cart_coupon')
        if coupon_code:
            try:
                coupon_instance = Coupon.objects.get(code=coupon_code, is_active=True)
                discount = float(coupon_instance.discount_amount)
            except Coupon.DoesNotExist:
                discount = 0
        else:
            discount = 0

        sub_total = max(famount - discount, 0)
        tax = round(sub_total * 0.18)
        order_total = sub_total + tax
        totalamount = order_total       
        #print(coupon_code)
        razoramount = int(totalamount * 100)



        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razoramount, "currency": "INR", "receipt": f"order_rcptid_{int(time.time())}"}
        payment_response = client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']

        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status,
                discount_applied=discount,
                tax=tax                
            )
            payment.save()

        return render(request,'userpanel/checkout.html',locals())
    

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    product_id = request.GET.get('product_id')
    user = request.user
    customer = Customer.objects.get(id=cust_id)
    payment = Payment.objects.get(razorpay_order_id=order_id)

    if not order_id or order_id == "undefined":
        messages.error(request, "Payment failed or invalid order ID.")
        return redirect("checkout")

    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
    except Payment.DoesNotExist:
        messages.error(request, "No payment record found for this order.")
        return redirect("checkout")

    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    address_data = {
        'name': customer.name,
        'locality': customer.locality,
        'city': customer.city,
        'state': customer.state,
        'zipcode': customer.zipcode,
        'mobile': customer.mobile,
    }
    if product_id:
        product = Product.objects.get(id=product_id)
        OrderPlaced(user=user, customer=customer, product=product, quantity=1, payment=payment,product_title=product.title,product_price=product.price,product_image_url=product.product_image.url if product.product_image else None,**address_data).save()
        product.stock_value -= 1
        if product.stock_value < 0:
            product.stock_value = 0
        product.save()
    else:
        cart = Cart.objects.filter(user=user)
        for c in cart:
            OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment=payment,product_title=c.product.title,product_price=c.product.price,product_image_url=c.product.product_image.url if c.product.product_image else None,**address_data).save()
            c.product.stock_value -= c.quantity
            if c.product.stock_value < 0:
                c.product.stock_value = 0
            c.product.save()
            c.delete()

    return redirect("orders")


@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def orders(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user))      
    order_placed = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')
    #print(order_placed)
    #for orders in order_placed:
    #    print(orders.payment.discount_applied)

    
    return render(request,'userpanel/orders.html',locals())

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_detail(request, pk):
    order = get_object_or_404(OrderPlaced, pk=pk)
    allorder = OrderPlaced.objects.filter(payment__razorpay_order_id=order.payment.razorpay_order_id)
    torder = 0
    #print(order.payment.tax)
    for t in allorder:
        torder = torder + t.total_cost   
    return render(request, "userpanel/order_detail.html",{"order": order,"allorder": allorder,"torder":torder})


def plus_wishlist(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully'
        }
        return JsonResponse(data)
    
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Wishlist Removed Successfully'
        }
        return JsonResponse(data)

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)    
def show_wishlist(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user))      
    user = request.user
    wishlist = Wishlist.objects.filter(user=user).order_by('-id')
    incart = list(Cart.objects.filter(user=user).values_list('product_id',flat=True))
    return render(request,'userpanel/wishlist.html',locals())
    
def remove_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Wishlist.objects.get(Q(product = prod_id) & Q(user = request.user))
        c.delete()
        user = request.user
        wishlist = Wishlist.objects.filter(user=user)
        wishlist_count = wishlist.count()
        return JsonResponse({'status': 'success','wishlist_count': wishlist_count,})

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search(request):
    query = request.GET.get('search', '')
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user))      
    order_placed = OrderPlaced.objects.filter(user=request.user)    
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,"userpanel/search.html",locals())


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def privacypolicy(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user)) 
    return render(request,'userpanel/privacypolicy.html',locals())

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def termsconditions(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))   
        wishitem = len(Wishlist.objects.filter(user=request.user)) 
    return render(request,'userpanel/termsconditions.html',locals())


def cancel_order(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']
        order = OrderPlaced.objects.get(Q(id = order_id) & Q(user = request.user))
        order.status = 'Cancel'
        order.save()
        product = order.product
        product.stock_value += order.quantity
        product.save()     
        payment = order.payment
        if payment and payment.razorpay_payment_status == 'COD':
            refund_amount = order.payment.amount

            if refund_amount > 0:
                wallet, created = Wallet.objects.get_or_create(user=request.user)
                wallet.balance += refund_amount
                wallet.save()

                WalletTransaction.objects.create(
                    user=request.user,
                    amount=refund_amount,
                    transaction_type='REFUND'
                )
        return JsonResponse({'status': 'success'})

def return_order(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']
        order = OrderPlaced.objects.get(Q(id = order_id) & Q(user = request.user))
        order.status = 'Return'
        order.save()
        product = order.product
        product.stock_value += order.quantity
        product.save()
        return JsonResponse({'status': 'success'})    

@method_decorator(login_required(login_url='/account/login/'), name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')  
class buynow(View):
    def get(self, request, pk):
        user = request.user
        add = Customer.objects.filter(user=user)
        
        product = Product.objects.get(pk=pk)

        famount = product.price  
        coupon_instance = None
        discount = 0
        coupon_code = request.session.get('single_coupon')
        if coupon_code:
            try:
                coupon_instance = Coupon.objects.get(code=coupon_code, is_active=True)
                discount = float(coupon_instance.discount_amount)
            except Coupon.DoesNotExist:
                discount = 0
                request.session.pop('single_coupon', None)


        sub_total = max(famount - discount, 0)
        tax = round(sub_total * 0.18)
        order_total = sub_total + tax
        totalamount = order_total       

        razoramount = int(totalamount * 100) 
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razoramount, "currency": "INR", "receipt": f"order_rcptid_{product.id}_{int(time.time())}"}
        payment_response = client.order.create(data=data)
        print(payment_response)

        order_id = payment_response['id']
        order_status = payment_response['status']

        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status,
                discount_applied=discount,
                tax=tax                
            )
            payment.save()


        cart_items = [{
            "product": product,
            "quantity": 1,
            "total": famount
        }]
        
        return render(request, "userpanel/singlecheckout.html", locals())

def apply_coupon(request):
    if request.method == "GET":
        code = request.GET.get("code") 
        ctype = request.GET.get("type", "cart")
        user = request.user
        try:
            coupon = Coupon.objects.get(code=code, is_active=True) 
            allowed_categories = coupon.categories.all()
            if ctype == "cart":
                cart_items = Cart.objects.filter(user=user)
                eligible_items = [item for item in cart_items if item.product.category in allowed_categories]

                if not eligible_items:
                    return JsonResponse({"success": False, "message": "This coupon is not applicable for your cart items."})

                famount = sum(item.quantity * item.product.price for item in cart_items)
                request.session['cart_coupon'] = code
                session_discount_key = 'cart_discount'

            else:  
                product_id = request.GET.get("prod_id")
                product = get_object_or_404(Product, id=product_id)

                if product.category not in allowed_categories:
                    return JsonResponse({"success": False, "message": "This coupon is not applicable for this product."})

                famount = product.price
                request.session['single_coupon'] = code
                session_discount_key = 'single_discount'
            
         
            discount = float(coupon.discount_amount)
            if famount < discount:
                return JsonResponse({"success": False, "message": "Coupon cannot be applied as amount is less than coupon discount."})

            sub_total = max(famount - discount, 0)
            tax = round(sub_total * 0.18)
            order_total = sub_total + tax
            totalamount = order_total
            razoramount = int(order_total * 100)
            request.session[session_discount_key] = discount

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            

            data_order = {
                "amount": razoramount,
                "currency": "INR",
                "receipt": f"order_rcptid_coupon_{int(time.time())}"
            }
            payment_response = client.order.create(data=data_order)
            payment = Payment.objects.create(
                user=user,
                amount=order_total,
                razorpay_order_id=payment_response['id'],
                razorpay_payment_status='created',
                discount_applied=discount,
                tax=tax
            )
            request.session['active_payment_id'] = payment.id
            request.session['active_order_id'] = payment_response['id']
            request.session['active_tax'] = tax
            request.session['active_order_total'] = order_total
            request.session['active_discount'] = discount

            return JsonResponse({"success": True, "discount": discount,"tax": tax,"order_total": order_total,"order_id": payment_response['id'],"razoramount": razoramount})
        except Coupon.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid or inactive coupon."})
        


def remove_coupon(request):
    user = request.user
    code_type = request.GET.get("type", "cart")  
    if code_type == "cart":
        request.session.pop('cart_coupon', None)
        request.session.pop('cart_discount', None)

    else:
        request.session.pop('single_coupon', None)
        request.session.pop('single_discount', None)

    if code_type == "cart":
        cart_items = Cart.objects.filter(user=user)
        famount = sum(item.quantity * item.product.price for item in cart_items)
    else:
        product_id = request.GET.get("prod_id")
        product = get_object_or_404(Product, id=product_id)
        famount = product.price

 
    sub_total = famount
    tax = round(sub_total * 0.18)
    order_total = sub_total + tax
    razoramount = int(order_total * 100)


    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    data_order = {
        "amount": razoramount,
        "currency": "INR",
        "receipt": f"order_rcptid_coupon_cancel_{int(time.time())}"
    }
    payment_response = client.order.create(data=data_order)

    payment = Payment.objects.create(
        user=user,
        amount=order_total,
        razorpay_order_id=payment_response['id'],
        razorpay_payment_status='created',
        discount_applied=0,  
        tax=tax
    )


    request.session['active_payment_id'] = payment.id
    request.session['active_order_id'] = payment_response['id']
    request.session['active_tax'] = tax
    request.session['active_order_total'] = order_total
    request.session['active_discount'] = 0

 
    return JsonResponse({
        "success": True,
        "message": "Coupon removed successfully.",
        "discount": 0,
        "tax": tax,
        "order_total": order_total,
        "order_id": payment_response['id'],
        "razoramount": razoramount
    })    





def create_razorpay_order(request):
    if request.method == "POST":
        user = request.user
        product_id = request.POST.get("product_id")
        cust_id = request.POST.get("cust_id")
        total = float(request.POST.get("total"))  
        

        razoramount = int(total * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        data = {
            "amount": razoramount,
            "currency": "INR",
            "receipt": f"order_rcptid_{product_id}_{int(time.time())}",
        }
        payment_response = client.order.create(data=data)

        return JsonResponse({
            "order_id": payment_response["id"],
            "amount": razoramount
        })


@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cod_order(request):
    user = request.user
    cust_id = request.GET.get('cust_id')
    product_id = request.GET.get('product_id')

    try:
        customer = Customer.objects.get(id=cust_id)
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "message": "Customer not found."})

    famount = 0
    product = None
    if product_id:  
        product = Product.objects.get(id=product_id)
        famount = product.price
        coupon_code = request.session.get('single_coupon')
    else:  
        cart_items = Cart.objects.filter(user=user)
        famount = sum(item.quantity * item.product.price for item in cart_items)
        coupon_code = request.session.get('cart_coupon')

    discount = 0
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            discount = float(coupon.discount_amount)
        except Coupon.DoesNotExist:
            discount = 0


    sub_total = max(famount - discount, 0)
    tax = round(sub_total * 0.18)
    totalamount = sub_total + tax    
    
    wallet_deduction = request.session.get('wallet_deduction', 0)
    wallet_applied = request.session.get('wallet_applied', False)
    print(wallet_deduction)
    if wallet_applied and wallet_deduction > 0:
        totalamount = max(totalamount - wallet_deduction, 0)
    
    payment = Payment.objects.create(
        user=user,
        amount=totalamount,
        razorpay_order_id=f"COD_{int(time.time())}",
        razorpay_payment_status="COD",
        discount_applied=discount,
        tax=tax,
        paid=False
    )

    address_data = {
        'name': customer.name,
        'locality': customer.locality,
        'city': customer.city,
        'state': customer.state,
        'zipcode': customer.zipcode,
        'mobile': customer.mobile,
    }


    if product_id:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "Product not found."})

        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=product,
            quantity=1,
            payment=payment,
            product_title=product.title,
            product_price=product.price,
            product_image_url=product.product_image.url if product.product_image else None,
            **address_data
        )
        product.stock_value = max(product.stock_value - 1, 0)
        product.save()


    else:
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return JsonResponse({"success": False, "message": "Cart is empty."})
        for c in cart_items:
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                payment=payment,
                product_title=c.product.title,
                product_price=c.product.price,
                product_image_url=c.product.product_image.url if c.product.product_image else None,
                **address_data
            )
            c.product.stock_value = max(c.product.stock_value - c.quantity, 0)
            c.product.save()
            c.delete()
    request.session.pop('wallet_deduction', None)
    request.session.pop('wallet_applied', None)

    return JsonResponse({"success": True})

@login_required(login_url='/account/login/')
def cod_success(request):
    return render(request, "userpanel/cod_success.html")

def apply_wallet(request):
    if request.method == "POST":
        user = request.user
        wallet = Wallet.objects.get(user=user)
        wallet_balance = wallet.balance
        product_id = request.GET.get('product_id')
        if product_id:  
            product = Product.objects.get(id=product_id)
            coupon_code = request.session.get('single_coupon')
        else:  
            cart_items = Cart.objects.filter(user=user)
            coupon_code = request.session.get('cart_coupon')
        discount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                discount = float(coupon.discount_amount)
            except Coupon.DoesNotExist:
                discount = 0

        total_amount = float(request.POST.get("total_amount"))
        action = request.POST.get("action")
        payment_id = request.session.get('active_payment_id')
        payment = Payment.objects.filter(id=payment_id, user=user).first()
        
        if not payment:
            return JsonResponse({"success": False, "message": "Payment not found"})
        tax = request.session.get('active_tax', 0)
        order_total = request.session.get('active_order_total', total_amount)

        if action == "apply":

            wallet_deduction = min(wallet_balance, total_amount)
            payable_amount = total_amount - wallet_deduction

            wallet.balance -= wallet_deduction
            wallet.save()
    

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            razoramount = int(payable_amount * 100)
            print(payable_amount)
            data_order = {
                "amount": razoramount,
                "currency": "INR",
                "receipt": f"order_rcptid_wallet_{int(time.time())}"
            }
            payment_response = client.order.create(data=data_order)
            print(payment_response)
            new_payment = Payment.objects.create(
                user=user,
                amount=payable_amount,
                razorpay_order_id=payment_response['id'],
                razorpay_payment_status='created',
                discount_applied=discount,
                wallet_deduction = wallet_deduction,
                tax=tax
            )
            WalletTransaction.objects.create(
                    user=request.user,
                    amount=wallet_deduction,
                    transaction_type='DEBIT'
                )
            request.session['wallet_deduction'] = wallet_deduction
            request.session['wallet_applied'] = True
            request.session['active_payment_id'] = new_payment.id
            request.session['active_order_id'] = payment_response['id']
            request.session['active_order_total'] = payable_amount
            return JsonResponse({
                "success": True,
                "action": "apply",
                "wallet_deduction": wallet_deduction,
                "payable_amount": payable_amount,
                "wallet_balance_remaining": wallet.balance,
                "order_id": payment_response['id'],
                "order_total": payable_amount,
                "razoramount": payable_amount
            })

        elif action == "cancel":
            
            wallet_deduction = payment.wallet_deduction or 0
            wallet.balance += wallet_deduction
            wallet.save()
            payable_amount = float(request.POST.get("total_amount", 0))
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            razoramount = int(payable_amount * 100)
            data_order = {
                "amount": razoramount,
                "currency": "INR",
                "receipt": f"order_rcptid_wallet_cancel_{int(time.time())}"
            }
            payment_response = client.order.create(data=data_order)
            new_payment = Payment.objects.create(
                user=user,
                amount=payable_amount,
                razorpay_order_id=payment_response['id'],
                razorpay_payment_status='created',
                discount_applied=discount,
                wallet_deduction=0,
                tax=tax
            )
            WalletTransaction.objects.filter(user=user, transaction_type='DEBIT').order_by('-id').first().delete()
            request.session.pop('wallet_deduction', None)
            request.session['wallet_applied'] = False
            request.session['active_payment_id'] = new_payment.id
            request.session['active_order_id'] = payment_response['id']
            request.session['active_order_total'] = payable_amount
            return JsonResponse({
                "success": True,
                "action": "cancel",
                "wallet_refunded": wallet_deduction,
                "payable_amount": payable_amount,
                "wallet_balance_remaining": wallet.balance,
                "order_id": payment_response['id'],
                "razoramount": payable_amount,
                "order_total": payable_amount,
            })

    return JsonResponse({"success": False, "message": "Invalid request method"})

@login_required(login_url='/account/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'userpanel/wallet.html', {'wallet': wallet,'transactions': transactions})


def add_money(request):
    if request.method == "POST":
        amount = float(request.POST.get('amount', 0))
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.save()

        WalletTransaction.objects.create(
            user=request.user,
            amount=amount,
            transaction_type='CREDIT'
        )
        return redirect('wallet')
    
def wallet_full_payment(request):
    user = request.user
    cust_id = request.GET.get('cust_id')
    product_id = request.GET.get('product_id')

    try:
        customer = Customer.objects.get(id=cust_id)
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "message": "Customer not found."})

    famount = 0
    product = None

 
    if product_id:
        product = Product.objects.get(id=product_id)
        famount = product.price
        coupon_code = request.session.get('single_coupon')
    else:
        cart_items = Cart.objects.filter(user=user)
        famount = sum(item.quantity * item.product.price for item in cart_items)
        coupon_code = request.session.get('cart_coupon')


    discount = 0
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            discount = float(coupon.discount_amount)
        except Coupon.DoesNotExist:
            discount = 0

    sub_total = max(famount - discount, 0)
    tax = round(sub_total * 0.18)
    totalamount = sub_total + tax


    wallet = Wallet.objects.get(user=user)
    if wallet.balance < totalamount:
        return JsonResponse({
            "success": False,
            "message": "Insufficient wallet balance to complete this order."
        })

 
    wallet.balance -= totalamount
    wallet.save()

    WalletTransaction.objects.create(
        user=user,
        amount=totalamount,
        transaction_type='DEBIT'
    )

 
    payment = Payment.objects.create(
        user=user,
        amount=totalamount,
        razorpay_order_id=f"WALLET_{int(time.time())}",
        razorpay_payment_status="WALLET",
        discount_applied=discount,
        tax=tax,
        paid=True
    )

    address_data = {
        'name': customer.name,
        'locality': customer.locality,
        'city': customer.city,
        'state': customer.state,
        'zipcode': customer.zipcode,
        'mobile': customer.mobile,
    }


    if product_id:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=product,
            quantity=1,
            payment=payment,
            product_title=product.title,
            product_price=product.price,
            product_image_url=product.product_image.url if product.product_image else None,
            **address_data
        )
        product.stock_value = max(product.stock_value - 1, 0)
        product.save()
    else:
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return JsonResponse({"success": False, "message": "Cart is empty."})
        for c in cart_items:
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                payment=payment,
                product_title=c.product.title,
                product_price=c.product.price,
                product_image_url=c.product.product_image.url if c.product.product_image else None,
                **address_data
            )
            c.product.stock_value = max(c.product.stock_value - c.quantity, 0)
            c.product.save()
            c.delete()

  
    request.session.pop('wallet_deduction', None)
    request.session.pop('wallet_applied', None)

    return JsonResponse({"success": True})


def custom_404(request, exception=None):
    path = request.path
    if path.startswith('/sadmin'):
        home_url = '/sadmin/index'
    else:
        home_url = '/index'

    return render(request, 'userpanel/404.html', {'home_url': home_url}, status=404)

