from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   # ✅ HOME PAGE
    path('register/', views.register, name='register'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('export/csv/', views.export_transactions_csv, name='export_transactions_csv'),
    path('dashboard/', views.home, name='dashboard')
]