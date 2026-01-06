from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from .forms import customuserchangeform,customproductchangeform,customproductAddform,customorderchangeform,customcategoriesAddform,customcategorieschangeform,customcodeAddform,customcodechangeform
from userpanel.models import Product,OrderPlaced,Category,Coupon,Payment,Subscription,ContactMessage,Review,Customer
from django.db.models import Q
from django.utils.timezone import now
import base64
from django.core.files.base import ContentFile
from cloudinary.uploader import upload as cloudinary_upload
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth,ExtractYear

# Create your views here.
@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    pending_orders = OrderPlaced.objects.filter(status='Pending').order_by('-ordered_date')
    return_orders = OrderPlaced.objects.filter(status='Return')
    outofstock_products = Product.objects.filter(stock="OutofStock")
    paid_orders = OrderPlaced.objects.filter(payment__paid=True)
    total_revenue = sum(order.total_cost for order in paid_orders)
    today = now().date()
    today_paid_orders = paid_orders.filter(ordered_date__date=today)
    today_revenue = sum(order.total_cost for order in today_paid_orders)
    monthly_sales = (
        paid_orders
        .annotate(month=TruncMonth('ordered_date'))
        .values('month')
        .annotate(
            total_sales=Sum(F('product_price') * F('quantity'))
        )
        .order_by('month')
    )
    yearly_sales = (
        paid_orders
        .annotate(year=ExtractYear('ordered_date'))
        .values('year')
        .annotate(
            total_sales=Sum(F('product_price') * F('quantity'))
        )
        .order_by('year')
    )

    yearly_labels = [str(y['year']) for y in yearly_sales]
    yearly_data = [y['total_sales'] or 0 for y in yearly_sales]

    chart_labels = [sale['month'].strftime('%b %Y') for sale in monthly_sales]
    chart_data = [sale['total_sales'] or 0 for sale in monthly_sales]
    return render(request,'adminpanel/index.html',{'pending_orders': pending_orders,'return_orders': return_orders,'outofstock_products':outofstock_products,'total_revenue': total_revenue,'today_revenue': today_revenue,'chart_labels': chart_labels,'chart_data': chart_data,'yearly_labels': yearly_labels,'yearly_data': yearly_data,})

def base(request):
    contact_msg = ContactMessage.objects.all()
    latest_messages = ContactMessage.objects.order_by('-created_at')[:3]
    return render(request,'adminpanel/base.html',locals())

def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request,form.save())
            return redirect('sindex')
    else:
        form = UserCreationForm()
    return render(request,'adminpanel/registration.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            login(request,form.get_user())
            return redirect('sindex')
    else:
        form = AuthenticationForm()
    return render(request,'adminpanel/login.html',{'form':form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('slogin_view')

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)    
def accounts(request):
    users = User.objects.all().order_by("id")
    return render(request, 'adminpanel/accounts.html',{'users': users})

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_users(request,user_id):
    user = get_object_or_404(User,id=user_id)
    if request.method == 'POST':
        form = customuserchangeform(request.POST,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,'User Updated Successfully')
            return redirect('saccounts')
    else:
        form = customuserchangeform(instance=user)
    return render(request,'adminpanel/editusers.html',{'form':form,'user_obj':user})


def delete_users(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('saccounts')  
    # return render(request, 'delete_users.html', {'user_obj': user})


def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password reset successfully.")
            return redirect('saccounts')
    else:
        form = SetPasswordForm(user)
    return render(request,'adminpanel/reset_password.html',{'form':form,'user_obj':user})

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def products(request):
    if request.method == 'POST':
        form = customproductAddform(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sproducts')
    else:
        form = customproductAddform()
    products = Product.objects.all().order_by("-id")
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(title__icontains=search_query)

    category = request.GET.get('category', '')
    if category:
        products = products.filter(category__category_choice=category)

    stock = request.GET.get('stock', '')
    if stock:
        products = products.filter(stock=stock)    

    sort_by = request.GET.get('sort', '')
    if sort_by:
        products = products.order_by(sort_by)
    return render(request, 'adminpanel/products.html',locals())



@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_products(request, product_id):
    products = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = customproductchangeform(request.POST, request.FILES, instance=products)

        if form.is_valid():
            # Get cropped image data from hidden input (if any)
            cropped_data = request.POST.get('cropped_image_data', '')

            if cropped_data:
                try:
                    # cropped_data looks like: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
                    format, imgstr = cropped_data.split(';base64,')
                    ext = format.split('/')[-1]              # "jpeg", "png", etc.
                    data = base64.b64decode(imgstr)

                    file_name = f"product_{products.id}_cropped.{ext}"
                    upload_result = cloudinary_upload(
                        ContentFile(data, name=file_name),
                        folder="products"  # optional: choose your folder
                    )
                    # ✅ Assign cropped image to the model instance
                    form.instance.product_image = upload_result["public_id"]
                except Exception as e:
                    # Optional: print(e) or log it
                    pass

            # This will now save all fields, including the (possibly replaced) product_image
            form.save()
            messages.success(request, 'product Updated Successfully')
            return redirect('sproducts')
    else:
        form = customproductchangeform(instance=products)

    return render(
        request,
        'adminpanel/edit_products.html',
        {'form': form, 'product_obj': products}
    )




def delete_products(request, product_id):
    products = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        products.delete()
        messages.success(request, 'product deleted successfully.')
        return redirect('sproducts')  
    
@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def categories(request):
    if request.method == 'POST':
        form = customcategoriesAddform(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('scategories')
    else:
        form = customcategoriesAddform()
    categories = Category.objects.all().order_by("id")
    return render(request, 'adminpanel/categories.html',locals())    

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_categories(request,categories_id):
    categories = get_object_or_404(Category,id=categories_id)
    if request.method == 'POST':
        form = customcategorieschangeform(request.POST,request.FILES,instance=categories)
        if form.is_valid():
            form.save()
            messages.success(request,'category Updated Successfully')
            return redirect('scategories')
    else:
        form = customcategorieschangeform(instance=categories)
    return render(request,'adminpanel/edit_categories.html',{'form':form,'categories_obj':categories})


def delete_categories(request, categories_id):
    categories = get_object_or_404(Category, id=categories_id)
    if request.method == 'POST':
        if categories.products.exists():
            messages.error(
                request,
                f"Cannot delete category {categories.category_choice} because it has associated products."
            )
            return redirect('scategories')
        categories.delete()
        messages.success(request, 'category deleted successfully.')
        return redirect('scategories')  


def blank(request):
    return render(request,'adminpanel/blank.html')

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def orders(request):
    orders = OrderPlaced.objects.all().order_by('-ordered_date')
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(Q(user__username__icontains=search_query) | Q(product__title__icontains =search_query))

    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    sort_by = request.GET.get('sort', '')
    if sort_by:
        orders = orders.order_by(sort_by)    
    return render(request, 'adminpanel/orders.html',{'orders': orders})

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_detail(request, pk):
    order = get_object_or_404(OrderPlaced, pk=pk)
    allorder = OrderPlaced.objects.filter(payment__razorpay_order_id=order.payment.razorpay_order_id)
    torder = 0
    print(order.payment.tax)
    for t in allorder:
        torder = torder + t.total_cost
    return render(request, "adminpanel/order_detail.html",{"order": order,"allorder": allorder,"torder":torder})

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_orders(request,order_id):
    order = get_object_or_404(OrderPlaced,id=order_id)
    if request.method == 'POST':
        form = customorderchangeform(request.POST,request.FILES,instance=order)
        if form.is_valid():
            form.save()
            messages.success(request,'order Updated Successfully')
            return redirect('sorders')
    else:
        form = customorderchangeform(instance=order)
    return render(request,'adminpanel/edit_orders.html',{'form':form,'order_obj':order})


def search(request):   
    users = User.objects.all().order_by("id")
    products = Product.objects.all().order_by("id")
    search_query = request.GET.get('fullsearch', '')
    if search_query:
        products = products.filter(title__icontains=search_query)
        users = users.filter(username__icontains=search_query)    
    return render(request,"adminpanel/search.html",locals())


@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def orders_single(request,user_id):
    user = get_object_or_404(User, id=user_id)
    orders = OrderPlaced.objects.filter(user=user).order_by('-ordered_date')
    return render(request, 'adminpanel/orders_single.html',{'orders': orders,'user_obj':user})


@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def code(request):
    if request.method == 'POST':
        form = customcodeAddform(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('scode')
    else:
        form = customcodeAddform()
    codes = Coupon.objects.all().order_by("id")
    return render(request, 'adminpanel/code.html',locals())    


@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_code(request,code_id):
    codes = get_object_or_404(Coupon,id=code_id)
    if request.method == 'POST':
        form = customcodechangeform(request.POST,request.FILES,instance=codes)
        if form.is_valid():
            form.save()
            messages.success(request,'Coupon Updated Successfully')
            return redirect('scode')
    else:
        form = customcodechangeform(instance=codes)
    return render(request,'adminpanel/edit_code.html',{'form':form,'code_obj':codes})


def delete_code(request, code_id):
    codes = get_object_or_404(Coupon, id=code_id)
    if request.method == 'POST':
        codes.delete()
        messages.success(request, 'Coupon deleted successfully.')
        return redirect('scode')  
    
@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def subscription(request):
    subscription = Subscription.objects.all()
    return render(request, 'adminpanel/subscriptions.html',{'subscription': subscription})    


@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Contact_MSG(request):
    contact_msg = ContactMessage.objects.all()
    return render(request, 'adminpanel/contact_msg.html',{'contact_msg': contact_msg})    


@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_review(request):
    prd_review = Review.objects.all().order_by('-created_at')    
    return render(request, 'adminpanel/product_review.html',{'prd_review': prd_review})  

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def single_review(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    prd_rev = product.reviews.all().order_by('-created_at')  
    
    return render(request, 'adminpanel/single_review.html',{'prd_rev': prd_rev,'product': product})  

@staff_member_required(login_url='/sadmin/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def address_view(request,user_id):
    user = get_object_or_404(User, id=user_id)
    address = Customer.objects.filter(user=user)
    return render(request, 'adminpanel/address_view.html',{'address': address,'user_obj':user})