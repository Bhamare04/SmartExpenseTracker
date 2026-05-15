from __future__ import annotations

import csv
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph

from .forms import BudgetForm, ExpenseForm, IncomeForm, LoginForm, ProfileUpdateForm, RegistrationForm
from .models import Budget, Expense, Income, Profile
from .utils import build_budget_snapshot, category_breakdown, category_suggestion, dashboard_summary, monthly_series


def home(request):
	return render(request, 'tracker/home.html')


def register_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	form = RegistrationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		login(request, user, backend='tracker.auth_backends.EmailOrUsernameBackend')
		messages.success(request, 'Registration successful. Welcome to Smart Expense Tracker.')
		return redirect('dashboard')
	return render(request, 'registration/register.html', {'form': form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	form = LoginForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		identifier = form.cleaned_data['username_or_email']
		password = form.cleaned_data['password']
		user = authenticate(request, username=identifier, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, 'Login successful.')
			return redirect(request.GET.get('next') or 'dashboard')
		messages.error(request, 'Invalid login credentials.')
	return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
	logout(request)
	messages.success(request, 'You have been logged out successfully.')
	return redirect('home')


@login_required
def dashboard(request):
	context = dashboard_summary(request.user)
	context['budget_snapshot'] = build_budget_snapshot(request.user)
	context['chart_payload'] = {
		'monthly': monthly_series(request.user),
		'categories': category_breakdown(request.user, year=timezone.localdate().year),
	}
	return render(request, 'tracker/dashboard.html', context)


@login_required
def income_page(request):
	incomes = Income.objects.filter(user=request.user)
	return render(request, 'tracker/income_list.html', {'incomes': incomes})


@login_required
def income_add(request):
	form = IncomeForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		income = form.save(commit=False)
		income.user = request.user
		income.save()
		messages.success(request, 'Income added successfully.')
		return redirect('income_list')
	return render(request, 'tracker/income_form.html', {'form': form, 'mode': 'Add'})


@login_required
def income_edit(request, pk):
	income = get_object_or_404(Income, pk=pk, user=request.user)
	form = IncomeForm(request.POST or None, instance=income)
	if request.method == 'POST' and form.is_valid():
		form.save()
		messages.success(request, 'Income updated successfully.')
		return redirect('income_list')
	return render(request, 'tracker/income_form.html', {'form': form, 'mode': 'Edit'})


@login_required
def income_delete(request, pk):
	income = get_object_or_404(Income, pk=pk, user=request.user)
	if request.method == 'POST':
		income.delete()
		messages.success(request, 'Income deleted successfully.')
	return redirect('income_list')


@login_required
def expense_page(request):
	search = request.GET.get('search', '').strip()
	category = request.GET.get('category', '')
	date_filter = request.GET.get('date', '')
	expenses = Expense.objects.filter(user=request.user)
	if search:
		expenses = expenses.filter(description__icontains=search)
	if category:
		expenses = expenses.filter(category=category)
	if date_filter:
		expenses = expenses.filter(expense_date=date_filter)
	return render(
		request,
		'tracker/expense_list.html',
		{
			'expenses': expenses,
			'search': search,
			'selected_category': category,
			'selected_date': date_filter,
			'categories': [choice[0] for choice in Expense.CATEGORY_CHOICES],
		},
	)


@login_required
def expense_add(request):
	form = ExpenseForm(request.POST or None, request.FILES or None)
	if request.method == 'POST' and form.is_valid():
		expense = form.save(commit=False)
		expense.user = request.user
		if not expense.category or expense.category == 'Others':
			expense.category = category_suggestion(expense.description)
		expense.save()
		messages.success(request, 'Expense added successfully.')
		return redirect('expense_list')
	return render(request, 'tracker/expense_form.html', {'form': form, 'mode': 'Add'})


@login_required
def expense_edit(request, pk):
	expense = get_object_or_404(Expense, pk=pk, user=request.user)
	form = ExpenseForm(request.POST or None, request.FILES or None, instance=expense)
	if request.method == 'POST' and form.is_valid():
		expense = form.save(commit=False)
		if not expense.category or expense.category == 'Others':
			expense.category = category_suggestion(expense.description)
		expense.save()
		messages.success(request, 'Expense updated successfully.')
		return redirect('expense_list')
	return render(request, 'tracker/expense_form.html', {'form': form, 'mode': 'Edit'})


@login_required
def expense_delete(request, pk):
	expense = get_object_or_404(Expense, pk=pk, user=request.user)
	if request.method == 'POST':
		expense.delete()
		messages.success(request, 'Expense deleted successfully.')
	return redirect('expense_list')


@login_required
def budget_page(request):
	current_month = timezone.localdate().replace(day=1)
	budget = Budget.objects.filter(user=request.user, month=current_month).first()
	form = BudgetForm(request.POST or None, instance=budget)
	if request.method == 'POST' and form.is_valid():
		budget_obj = form.save(commit=False)
		budget_obj.user = request.user
		budget_obj.month = current_month
		budget_obj.save()
		messages.success(request, 'Budget saved successfully.')
		return redirect('budget')
	snapshot = build_budget_snapshot(request.user)
	return render(request, 'tracker/budget.html', {'form': form, 'snapshot': snapshot, 'month_name': current_month.strftime('%B %Y')})


@login_required
def reports_page(request):
	current_year = timezone.localdate().year
	annual_income = Income.objects.filter(user=request.user, income_date__year=current_year).aggregate(total=Sum('amount'))['total'] or Decimal('0')
	annual_expense = Expense.objects.filter(user=request.user, expense_date__year=current_year).aggregate(total=Sum('amount'))['total'] or Decimal('0')
	context = {
		'year': current_year,
		'income_total': annual_income,
		'expense_total': annual_expense,
		'savings_total': annual_income - annual_expense,
		'chart_payload': {
			'monthly': monthly_series(request.user),
			'categories': category_breakdown(request.user, year=current_year),
		},
		'insights': dashboard_summary(request.user)['insights'],
	}
	return render(request, 'tracker/reports.html', context)


@login_required
def profile_page(request):
	profile = request.user.profile
	profile_form = ProfileUpdateForm(
		request.POST or None,
		request.FILES or None,
		instance=profile,
		user=request.user,
		prefix='profile',
	)
	password_form = PasswordChangeForm(request.user, request.POST or None, prefix='password')
	if request.method == 'POST':
		action = request.POST.get('action')
		if action == 'profile' and profile_form.is_valid():
			profile_form.save()
			messages.success(request, 'Profile updated successfully.')
			return redirect('profile')
		if action == 'password' and password_form.is_valid():
			user = password_form.save()
			update_session_auth_hash(request, user)
			messages.success(request, 'Password changed successfully.')
			return redirect('profile')
	return render(request, 'tracker/profile.html', {'profile_form': profile_form, 'password_form': password_form, 'profile': profile})


@login_required
def download_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="smart_expense_tracker_report.csv"'
	writer = csv.writer(response)
	writer.writerow(['Type', 'Title/Source', 'Amount', 'Category', 'Date', 'Description'])
	for income in Income.objects.filter(user=request.user):
		writer.writerow(['Income', income.source, income.amount, '', income.income_date, income.description])
	for expense in Expense.objects.filter(user=request.user):
		writer.writerow(['Expense', expense.category, expense.amount, expense.category, expense.expense_date, expense.description])
	return response


@login_required
def download_pdf(request):
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="smart_expense_tracker_report.pdf"'
	doc = SimpleDocTemplate(response, pagesize=A4)
	styles = getSampleStyleSheet()
	story = [Paragraph('Smart Expense Tracker Report', styles['Title']), Spacer(1, 12)]

	income_total = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
	expense_total = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
	story.append(Paragraph(f'Total Income: {income_total}', styles['BodyText']))
	story.append(Paragraph(f'Total Expense: {expense_total}', styles['BodyText']))
	story.append(Spacer(1, 12))

	data = [['Type', 'Item', 'Amount', 'Date']]
	for income in Income.objects.filter(user=request.user):
		data.append(['Income', income.source, str(income.amount), str(income.income_date)])
	for expense in Expense.objects.filter(user=request.user):
		data.append(['Expense', expense.category, str(expense.amount), str(expense.expense_date)])

	table = Table(data, repeatRows=1)
	table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1d3557')),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
		('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('LEADING', (0, 0), (-1, -1), 12),
	]))
	story.append(table)
	doc.build(story)
	return response


@user_passes_test(lambda user: user.is_superuser)
def admin_panel(request):
	users = User.objects.all().order_by('-date_joined')
	expenses = Expense.objects.select_related('user').order_by('-created_at')[:50]
	incomes = Income.objects.select_related('user').order_by('-created_at')[:50]
	budgets = Budget.objects.select_related('user').order_by('-updated_at')[:50]
	context = {
		'user_count': users.count(),
		'income_count': incomes.count(),
		'expense_count': expenses.count(),
		'budget_count': budgets.count(),
		'users': users,
		'expenses': expenses,
		'incomes': incomes,
		'budgets': budgets,
	}
	return render(request, 'tracker/admin_panel.html', context)


@user_passes_test(lambda user: user.is_superuser)
def admin_delete_record(request, model_name, pk):
	model_map = {
		'income': Income,
		'expense': Expense,
		'budget': Budget,
		'user': User,
	}
	model = model_map.get(model_name)
	if model and request.method == 'POST':
		obj = get_object_or_404(model, pk=pk)
		obj.delete()
		messages.success(request, f'{model_name.title()} record deleted successfully.')
	return redirect('admin_panel')
