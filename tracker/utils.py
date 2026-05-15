from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import Budget, Expense, Income


def month_start(value: date | None = None) -> date:
    value = value or timezone.localdate()
    return value.replace(day=1)


def add_months(base: date, months: int) -> date:
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, monthrange(year, month)[1])
    return date(year, month, day)


def month_label(value: date) -> str:
    return value.strftime('%b %Y')


def category_suggestion(description: str) -> str:
    text = (description or '').lower()
    keyword_map = {
        'Food': ('food', 'lunch', 'dinner', 'breakfast', 'restaurant', 'coffee', 'meal', 'snack'),
        'Travel': ('travel', 'taxi', 'cab', 'bus', 'train', 'metro', 'flight', 'fuel'),
        'Shopping': ('shopping', 'shirt', 'dress', 'bag', 'online', 'amazon', 'mall', 'purchase'),
        'Bills': ('bill', 'electricity', 'water', 'internet', 'phone', 'rent', 'subscription'),
        'Entertainment': ('movie', 'game', 'netflix', 'music', 'concert', 'party'),
        'Health': ('doctor', 'medicine', 'hospital', 'pharmacy', 'health', 'clinic'),
        'Education': ('course', 'college', 'school', 'book', 'tuition', 'exam'),
    }
    for category, keywords in keyword_map.items():
        if any(keyword in text for keyword in keywords):
            return category
    return 'Others'


def build_budget_snapshot(user):
    current_month = month_start()
    budget = Budget.objects.filter(user=user, month=current_month).first()
    spent = Expense.objects.filter(user=user, expense_date__year=current_month.year, expense_date__month=current_month.month).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    progress = (spent / budget.amount * 100) if budget and budget.amount else Decimal('0')
    return {
        'budget': budget,
        'spent': spent,
        'progress': min(progress, Decimal('100')),
        'warning': bool(budget and progress >= Decimal('80')),
        'exceeded': bool(budget and spent > budget.amount),
    }


def monthly_series(user, months: int = 6):
    today = timezone.localdate().replace(day=1)
    labels = []
    income_values = []
    expense_values = []
    savings_values = []

    for offset in range(months - 1, -1, -1):
        month_anchor = add_months(today, -offset)
        labels.append(month_label(month_anchor))

        income_total = Income.objects.filter(user=user, income_date__year=month_anchor.year, income_date__month=month_anchor.month).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        expense_total = Expense.objects.filter(user=user, expense_date__year=month_anchor.year, expense_date__month=month_anchor.month).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        income_values.append(float(income_total))
        expense_values.append(float(expense_total))
        savings_values.append(float(income_total - expense_total))

    return {
        'labels': labels,
        'income': income_values,
        'expense': expense_values,
        'savings': savings_values,
    }


def category_breakdown(user, year: int | None = None, month: int | None = None):
    queryset = Expense.objects.filter(user=user)
    if year:
        queryset = queryset.filter(expense_date__year=year)
    if month:
        queryset = queryset.filter(expense_date__month=month)

    categories = defaultdict(Decimal)
    for row in queryset.values('category').annotate(total=Sum('amount')):
        categories[row['category']] = row['total'] or Decimal('0')

    labels = list(categories.keys())
    values = [float(categories[label]) for label in labels]
    return {'labels': labels, 'values': values}


def dashboard_summary(user):
    income_total = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    expense_total = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    remaining = income_total - expense_total
    savings = remaining if remaining > 0 else Decimal('0')
    expense_percentage = float((expense_total / income_total * 100) if income_total else Decimal('0'))
    recent_transactions = list(
        Income.objects.filter(user=user).order_by('-created_at')[:3]
    ) + list(
        Expense.objects.filter(user=user).order_by('-created_at')[:5]
    )
    recent_transactions = sorted(recent_transactions, key=lambda item: item.created_at, reverse=True)[:8]

    budget = build_budget_snapshot(user)
    monthly = monthly_series(user)
    insights = smart_insights(user, income_total, expense_total)
    top_category = category_breakdown(user, month=timezone.localdate().month, year=timezone.localdate().year)

    return {
        'income_total': income_total,
        'expense_total': expense_total,
        'remaining_balance': remaining,
        'monthly_savings': savings,
        'expense_percentage': expense_percentage,
        'recent_transactions': recent_transactions,
        'budget_snapshot': budget,
        'monthly_series': monthly,
        'category_breakdown': top_category,
        'insights': insights,
    }


def smart_insights(user, income_total: Decimal, expense_total: Decimal) -> list[str]:
    current_month = timezone.localdate()
    current_expenses = Expense.objects.filter(user=user, expense_date__year=current_month.year, expense_date__month=current_month.month)
    last_month_date = add_months(current_month.replace(day=1), -1)
    last_month_expenses = Expense.objects.filter(user=user, expense_date__year=last_month_date.year, expense_date__month=last_month_date.month)

    insights = []
    category_totals = current_expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    top_category = category_totals.first()
    if top_category:
        insights.append(f"You spent most on {top_category['category']} this month.")

    if last_month_expenses.exists():
        this_month_total = current_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        last_month_total = last_month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        if last_month_total > 0:
            change = ((this_month_total - last_month_total) / last_month_total) * 100
            if change >= 0:
                insights.append(f'Your expenses increased by {abs(change):.0f}% compared to last month.')
            else:
                insights.append(f'Your expenses decreased by {abs(change):.0f}% compared to last month.')

    shopping_total = current_expenses.filter(category='Shopping').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    if shopping_total > 0:
        insights.append('You can save more by reducing Shopping expenses.')

    if not insights:
        insights.append('Add a few transactions to unlock meaningful spending insights.')
    return insights
