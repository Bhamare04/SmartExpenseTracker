import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Case, FloatField, Sum, Value, When
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


def _filtered_transactions(request, user):
    transactions = user.transaction_set.select_related('category').order_by('-date', '-id')

    transaction_type = (request.GET.get('type') or '').strip()
    category_id = (request.GET.get('category') or '').strip()
    date_from = (request.GET.get('from') or '').strip()
    date_to = (request.GET.get('to') or '').strip()
    query = (request.GET.get('q') or '').strip()

    if transaction_type in {'income', 'expense'}:
        transactions = transactions.filter(transaction_type=transaction_type)

    if category_id.isdigit():
        transactions = transactions.filter(category_id=int(category_id))

    if date_from:
        transactions = transactions.filter(date__gte=date_from)

    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    if query:
        transactions = transactions.filter(description__icontains=query)

    return transactions, {
        'type': transaction_type,
        'category': category_id,
        'from': date_from,
        'to': date_to,
        'q': query,
    }


def _summary_from_transactions(transactions):
    summary = transactions.aggregate(
        income_total=Coalesce(
            Sum(
                Case(
                    When(transaction_type='income', then='amount'),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
            ),
            0.0,
        ),
        expense_total=Coalesce(
            Sum(
                Case(
                    When(transaction_type='expense', then='amount'),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
            ),
            0.0,
        ),
    )
    summary['balance'] = summary['income_total'] - summary['expense_total']
    return summary

def home(request):
    context = {}

    if request.user.is_authenticated:
        transactions, filters = _filtered_transactions(request, request.user)
        summary = _summary_from_transactions(transactions)

        month_start = date.today().replace(day=1)
        month_transactions = request.user.transaction_set.filter(date__gte=month_start)
        month_summary = _summary_from_transactions(month_transactions)

        context = {
            'transactions': transactions[:20],
            'summary': summary,
            'month_summary': month_summary,
            'categories': request.user.transaction_set.values_list(
                'category__id', 'category__name'
            ).distinct().order_by('category__name'),
            'filters': filters,
            'has_filters': any(filters.values()),
        }

    return render(request, "tracker/home.html", context)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Welcome!')
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "tracker/register.html", {"form": form})

from .forms import RegisterForm, TransactionForm
from .models import Transaction


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction saved successfully.')
            return redirect('home')
    else:
        form = TransactionForm()

    return render(request, 'tracker/add_transaction.html', {'form': form, 'is_edit': False})


@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully.')
            return redirect('home')
    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'tracker/add_transaction.html', {'form': form, 'is_edit': True})


@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully.')
        return redirect('home')

    return render(request, 'tracker/delete_transaction.html', {'transaction': transaction})


@login_required
def export_transactions_csv(request):
    transactions, _ = _filtered_transactions(request, request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Type', 'Amount', 'Description'])
    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.category.name,
            transaction.transaction_type,
            f'{transaction.amount:.2f}',
            transaction.description,
        ])

    return response