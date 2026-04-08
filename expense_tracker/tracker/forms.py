from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction
from .models import Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class TransactionForm(forms.ModelForm):
    new_category = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Or create new category"}),
        help_text="Type a category name here to create and use it for this transaction.",
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'transaction_type', 'date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'category': forms.Select(),
            'transaction_type': forms.Select(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Optional note...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['category'].required = False
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = (cleaned_data.get('new_category') or '').strip()
        amount = cleaned_data.get('amount')

        if amount is not None and amount <= 0:
            self.add_error('amount', 'Amount must be greater than zero.')

        if not category and not new_category:
            self.add_error('category', 'Select a category or create a new one.')

        if new_category:
            normalized_name = ' '.join(new_category.split())
            existing_category = Category.objects.filter(name__iexact=normalized_name).first()
            category = existing_category or Category.objects.create(name=normalized_name)
            cleaned_data['category'] = category

        return cleaned_data