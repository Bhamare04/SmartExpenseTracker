from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Transaction


class TrackerFlowTests(TestCase):
	def setUp(self):
		self.client.post(
			reverse('register'),
			{
				'username': 'newuser',
				'email': 'newuser@example.com',
				'password1': 'StrongPass123!',
				'password2': 'StrongPass123!',
			},
			follow=True,
		)
		self.salary = Category.objects.create(name='Salary')
		self.food = Category.objects.create(name='Food')
		self.user = User.objects.get(username='newuser')

	def test_home_page_loads(self):
		response = self.client.get(reverse('home'))
		self.assertEqual(response.status_code, 200)

	def test_add_transaction_requires_login(self):
		self.client.logout()
		response = self.client.get(reverse('add_transaction'))
		self.assertEqual(response.status_code, 302)
		self.assertIn('/login/', response.url)

	def test_register_and_add_transaction(self):
		add_response = self.client.post(
			reverse('add_transaction'),
			{
				'amount': '1200.50',
				'category': self.salary.id,
				'transaction_type': 'income',
				'date': '2026-04-01',
				'description': 'Monthly salary',
			},
			follow=True,
		)
		self.assertEqual(add_response.status_code, 200)
		self.assertTrue(Transaction.objects.filter(user__username='newuser').exists())

	def test_add_transaction_with_new_category(self):
		add_response = self.client.post(
			reverse('add_transaction'),
			{
				'amount': '65.00',
				'category': '',
				'new_category': 'Snacks',
				'transaction_type': 'expense',
				'date': '2026-04-05',
				'description': 'Coffee and sandwich',
			},
			follow=True,
		)
		self.assertEqual(add_response.status_code, 200)
		self.assertTrue(Category.objects.filter(name='Snacks').exists())

	def test_amount_must_be_positive(self):
		response = self.client.post(
			reverse('add_transaction'),
			{
				'amount': '0',
				'category': self.food.id,
				'transaction_type': 'expense',
				'date': '2026-04-07',
				'description': 'Invalid amount',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Amount must be greater than zero.')

	def test_filter_transactions_on_dashboard(self):
		Transaction.objects.create(
			user=self.user,
			amount=2000,
			category=self.salary,
			transaction_type='income',
			date='2026-04-01',
			description='Salary April',
		)
		Transaction.objects.create(
			user=self.user,
			amount=100,
			category=self.food,
			transaction_type='expense',
			date='2026-04-03',
			description='Groceries',
		)

		response = self.client.get(reverse('home'), {'type': 'expense', 'q': 'Groc'})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Groceries')
		self.assertNotContains(response, 'Salary April')

	def test_edit_and_delete_transaction(self):
		transaction = Transaction.objects.create(
			user=self.user,
			amount=100,
			category=self.food,
			transaction_type='expense',
			date='2026-04-03',
			description='Initial',
		)

		edit_response = self.client.post(
			reverse('edit_transaction', args=[transaction.id]),
			{
				'amount': '140',
				'category': self.food.id,
				'new_category': '',
				'transaction_type': 'expense',
				'date': '2026-04-04',
				'description': 'Updated',
			},
			follow=True,
		)
		self.assertEqual(edit_response.status_code, 200)
		transaction.refresh_from_db()
		self.assertEqual(float(transaction.amount), 140.0)

		delete_response = self.client.post(
			reverse('delete_transaction', args=[transaction.id]),
			follow=True,
		)
		self.assertEqual(delete_response.status_code, 200)
		self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())

	def test_export_csv(self):
		Transaction.objects.create(
			user=self.user,
			amount=100,
			category=self.food,
			transaction_type='expense',
			date='2026-04-03',
			description='Groceries',
		)

		response = self.client.get(reverse('export_transactions_csv'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'text/csv')
		self.assertIn('Groceries', response.content.decode('utf-8'))
