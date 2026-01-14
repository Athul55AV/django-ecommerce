from django.conf import settings
from django.urls import path
from userpanel.views import *
from django.conf.urls.static import static
from .forms import MyPasswordResetForm,LoginForm,MyPasswordChangeForm,MySetPasswordForm
from django.contrib.auth import views as auth_view



urlpatterns = [
    path('',base,name='base'),
    
    path('index/',index,name='index'),
    path('about/',about,name='about'),
    path('contact/',contact,name='contact'),
    path('account/',account,name='account'),
    path('category/<slug:val>',CategoryView.as_view(),name='category'),
    path('productdetail/<int:pk>',ProductDetail.as_view(),name='productdetail'),
    path('profile/',ProfileView.as_view(),name='profile'),
    path('userprofile/',userprofile,name='userprofile'),
    path('address/',address,name='address'),
    path('updateAddress/<int:pk>',updateAddress.as_view(),name='updateAddress'),
    path('deleteAddress/<int:pk>',deleteAddress,name ='deleteAddress'),

    path('add-to-cart/',add_to_cart, name='add-to-cart'),
    path('showcart/',show_cart, name='showcart'),
    path('pluscart/',plus_cart, name='pluscart'),
    path('minuscart/',minus_cart, name='minuscart'),
    path('removecart/',remove_cart, name='removecart'),

    path('buynow/<int:pk>/',buynow.as_view(), name='buynow'),
    path('cod_order/', cod_order, name='cod_order'),
    path("cod_success/", cod_success, name="cod_success"),



    path('checkout/',checkout.as_view(),name='checkout'),
    path('paymentdone/',payment_done,name='paymentdone'),
    path('orders/',orders,name='orders'),
    path("orders/<int:pk>/",order_detail, name="orderdetail"),
    path('cancelorder/',cancel_order, name='cancelorder'),
    path('returnorder/',return_order, name='returnorder'),

    path('wallet/', wallet_view, name='wallet'),
    path('wallet_add/', add_money, name='add_money'),
    path("wallet_full_payment/", wallet_full_payment, name="wallet_full_payment"),


    path('applycoupon/',apply_coupon, name='applycoupon'),
    path('remove_coupon/',remove_coupon, name='remove_coupon'),
    path('apply-wallet/', apply_wallet, name='apply_wallet'),

    path('pluswishlist/',plus_wishlist,name='pluswishlist'),
    path('minuswishlist/',minus_wishlist,name='minuswishlist'),

    path('wishlist/',show_wishlist, name='wishlist'),
    path('removewishlist/',remove_wishlist, name='removewishlist'),

    path('search/',search,name='search'),
    path('privacypolicy/',privacypolicy,name='privacypolicy'),
    path('termsconditions/',termsconditions,name='termsconditions'),

    path('customerregistration/',CustomerRegistrationView.as_view(),name='customerregistration'),
    path('account/login/',auth_view.LoginView.as_view(template_name='userpanel/login.html',authentication_form=LoginForm),name='login'),
    path('logout/',auth_view.LogoutView.as_view(next_page='login'),name='logout_view'),
    path('passwordchange/',auth_view.PasswordChangeView.as_view(template_name='userpanel/changepassword.html',form_class=MyPasswordChangeForm,success_url='/passwordchangedone'),name='passwordchange'),
    path('passwordchangedone/',auth_view.PasswordChangeDoneView.as_view(template_name='userpanel/passwordchangedone.html'),name='passwordchangedone'),
    # path('password-reset/',auth_view.PasswordResetView.as_view(template_name='userpanel/password_reset.html',form_class=MyPasswordResetForm),name='password_reset'),
    # path('password-reset/done',auth_view.PasswordResetDoneView.as_view(template_name='userpanel/password_reset_done.html'),name='password_reset_done'),
    # path('password-reset-confirm/<uidb64>/<token>/',auth_view.PasswordResetConfirmView.as_view(template_name='userpanel/password_reset_confirm.html',form_class=MySetPasswordForm),name='password_reset_confirm'),
    # path('password-reset-complete/',auth_view.PasswordResetCompleteView.as_view(template_name='userpanel/password_reset_complete.html'),name='password_reset_complete'),

    path('password-reset/', auth_view.PasswordResetView.as_view(template_name='userpanel/password_reset.html',form_class=MyPasswordResetForm,email_template_name='userpanel/password_reset_email.html',subject_template_name='userpanel/password_reset_subject.txt',), name='password_reset'),
    path('password-reset/done/', auth_view.PasswordResetDoneView.as_view(template_name='userpanel/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(template_name='userpanel/password_reset_confirm.html',form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('reset/done/', auth_view.PasswordResetCompleteView.as_view(template_name='userpanel/password_reset_complete.html'), name='password_reset_complete'),



]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)