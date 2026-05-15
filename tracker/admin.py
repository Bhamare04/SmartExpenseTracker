from django.contrib import admin

from .models import Budget, Expense, Income, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'user', 'mobile_number', 'currency', 'updated_at')
	search_fields = ('full_name', 'user__username', 'user__email', 'mobile_number')


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
	list_display = ('source', 'user', 'amount', 'income_date', 'created_at')
	list_filter = ('income_date',)
	search_fields = ('source', 'description', 'user__username')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
	list_display = ('category', 'user', 'amount', 'payment_method', 'expense_date', 'created_at')
	list_filter = ('category', 'payment_method', 'expense_date')
	search_fields = ('description', 'category', 'user__username')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
	list_display = ('user', 'month', 'amount', 'updated_at')
	list_filter = ('month',)

