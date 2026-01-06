from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from userpanel.models import Product,OrderPlaced,Category,Coupon
from django.utils.safestring import mark_safe

class customuserchangeform(UserChangeForm):
    class Meta:
        model = User
        fields = ['username','email','is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class customproductAddform(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'price', 'description', 'category', 'status', 'stock_value','product_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product title'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price','min': 0}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.Select(attrs={'class': 'form-control'}),
            'stock_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock_value','min': 0}),
            'product_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price
    def clean_stock_value(self):
        stock_value = self.cleaned_data.get('stock_value')
        if stock_value is not None and stock_value < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        if stock_value is not None and stock_value > 20:
            raise forms.ValidationError("Stock quantity exceeded.")
        return stock_value

class customproductchangeform(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title','price','description','category', 'status', 'stock_value','product_image']
        widgets = {
            "product_image": forms.ClearableFileInput()
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create preview image markup with a known id
        if self.instance and self.instance.pk and self.instance.product_image:
            img_url = self.instance.product_image.url
            self.fields['product_image'].help_text = mark_safe(
                f'<img id="product_image_preview" src="{img_url}" height="150" '
                'style="border-radius:8px; margin-top:10px; display:block;" />'
            )
        else:
            # placeholder <img> (hidden) so JS can always find the element
            self.fields['product_image'].help_text = mark_safe(
                '<img id="product_image_preview" src="" height="150" '
                'style="border-radius:8px; margin-top:10px; display:none;" />'
            )
    def clean_product_image(self):
        image = self.cleaned_data.get('product_image')
        if not image and self.instance and self.instance.product_image:
            return self.instance.product_image
        return image
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price
    def clean_stock_value(self):
        stock_value = self.cleaned_data.get('stock_value')
        if stock_value is not None and stock_value < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        if stock_value is not None and stock_value > 20:
            raise forms.ValidationError("Stock quantity exceeded.")
        return stock_value

class customorderchangeform(forms.ModelForm):
    class Meta:
        model = OrderPlaced
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            current_status = self.instance.status
            status_order = ['Pending', 'Accepted', 'Packed', 'On The Way', 'Delivered', 'Cancel', 'Return']
            if current_status in ['Cancel', 'Return']:
                allowed_statuses = [current_status]
            else:
                allowed_statuses = [
                s for s in status_order
                if status_order.index(s) >= status_order.index(current_status)
                or s in ['Cancel', 'Return']
                ]
        self.fields['status'].choices = [(s, s) for s in allowed_statuses]    


class customcategoriesAddform(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_choice']
        widgets = {
            'category_choice': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Category'}),
        }

class customcategorieschangeform(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_choice']

class customcodeAddform(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount_amount','is_active','categories']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Code'}),
            'discount_amount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount_amount'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categories': forms.CheckboxSelectMultiple()
        }

class customcodechangeform(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount_amount','is_active','categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple()
        }