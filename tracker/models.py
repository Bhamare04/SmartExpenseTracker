from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
	CURRENCY_CHOICES = [
		('INR', 'Indian Rupee (INR)'),
		('USD', 'US Dollar (USD)'),
		('EUR', 'Euro (EUR)'),
		('GBP', 'British Pound (GBP)'),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	full_name = models.CharField(max_length=150, blank=True, default='')
	mobile_number = models.CharField(max_length=20, blank=True, null=True)
	profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
	currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='INR')
	dark_mode = models.BooleanField(default=True)
	email_notifications = models.BooleanField(default=True)
	daily_reminder = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.full_name or self.user.get_username()


class Income(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
	amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
	source = models.CharField(max_length=120)
	income_date = models.DateField(default=timezone.localdate)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-income_date', '-created_at']

	def __str__(self) -> str:
		return f'{self.source} - {self.amount}'


class Expense(models.Model):
	CATEGORY_CHOICES = [
		('Food', 'Food'),
		('Travel', 'Travel'),
		('Shopping', 'Shopping'),
		('Bills', 'Bills'),
		('Entertainment', 'Entertainment'),
		('Health', 'Health'),
		('Education', 'Education'),
		('Others', 'Others'),
	]

	PAYMENT_CHOICES = [
		('Cash', 'Cash'),
		('Card', 'Card'),
		('UPI', 'UPI'),
		('Bank Transfer', 'Bank Transfer'),
		('Wallet', 'Wallet'),
		('Other', 'Other'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
	amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
	category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Others')
	payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UPI')
	expense_date = models.DateField(default=timezone.localdate)
	description = models.TextField(blank=True)
	receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-expense_date', '-created_at']

	def __str__(self) -> str:
		return f'{self.category} - {self.amount}'


class Budget(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
	month = models.DateField(default=timezone.localdate)
	amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
	note = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['user', 'month'], name='unique_budget_per_user_month'),
		]
		ordering = ['-month']

	def __str__(self) -> str:
		return f'{self.user.get_username()} - {self.month:%B %Y}'


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(
			user=instance,
			full_name=instance.get_full_name() or instance.get_username(),
		)


@receiver(post_save, sender=User)
def save_profile_for_user(sender, instance, **kwargs):
	if hasattr(instance, 'profile'):
		instance.profile.save()
