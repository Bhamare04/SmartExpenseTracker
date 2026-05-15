from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Budget, Expense, Income, Profile


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    mobile_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Mobile Number'}))

    class Meta:
        model = User
        fields = ('full_name', 'username', 'email', 'mobile_number', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number'].strip()
        if Profile.objects.filter(mobile_number=mobile_number).exists():
            raise forms.ValidationError('A profile with this mobile number already exists.')
        return mobile_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].strip().lower()
        user.first_name = self.cleaned_data['full_name'].strip()
        if commit:
            user.save()
            profile = user.profile
            profile.full_name = self.cleaned_data['full_name'].strip()
            profile.mobile_number = self.cleaned_data['mobile_number'].strip()
            profile.save()
        return user


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or email'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ('amount', 'source', 'income_date', 'description')
        widgets = {
            'income_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('amount', 'category', 'payment_method', 'expense_date', 'description', 'receipt_image')
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4, 'data-autosuggest': 'true'}),
        }


class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        input_formats=['%Y-%m-%d', '%Y-%m'],
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Budget
        fields = ('month', 'amount', 'note')
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = (
            'full_name',
            'mobile_number',
            'currency',
            'profile_image',
            'dark_mode',
            'email_notifications',
            'daily_reminder',
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'mobile_number': forms.TextInput(attrs={'placeholder': 'Mobile Number'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        query = User.objects.filter(email__iexact=email)
        if self.user:
            query = query.exclude(pk=self.user.pk)
        if query.exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            self.user.first_name = self.cleaned_data['full_name']
            self.user.save(update_fields=['email', 'first_name'])
        if commit:
            profile.save()
        return profile


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))