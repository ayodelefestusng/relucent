from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Address, Review, NewsletterSubscriber, Order


class CustomUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-none focus:outline-none focus:border-[#C9A865] text-sm font-sans transition-colors'
            })


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-none focus:outline-none focus:border-[#C9A865] text-sm font-sans transition-colors'
            })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-none focus:outline-none focus:border-[#C9A865] text-sm font-sans transition-colors'
            })


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('full_name', 'phone', 'street_address', 'apartment', 'city', 'state', 'country', 'postal_code', 'is_default_shipping')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-none focus:outline-none focus:border-[#C9A865] text-sm font-sans transition-colors'
                })


class CheckoutForm(forms.Form):
    # Customer Info
    customer_name = forms.CharField(max_length=150, required=True)
    customer_email = forms.EmailField(required=True)
    customer_phone = forms.CharField(max_length=30, required=True)

    # Shipping Address
    shipping_address = forms.CharField(max_length=255, required=True)
    apartment = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    country = forms.ChoiceField(
        choices=[
            ('Nigeria', 'Nigeria'),
            ('United Kingdom', 'United Kingdom'),
            ('United States', 'United States'),
            ('Canada', 'Canada'),
            ('Ghana', 'Ghana'),
            ('Kenya', 'Kenya'),
            ('South Africa', 'South Africa'),
            ('Germany', 'Germany'),
            ('France', 'France'),
            ('United Arab Emirates', 'United Arab Emirates'),
        ],
        initial='Nigeria',
        required=True
    )
    postal_code = forms.CharField(max_length=30, required=False)

    # Shipping & Payment Options
    shipping_method = forms.ChoiceField(
        choices=[
            ('dhl_local', 'DHL Express Nationwide Nigeria (1-2 Business Days) - ₦5,000'),
            ('dhl_intl', 'DHL International Worldwide Priority (3-5 Business Days) - ₦25,000 / $25'),
            ('lagos_express', 'Same Day Lagos VIP Courier - ₦7,500'),
        ],
        initial='dhl_local',
        required=True
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('paystack', 'Paystack (Debit/Credit Card, Bank Transfer, USSD)'),
            ('flutterwave', 'Flutterwave (Mobile Money, Global Cards)'),
            ('stripe', 'Stripe (Apple Pay, Google Pay, Global Cards)'),
            ('bank_transfer', 'Direct Bank Transfer / Private Concierge'),
        ],
        initial='paystack',
        required=True
    )
    coupon_code = forms.CharField(max_length=50, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-none focus:outline-none focus:border-[#C9A865] text-sm font-sans transition-colors'
            })


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'headline', 'comment', 'customer_name', 'customer_email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-none focus:outline-none focus:border-[#C9A865] text-sm font-sans transition-colors'
            })


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-white/60 text-white placeholder-white/60 focus:outline-none focus:border-[#C9A865] text-sm transition-colors',
            'placeholder': 'Enter your email for 10% off'
        })


class SizeRecommendationForm(forms.Form):
    FIT_CHOICES = [
        ('slim', 'Slim Tailored Fit'),
        ('regular', 'Classic Regular Fit'),
        ('relaxed', 'Relaxed Oversized Fit'),
    ]
    height_cm = forms.IntegerField(min_value=120, max_value=230, initial=175, label="Height (cm)")
    weight_kg = forms.IntegerField(min_value=35, max_value=180, initial=70, label="Weight (kg)")
    fit_preference = forms.ChoiceField(choices=FIT_CHOICES, initial='regular', label="Fit Preference")
