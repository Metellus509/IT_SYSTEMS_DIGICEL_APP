from django.urls import path
from . import views

urlpatterns = [
    # Device CRUD
    path('', views.device_list, name='device_list'),
    path('create/', views.device_create, name='device_create'),
    path('search/', views.search_devices, name='search_devices'),
    path('stats/', views.device_stats, name='device_stats'),
    path('types/', views.device_types, name='device_types'),
    path('statuses/', views.device_statuses, name='device_statuses'),
    path('<int:device_id>/', views.device_detail, name='device_detail'),
    path('<int:device_id>/update/', views.device_update, name='device_update'),
    path('<int:device_id>/delete/', views.device_delete, name='device_delete'),
    
    # Device Accounts
    path('<int:device_id>/accounts/add/', views.device_add_account, name='device_add_account'),
    path('accounts/my-accounts/', views.my_accounts, name='my_accounts'),
    path('accounts/all-accounts/', views.all_accounts, name='all_accounts'),
    path('accounts/<int:account_id>/', views.update_account, name='update_account'),
    path('accounts/<int:account_id>/delete/', views.delete_account, name='delete_account'),
    path('accounts/<int:account_id>/reveal-password/', views.reveal_account_password, name='reveal_account_password'),

    path('reveal-passwords/', views.reveal_passwords, name='reveal_passwords'),
    path('reveal-passwords/<int:device_id>/', views.reveal_passwords, name='reveal_passwords_device'),
    path('accounts/reveal-passwords/', views.reveal_my_accounts_passwords, name='reveal_my_accounts_passwords'),

]