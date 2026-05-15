from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import Budget, Expense, Income


class Command(BaseCommand):
    help = 'Seed demo data for the Smart Expense Tracker application.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='demo', help='Username for the demo account.')
        parser.add_argument('--password', default='Demo@12345', help='Password for the demo account.')
        parser.add_argument('--email', default='demo@example.com', help='Email for the demo account.')

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=options['username'],
            defaults={
                'email': options['email'],
            },
        )
        if created:
            user.set_password(options['password'])
            user.save()
            user.profile.full_name = 'Demo User'
            user.profile.mobile_number = '9999999999'
            user.profile.save()

        current_month = timezone.localdate().replace(day=1)
        Budget.objects.update_or_create(
            user=user,
            month=current_month,
            defaults={'amount': Decimal('50000.00'), 'note': 'Demo monthly budget'},
        )

        if not Income.objects.filter(user=user).exists():
            Income.objects.bulk_create([
                Income(user=user, amount=Decimal('40000.00'), source='Salary', income_date=timezone.localdate(), description='Monthly salary'),
                Income(user=user, amount=Decimal('5000.00'), source='Freelance', income_date=timezone.localdate(), description='Project payment'),
            ])

        if not Expense.objects.filter(user=user).exists():
            Expense.objects.bulk_create([
                Expense(user=user, amount=Decimal('4500.00'), category='Food', payment_method='UPI', expense_date=timezone.localdate(), description='Lunch, dinner, groceries'),
                Expense(user=user, amount=Decimal('2500.00'), category='Travel', payment_method='Card', expense_date=timezone.localdate(), description='Metro and taxi rides'),
                Expense(user=user, amount=Decimal('3200.00'), category='Bills', payment_method='Bank Transfer', expense_date=timezone.localdate(), description='Internet and electricity bill'),
            ])

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
