from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordChangeForm,UsernameField,SetPasswordForm,PasswordResetForm
from django.contrib.auth.models import User
from . models import Customer,Subscription,ContactMessage,Review

class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": (
            "Login failed. Please check your username and password. "
        ),
        "inactive": (
            "Your account has been blocked. Please contact customer care."
        ),
    }
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus ':'True','class':'form-control','placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control','placeholder': 'Enter your password'}))



class CustomerRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus ':'True','class':'form-control','placeholder': 'Choose a username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder': 'Enter your email'}))
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder': 'Enter password'}))
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalpha():
            raise forms.ValidationError("Username must contain only alphabets (A–Z).")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'autofocus':'True','autocomplete':'current-password','class':'form-control'}))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))

class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))

class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','locality','city','mobile','state','zipcode']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'locality':forms.TextInput(attrs={'class':'form-control'}),
            'city':forms.TextInput(attrs={'class':'form-control'}),
            'mobile':forms.NumberInput(attrs={'class':'form-control'}),
            'state':forms.Select(attrs={'class':'form-control'}),
            'zipcode':forms.NumberInput(attrs={'class':'form-control'})

        }
        error_messages = {
            'mobile': {'max_length': 'Enter a valid 10-digit mobile number'}
        }
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Name should only contain letters.")
        return name
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        mobile_str = str(mobile).strip()
        if not mobile_str.isdigit():
            raise forms.ValidationError("Enter a valid 10-digit mobile number")
        if len(mobile_str) != 10:
            raise forms.ValidationError("Enter a valid 10-digit mobile number")
        if mobile and int(mobile) < 0:
            raise forms.ValidationError("Enter a valid 10-digit mobile number")

        return mobile_str
    
    def clean_zipcode(self):
        zipcode = self.cleaned_data.get('zipcode')
        if zipcode <= 0:
            raise forms.ValidationError("Enter a valid zipcode.")
        if len(str(zipcode)) not in [5, 6]:
            raise forms.ValidationError("Enter a valid zipcode.")
        return zipcode

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'email']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','placeholder': 'Enter your Name'}),
            'email':forms.EmailInput(attrs={'class':'form-control','placeholder': 'Enter your Email'})
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'message']      
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'fname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'lname'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'id': 'message', 'rows': 5}),
        }  


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'number', 'message','rating']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Your Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Email Address'}),
            'number': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Phone Number'}),
            'message': forms.Textarea(attrs={'class': 'form-control','rows': 1,'placeholder': 'Review'}),
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')]),
        }        